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

# ---------- 应用与扩展初始化 ----------
# 创建 Flask 应用，static 指向 src/static（用于部署 SPA 前端）
app = Flask(__name__, static_folder=str(project_root / "src" / "static"))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# 启用跨域（简单开启，生产需按需配置）
CORS(app)

# 尝试导入项目内的 db 与 蓝图；导入失败时回退到临时 SQLAlchemy（避免导入错误导致整个函数报错）
try:
    from src.models.user import db
    from src.routes.user import user_bp
    from src.routes.note import note_bp
    # 触发模型定义（可选）
    from src.models.note import Note
    _have_models = True
except Exception as e:
    # 导入失败时打印错误并建立临时 db 实例以允许最小化启动
    print(f"Import warning (models/blueprints): {e}")
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    user_bp = None
    note_bp = None
    _have_models = False

# ---------- 配置数据库连接 ----------
database_url = os.getenv("DATABASE_URL")
if database_url:
    # 兼容老的 postgres:// -> postgresql:// 前缀，以便 SQLAlchemy 正确识别
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # 本地开发备用 sqlite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化 db（如果 db 提供 init_app）
try:
    if hasattr(db, "init_app"):
        db.init_app(app)
except Exception as e:
    print(f"Database initialization error: {e}")

# ---------- 注册蓝图（如果有的话） ----------
if user_bp:
    app.register_blueprint(user_bp, url_prefix="/api")
if note_bp:
    app.register_blueprint(note_bp, url_prefix="/api")

# 在应用上下文中尝试创建表（如果模型可用）
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Warning: create_all failed or no models available: {e}")

# ---------- 路由：静态文件与 SPA 支持 ----------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    """服务静态资源并支持前端 SPA 路由"""
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

# 健康检查端点（便于 Vercel 或外部探针检查服务状态）
@app.route("/health")
def health_check():
    return {"status": "ok", "message": "NoteTaker API is running"}

# ---------- 导出入口（兼容 Vercel） ----------
# 1) 明确提供 WSGI callable，供需要 (environ, start_response) 签名的平台使用
def wsgi_handler(environ, start_response):
    """
    明确的 WSGI 入口函数，签名为 (environ, start_response)。
    在某些环境下（或测试）可能直接被调用。
    """
    return app.wsgi_app(environ, start_response)

# 2) 提供 Flask 实例变量 app（多数 WSGI 平台会识别这一约定）
# 3) 同时提供 handler 变量（设置为 Flask 实例），避免某些运行时代码在检测类型时抛出 issubclass TypeError
#    将 handler 直接设置为 Flask 实例可以保证 type(handler) 是类（Flask），从而避免 issubclass() 的类型错误。
handler = app      # Vercel 在某些实现中会读取 handler；将其设为 Flask 实例以兼容检测逻辑
app_instance = app # 保留备用命名以兼容不同部署/测试场景
# 同时保留明确的 WSGI callable，视需要可更改 handler = wsgi_handler

# ---------- 本地调试入口 ----------
if __name__ == "__main__":
    # 仅在本地直接运行时启用调试服务器
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))