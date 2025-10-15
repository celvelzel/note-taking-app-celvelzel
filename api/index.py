"""Vercel adapter (minimal).

这个文件仅导出 Flask `app` 实例和一个明确的 WSGI callable
`wsgi_handler`。请不要在此导出任何继承自
`http.server.BaseHTTPRequestHandler` 的类或名为 `handler` 的变量，
因为某些 Vercel 运行时会对导出的对象做 `issubclass`/实例化等检查，
这可能触发 501/TypeError 等不期望的运行时行为。

中文注释：本文件保持精简 — 应用逻辑在 `src/main.py`。
"""

import sys
import os
import traceback

# 把项目根目录加入 sys.path，确保可以 import src.main
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    # 从 src.main 导入 Flask app（主应用入口）
    from src.main import app  # type: ignore
except Exception:
    print("ERROR importing src.main.app:")
    traceback.print_exc()
    # 让导入错误能够在 Vercel 日志中清晰可见
    raise
else:
    print("Imported Flask app from src.main successfully.")


def wsgi_handler(environ, start_response):
    """明确的 WSGI 入口（签名：environ, start_response）。

    Vercel 和许多平台都能识别 WSGI callable。此函数仅将调用
    转发给 Flask 的 `app.wsgi_app`，并在 Vercel 日志打印简短的请求信息。
    """
    try:
        method = environ.get("REQUEST_METHOD", "")
        path = environ.get("PATH_INFO", "")
        print(f"wsgi_handler called: {method} {path}")
    except Exception:
        # 打印失败不可影响请求处理
        pass
    return app.wsgi_app(environ, start_response)


# 仅导出这两个名字，避免导出会被运行时特殊对待的符号
__all__ = ["app", "wsgi_handler"]