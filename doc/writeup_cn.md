# Vercel 部署步骤，问题总结与解决方案回顾

本文档详细记录了将 Flask 笔记应用部署到 Vercel 平台的操作步骤和部署时遇到的主要问题及解决方案，供后续参考。

---

## 目录
- [Vercel 部署步骤，问题总结与解决方案回顾](#vercel-部署步骤问题总结与解决方案回顾)
  - [目录](#目录)
  - [1. 添加新功能和重构app步骤](#1-添加新功能和重构app步骤)
    - [1. 分析项目结构和现有代码](#1-分析项目结构和现有代码)
    - [2. 修改前端界面](#2-修改前端界面)
    - [3. 实现前端交互逻辑](#3-实现前端交互逻辑)
    - [4. 创建后端API接口](#4-创建后端api接口)
    - [5. 集成GitHub大语言模型API](#5-集成github大语言模型api)
    - [6. 更新依赖和配置](#6-更新依赖和配置)
    - [7. 添加信息持久化存储功能](#7-添加信息持久化存储功能)
    - [8. 前端页面优化](#8-前端页面优化)
    - [9. Vercel云部署准备](#9-vercel云部署准备)
  - [2. 配置supabase和vercel](#2-配置supabase和vercel)
    - [1. 创建vercel项目](#1-创建vercel项目)
    - [2. 在supabase创建新项目，保存连接字符串](#2-在supabase创建新项目保存连接字符串)
  - [3. 经验总结与最佳实践](#3-经验总结与最佳实践)
    - [核心经验](#核心经验)
    - [常见错误快速诊断表](#常见错误快速诊断表)
    - [部署检查清单](#部署检查清单)
- [部署时遇到的问题](#部署时遇到的问题)
  - [1. Vercel 配置文件问题](#1-vercel-配置文件问题)
    - [问题描述](#问题描述)
    - [根本原因](#根本原因)
    - [解决方案](#解决方案)
  - [2. Vercel 环境变量的 Secret 引用](#2-vercel-环境变量的-secret-引用)
    - [问题描述](#问题描述-1)
    - [根本原因](#根本原因-1)
    - [解决方案](#解决方案-1)
  - [3. Python 版本和依赖问题](#3-python-版本和依赖问题)
    - [问题描述](#问题描述-2)
    - [根本原因](#根本原因-2)
    - [解决方案](#解决方案-2)
  - [4. Flask `@before_first_request` 装饰器废弃](#4-flask-before_first_request-装饰器废弃)
    - [问题描述](#问题描述-3)
    - [根本原因](#根本原因-3)
    - [解决方案](#解决方案-3)
  - [5. 数据库从本地 SQLite 切换到远程 PostgreSQL](#5-数据库从本地-sqlite-切换到远程-postgresql)
    - [问题描述](#问题描述-4)
    - [根本原因](#根本原因-4)
    - [解决方案](#解决方案-4)
  - [6. `api/index.py` 入口文件的演进](#6-apiindexpy-入口文件的演进)
    - [问题描述](#问题描述-5)
    - [根本原因分析](#根本原因分析)
    - [解决方案演进过程](#解决方案演进过程)
      - [阶段 1：初始尝试（失败）](#阶段-1初始尝试失败)
      - [阶段 2：实现代理类（部分成功）](#阶段-2实现代理类部分成功)
      - [阶段 3：最终方案（成功）](#阶段-3最终方案成功)
    - [关键要点总结](#关键要点总结)

---
## 1. 添加新功能和重构app步骤
### 1. 分析项目结构和现有代码
- 分析主要文件：main.py、models/note.py、routes/note.py、static/index.html
- 了解了Flask应用架构、SQLAlchemy数据模型和前端界面结构
- 确认了现有的API端点和前端功能

### 2. 修改前端界面
- 在编辑器操作区域添加了"提取信息"按钮,添加了按钮的hover效果和禁用状态样式
- 新增右侧 AI 辅助面板：翻译目标语言下拉框、翻译按钮、并排展示原文与译文。
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)

### 3. 实现前端交互逻辑
- 添加了js方法处理按钮点击事件
- 实现了API调用和加载状态管理
- 创建了模态窗口来展示提取的信息
- 添加了完整的错误处理和用户反馈

### 4. 创建后端API接口
- 在`src/routes/note.py`中添加了新的API端点`/api/notes/extract-info`，`/api/notes/translate` 与 `/api/notes/generate-quiz`
- 接口支持可选的 `note_id` 参数，成功时写入数据库并返回结构化数据，失败时提供清晰的错误信息。
- 实现了POST方法来处理信息提取请求
- 添加了错误处理和输入验证

### 5. 集成GitHub大语言模型API
- 创建了`src/services/`目录和AI服务模块
- 实现了`GitHubAIService`类来调用GitHub Models API
- 配置了专业的提示词来提取文档关键信息
- 实现了完整的错误处理和超时控制
- 新增 `translate_content()` 与 `generate_quiz()` 方法。
- 引入中文提示词，约束返回格式，并对 JSON 结果做容错解析。
- 暴露 `translate_note_content()`、`generate_quiz_question()` 便于路由调用。

### 6. 更新依赖和配置
- 在`requirements.txt`中添加了`requests==2.31.0`依赖
- 创建了`.env.example`文件提供环境变量配置示例
- 更新了README.md包含新功能说明和配置指南

### 7. 添加信息持久化存储功能
- 在Note数据模型中添加了`extracted_info`和`extracted_at`字段以及翻译、题目与解析等字段，统一采用 JSON 文本和时间戳记录历史。
- `Note.to_dict()` 对输出进行 JSON 反序列化，保证前端拿到的结构化数据可直接使用。
- 更新了数据库结构来存储AI提取的信息
- 修改了API端点来保存提取的信息到数据库

### 8. 前端页面优化
- 实现了内容窗口自适应高度，支持动态布局
- 添加了笔记列表分页功能，每页显示10条笔记
- 优化了响应式设计，适配各种屏幕尺寸
- 改进了用户界面的空间利用率和交互体验

### 9. Vercel云部署准备
- 创建了vercel.json配置文件和运行时设置
- 构建了适配Serverless环境的API入口文件index.py
- 集成了云数据库支持(使用supbase上的PostgreSQL)
  
---

## 2. 配置supabase和vercel

### 1. 创建vercel项目
- 创建项目，链接github
- 在项目根目录创建vercel.json配置文件
- 在项目根目录创建api/index.py入口文件
- 在vercel项目设置中添加环境变量，包括github token以及密钥
  ![alt text](image-1.png)
- 通过github push自动部署到生产环境
- 设置vercel项目为公开，以便用户访问
  
### 2. 在supabase创建新项目，保存连接字符串
![alt text](image.png)
- 使用transaction pooler，适配vercel的serverless架构
- 在vercel项目设置中添加环境变量DATABASE_URL，值为连接字符串

## 3. 经验总结与最佳实践

### 核心经验
1. **Vercel 配置**：
   - 在 `functions` 中明确声明 serverless 函数配置
   - 需要在Vercel的项目设置中添加环境变量

2. **数据库选择**：
   - serverless 环境必须使用远程数据库
   - 通过 `DATABASE_URL` 环境变量注入连接字符串
   - 避免在只读文件系统中创建本地数据库文件

3. **入口文件设计**：
   - `api/index.py` 应当是轻量适配器，仅负责导入和导出
   - 优先导出 WSGI callable（`app` 或 `wsgi_handler`）
   - 避免导出未完整实现的 `handler` 类

4. **调试技巧**：
   - 在关键路径增加 `print()` 或日志记录
   - 使用 `traceback.print_exc()` 捕获完整错误堆栈
   - 对于可选功能的依赖，使用 try/except 优雅处理缺失情况
   - 返回清晰的错误消息（503 Service Unavailable + 配置提示）而非 500 Internal Error
   - 在 Vercel 日志中打印 traceback，便于快速定位问题

### 常见错误快速诊断表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `TypeError: issubclass() arg 1 must be a class` | 导出了非类对象作为 `handler` | 移除 `handler` 导出，只保留 `app`/`wsgi_handler` |
| `501 Unsupported method` | `handler` 类未实现 HTTP 方法 | 移除 `handler` 或实现完整的代理逻辑 |
| `OSError: Read-only file system` | 尝试写入 serverless 容器的只读目录 | 使用远程数据库，移除本地文件写入 |
| `No module named 'xxx'` | `requirements.txt` 缺少依赖 | 添加缺失的包到 `requirements.txt` |
| `DATABASE_URL not set` | 环境变量未配置 | 在 Vercel 项目设置中添加环境变量 |
| `DeprecationWarning: before_first_request` | 使用了 Flask 3.0 废弃的装饰器 | 改用 `with app.app_context()` 初始化 |
| `psycopg2.OperationalError` | PostgreSQL 连接失败 | 检查 `DATABASE_URL` 格式和数据库可访问性 |

### 部署检查清单
- [ ] `requirements.txt` 包含所有运行时依赖
- [ ] `vercel.json` 路由配置正确（静态 → API → 回退）
- [ ] 环境变量已在 Vercel 项目设置中配置（Production/Preview）
- [ ] `api/index.py` 只导出 `app` 和 `wsgi_handler`
- [ ] 数据库使用远程 PostgreSQL（通过 `DATABASE_URL`）
- [ ] 移除了 `@before_first_request` 等废弃装饰器
- [ ] 代码中无硬编码的敏感信息
- [ ] 本地 `vercel dev` 测试通过
- [ ] 部署后检查 Vercel 日志确认无错误

---

# 部署时遇到的问题

## 1. Vercel 配置文件问题

### 问题描述
初始部署时，`vercel.json` 的配置不当导致：
- 同时配置了functions和builds

### 根本原因
There are two ways to configure Vercel functions in your project: functions or builds. However, only one of them may be used at a time - they cannot be used in conjunction.

### 解决方案
使用functions进行配置，因为它支持更多功能


## 2. Vercel 环境变量的 Secret 引用

### 问题描述
环境变量 "GITHUB_TOKEN" 引用了 Secret "github_token"，但该 Secret 不存在。Vercel 支持用 @secret_name 语法在 vercel.json 里引用 Secret（密钥），这些 Secret 需要你在 Vercel CLI 或 Dashboard 里专门创建（而不是直接在 Settings → Environment Variables 里添加）。

### 根本原因
- 在 Vercel 的 Settings → Environment Variables 页面添加了 GITHUB_TOKEN，但没有创建 Secret github_token，所以 @github_token 这个引用找不到。
- 部署时如果环境变量未在对应环境中设置，运行时读取 `os.getenv()` 会返回 `None`。

### 解决方案
1. **在 Vercel 项目设置中添加环境变量**：
   - 进入项目 → Settings → Environment Variables
   - 添加键值对（如 `DATABASE_URL`）
   - 为 Production、Preview、Development 分别勾选生效环境

2. 不要在 vercel.json 里写 env 字段，直接删除即可。


---

## 3. Python 版本和依赖问题

### 问题描述
- 部署时报错："No module named 'xxx'"（缺少依赖）
- Python 版本不匹配导致某些包无法安装或运行时报错

### 根本原因
- `requirements.txt` 中未包含所有运行时需要的包
- Vercel 默认使用的 Python 版本可能与本地开发环境不同
- 某些包在特定 Python 版本下不兼容

### 解决方案
1. **确保 `requirements.txt` 完整**：
   ```txt
   Flask>=3.0.0
   Flask-CORS>=4.0.0
   Flask-SQLAlchemy>=3.1.0
   psycopg2-binary>=2.9.0
   openai>=1.0.0
   # ... 其他依赖
   ```

2. **在 `vercel.json` 或`runtime.txt` 中指定 Python 版本**：
   ```json
   {
     "functions": {
       "api/index.py": {
         "runtime": "python3.9"
       }
     }
   }
   ```


**关键要点**：
- serverless 环境是无状态的，每次冷启动都会重新安装依赖
- 尽量使用稳定的包版本范围（如 `>=3.0.0` 而非 `==3.0.1`）
- 避免在 `requirements.txt` 中包含不必要的大型包（会增加部署时间和冷启动延迟）

---

## 4. Flask `@before_first_request` 装饰器废弃

### 问题描述
在 Flask 3.0+ 版本中，代码中使用 `@app.before_first_request` 装饰器导致运行时警告或错误：
```
DeprecationWarning: 'before_first_request' is deprecated and will be removed in Flask 3.1
```

### 根本原因
- Flask 3.0 废弃了 `@before_first_request`，推荐使用应用上下文或在应用启动时执行初始化逻辑。
- serverless 环境的"第一次请求"概念模糊（每个函数实例可能独立冷启动）。

### 解决方案

**在模块导入时执行**（适合 serverless）
```python
# 在 src/main.py 中，app 实例化后
try:
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
except Exception as e:
    print(f"Warning: db.create_all() failed: {e}")
    traceback.print_exc()
```

**关键要点**：
- 在 serverless 中，应用上下文的初始化应当在模块导入时完成（而非等待第一次请求）
- 使用 try/except 包裹初始化逻辑，避免因数据库连接问题导致整个模块导入失败

---

## 5. 数据库从本地 SQLite 切换到远程 PostgreSQL

### 问题描述
- 本地开发时使用 SQLite 文件数据库（`database/notes.db`）
- 部署到 Vercel 时报错：`OSError: [Errno 30] Read-only file system: '/var/task/database'`
- serverless 环境的文件系统是只读的，无法创建或写入 SQLite 文件

### 根本原因
- Vercel serverless 函数运行在临时容器中，代码目录（`/var/task`）是只读的
- SQLite 依赖文件系统读写，不适合 serverless 部署
- 每个函数调用可能在不同容器中执行，本地文件不共享

### 解决方案
1. **使用远程 PostgreSQL 数据库**
   - 选择托管数据库服务：Supabase
   - 获取连接字符串（格式：`postgresql://user:password@host:port/dbname`）

2. **在 Vercel 中配置 `DATABASE_URL` 环境变量**：
   - 项目设置 → Environment Variables → 添加 `DATABASE_URL`
   - 值为上述连接字符串

3. **修改应用配置代码**（`src/main.py`）：
   ```python
   import os

   # 优先使用环境变量中的数据库 URL
   database_url = os.getenv("DATABASE_URL")
   if database_url:
       # 兼容 Heroku 老格式
       if database_url.startswith("postgres://"):
           database_url = database_url.replace("postgres://", "postgresql://", 1)
       app.config["SQLALCHEMY_DATABASE_URI"] = database_url
       print(f"Using remote database: {database_url[:30]}...")  # 只打印前缀，避免泄露密码
   else:
       # 回退到内存数据库（仅用于测试，数据不持久）
       print("Warning: DATABASE_URL not set; using in-memory SQLite.")
       app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
   ```

**关键要点**：
- SQLite 不适合 serverless 生产环境（无持久化、无并发支持）
- 使用托管数据库可获得备份、扩展性、连接池等企业级特性
- 连接字符串应通过环境变量注入，不要硬编码在代码中

---

## 6. `api/index.py` 入口文件的演进

### 问题描述
在部署过程中，`api/index.py` 经历了多次迭代，主要遇到以下错误：
- `TypeError: issubclass() arg 1 must be a class`
- `501 Unsupported method ('GET')`
- 静态资源和 API 请求无法正确路由

### 根本原因分析
1. **`issubclass` 错误**：
   - Vercel 的 Python 运行时（`vc__handler__python.py`）会检测导出的符号
   - 如果导出了名为 `handler` 的变量且该变量不是类（或是不兼容的类型），会触发 `issubclass()` 检查失败

2. **501 错误**：
   - 当运行时实例化了一个继承自 `BaseHTTPRequestHandler` 的类，但该类没有实现 `do_GET`、`do_POST` 等方法时，标准库会返回 `501 Unsupported method`
   - 早期版本的 `api/index.py` 导出了占位 `handler` 类（只有 `pass`），导致运行时使用该类处理请求时失败

3. **路由混乱**：
   - `api/index.py` 中定义了重复的 Flask 应用实例或路由
   - 与 `src/main.py` 中的应用定义冲突

### 解决方案演进过程

#### 阶段 1：初始尝试（失败）
```python
# 问题：导出了 handler 类但未实现 HTTP 方法
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    pass  # ❌ 会导致 501

# Vercel 运行时实例化 handler → 收到 GET 请求 → 返回 501
```

#### 阶段 2：实现代理类（部分成功）
```python
# 尝试实现 do_GET 等方法，将请求转发给 Flask
class VercelRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 构造 WSGI environ 并调用 app.wsgi_app
        # 但实现复杂且容易出错
        pass
```
问题：代理逻辑复杂，容易在环境变量构造、响应头处理等细节上出错。

#### 阶段 3：最终方案（成功）
**完全移除 `handler` 导出，只保留 WSGI callable**：


### 关键要点总结
- **不要导出 `handler` 类**：除非你能确保完整实现所有 HTTP 方法且与运行时兼容
- **优先使用 WSGI callable**：`wsgi_handler(environ, start_response)` 或直接导出 Flask 的 `app` 实例
- **保持 `api/index.py` 精简**：仅作为适配层，所有业务逻辑在 `src/main.py`
- **增加调试日志**：在导入时和请求处理时打印关键信息，便于在 Vercel 日志中追踪问题
---

**文档版本**：1.0  
**最后更新**：2025-10-16 
**维护者**：MA Jiyuan  
**项目仓库**：[note-taking-app-celvelzel](https://github.com/celvelzel/note-taking-app-celvelzel)
