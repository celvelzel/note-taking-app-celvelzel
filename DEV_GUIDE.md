# 🖥️ 本地开发指南

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/note-taking-app-celvelzel.git
cd note-taking-app-celvelzel
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的配置
```

### 4. 运行应用
```bash
# 使用原始版本 (本地SQLite)
python src/main.py

# 或使用Vercel兼容版本 (需要云数据库)
python api/index.py
```

## 🔧 开发模式

- **本地数据库**: 使用 `src/main.py` 启动，自动使用SQLite
- **云数据库测试**: 使用 `api/index.py` 启动，需要设置DATABASE_URL
- **AI功能**: 需要设置GITHUB_TOKEN环境变量

## 📁 项目结构

```
├── api/                 # Vercel部署入口
├── src/                 # 源代码
│   ├── models/         # 数据模型
│   ├── routes/         # API路由
│   ├── services/       # 服务层
│   └── static/         # 前端文件
├── vercel.json         # Vercel配置
├── requirements.txt    # Python依赖
└── DEPLOYMENT.md       # 部署指南
```

## 🌐 访问地址

- 本地开发: http://localhost:5001
- Vercel部署: https://your-app.vercel.app

## 🚀 准备部署

完成开发后，按照 `DEPLOYMENT.md` 指南部署到Vercel。