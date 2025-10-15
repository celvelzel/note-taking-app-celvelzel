import os
import sys
from pathlib import Path

# 将项目 src 和 根目录加入 Python 路径，便于导入本地包
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

from flask import Flask, send_from_directory
from flask_cors import CORS

# 尝试导入数据库和蓝图，若失败则回退到临时 SQLAlchemy 实例（便于本地测试或缺少模块时启动）
try:
    from src.models.user import db
    from src.routes.user import user_bp
    from src.routes.note import note_bp
    from src.models.note import Note  # 若需要，可触发模型导入以便 create_all 创建表
    _have_models = True
except ImportError as e:
    print(f"Import error: {e}")
    # 回退：创建临时 SQLAlchemy 实例（功能受限，但可避免导入失败导致整个应用崩溃）
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    user_bp = None
    note_bp = None
    _have_models = False

# 创建 Flask 应用，静态目录指向 src/static（用于部署单页应用）
app = Flask(__name__, static_folder=str(project_root / "src" / "static"))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# 启用 CORS
CORS(app)

# 数据库连接配置：优先使用环境变量 DATABASE_URL（兼容 Heroku/Postgres URL 形式）
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        # SQLAlchemy 从新版起要求 postgresql:// 前缀
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # 开发时的后备方案：SQLite 文件
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化数据库扩展（若 db 提供 init_app）
try:
    if hasattr(db, "init_app"):
        db.init_app(app)
except Exception as e:
    print(f"Database initialization error: {e}")

# 注册蓝图（只有在成功导入蓝图时才注册）
if user_bp:
    app.register_blueprint(user_bp, url_prefix="/api")
if note_bp:
    app.register_blueprint(note_bp, url_prefix="/api")

# 尝试创建数据库表（在应用上下文中），如果没有模型则跳过错误
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Warning: create_all failed or no models available: {e}")

# 静态文件与 SPA 路由处理
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    """服务静态资源并支持 SPA 前端路由"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    full_path = os.path.join(static_folder_path, path)
    if path and os.path.exists(full_path):
        return send_from_directory(static_folder_path, path)
    index_path = os.path.join(static_folder_path, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, "index.html")
    return "index.html not found", 404

# 健康检查端点
@app.route("/health")
def health_check():
    return {"status": "ok", "message": "NoteTaker API is running"}

# Vercel 要求的 WSGI 风格处理函数（environ, start_response）
# 这样可以避免 Vercel 运行时对 handler 类型检查导致的 issubclass 错误
def handler(environ, start_response):
    """
    WSGI 兼容入口，Vercel 运行时会以 (environ, start_response) 调用此函数。
    直接将处理委托给 Flask 的 wsgi_app。
    """
    return app.wsgi_app(environ, start_response)

# 保留 app 和 app_instance 以兼容其他部署方式或测试工具
app_instance = app

if __name__ == "__main__":
    # 本地开发启动（仅在直运行此文件时生效）
    app.run(debug=True, host="0.0.0.0", port=5001)