"""Vercel function entry point.

This file exposes multiple entry points to maximize compatibility with different
Vercel Python runtime detection strategies:

- `app`: the Flask application instance imported from `src.main` (WSGI app)
- `wsgi_handler(environ, start_response)`: explicit WSGI callable that delegates to `app.wsgi_app`
- `handler`: a class placeholder inheriting from BaseHTTPRequestHandler so that
  runtimes that perform `issubclass(handler, BaseHTTPRequestHandler)` checks
  won't raise TypeError. This class also proxies requests to the WSGI app when
  instantiated by a server.

Keep this file minimal: actual app logic lives in `src/main.py`.
"""

import io
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit, unquote

# Ensure project root is on sys.path so `src` package imports work
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    # Import the Flask app from src.main
    from src.main import app  # type: ignore
except Exception as e:
    # Provide a clear import-time error for Vercel logs
    raise RuntimeError(f"Failed to import Flask app from src.main: {e}")


def wsgi_handler(environ, start_response):
    """Explicit WSGI callable that delegates to the Flask WSGI app.

    Some runtimes call a function with the WSGI signature directly. Expose
    this to be explicit and simple.
    """
    return app.wsgi_app(environ, start_response)


class handler(BaseHTTPRequestHandler):
    """A lightweight handler class that proxies requests to the Flask WSGI app.

    This class exists primarily to satisfy runtimes that expect `handler` to
    be a class and may perform `issubclass` checks. When instantiated by an
    HTTP server, it will forward the request to the WSGI app and write the
    response back.
    """

    def _build_environ(self):
        parsed = urlsplit(self.path)
        content_length = int(self.headers.get('Content-Length', 0) or 0)
        body = self.rfile.read(content_length) if content_length else b''

        environ = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if self.server.server_port == 443 else 'http',
            'wsgi.input': io.BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.command,
            'PATH_INFO': unquote(parsed.path),
            'QUERY_STRING': parsed.query or '',
            'SERVER_NAME': self.server.server_name or '',
            'SERVER_PORT': str(self.server.server_port),
            'SERVER_PROTOCOL': self.request_version,
        }

        for k, v in self.headers.items():
            environ['HTTP_' + k.upper().replace('-', '_')] = v

        if 'Content-Type' in self.headers:
            environ['CONTENT_TYPE'] = self.headers.get('Content-Type')
        if content_length:
            environ['CONTENT_LENGTH'] = str(content_length)

        return environ

    def _start_response(self, status, response_headers, exc_info=None):
        self._status = status
        self._response_headers = response_headers
        return None

    def _proxy(self):
        # Debug log for Vercel logs (helps identify which handler served the request)
        try:
            print(f"handler proxying: method={self.command} path={self.path} client={self.client_address}")
        except Exception:
            pass

        environ = self._build_environ()
        result = app.wsgi_app(environ, self._start_response)

        status_code = int(getattr(self, '_status', '200').split()[0])
        self.send_response(status_code)
        for name, value in getattr(self, '_response_headers', []):
            self.send_header(name, value)
        self.end_headers()

        for data in result:
            if isinstance(data, str):
                data = data.encode()
            if data:
                self.wfile.write(data)

        if hasattr(result, 'close'):
            result.close()

    # Implement common methods so BaseHTTPRequestHandler doesn't return 501
    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_HEAD(self):
        self._proxy()

    def do_OPTIONS(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()


# Exports expected by different runtimes
# - app: Flask instance
# - wsgi_handler: explicit WSGI callable
# - handler: class for runtime checks (and can be used by simple HTTP servers)

__all__ = ['app', 'wsgi_handler', 'handler']
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
from http.server import BaseHTTPRequestHandler

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
# 3) 提供兼容 Vercel 的导出：
# - wsgi_handler: 明确的 WSGI callable（environ, start_response），供运行时直接使用
# - app / app_instance: Flask 实例，供其它平台或测试工具识别
# - handler: 为避免 Vercel 在类型检测时对非类对象调用 issubclass 导致 TypeError，
#            我们导出一个占位类，该类继承自 BaseHTTPRequestHandler（仅用于通过类型检查）。

# 占位类：用于通过 Vercel 的类型检测（issubclass 检查）。
class VercelRequestHandler(BaseHTTPRequestHandler):
    """
    仅作为类型占位符导出，继承自 BaseHTTPRequestHandler 以满足运行时的 issubclass 检查。
    真正的请求处理仍由 Flask 的 wsgi_app / wsgi_handler 负责。
    """
    pass

# 导出变量：
handler = VercelRequestHandler
app_instance = app  # 备用命名以兼容不同部署/测试场景

# ---------- 本地调试入口 ----------
if __name__ == "__main__":
    # 仅在本地直接运行时启用调试服务器
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))