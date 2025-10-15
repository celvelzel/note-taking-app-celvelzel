import os
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

from flask import Flask, send_from_directory, request
from flask_cors import CORS

# 数据库和模型导入
try:
    from src.models.user import db
    from src.routes.user import user_bp
    from src.routes.note import note_bp
    from src.models.note import Note
except ImportError as e:
    print(f"Import error: {e}")
    # 使用临时数据库配置
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()

# 创建Flask应用
app = Flask(__name__, static_folder=str(project_root / "src" / "static"))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# 启用CORS
CORS(app)

# 数据库配置 - 使用环境变量
database_url = os.getenv('DATABASE_URL')
if database_url:
    # 云数据库
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # 开发环境后备方案 - 使用SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
try:
    db.init_app(app)
    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(note_bp, url_prefix='/api')
except Exception as e:
    print(f"Database initialization error: {e}")

# 为Vercel创建数据库表
# 应用启动时直接初始化数据库
with app.app_context():
    # 初始化数据库表结构（如未创建则自动创建）
    db.create_all()

# 静态文件路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """服务静态文件和SPA路由"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# 健康检查路由
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'NoteTaker API is running'}

# Vercel要求的处理函数
def handler(request):
    return app(request.environ, lambda *args: None)

# 对于Vercel部署
app_instance = app

if __name__ == '__main__':
    # 本地开发
    app.run(debug=True, host='0.0.0.0', port=5001)