# 云数据库配置指南

这个项目支持多种云数据库服务。选择以下任一服务：

## 🚀 推荐选项

### 1. Railway (最简单)
1. 访问 https://railway.app/
2. 使用GitHub账户登录
3. 创建新项目 → 选择"PostgreSQL"
4. 复制连接字符串(DATABASE_URL)

### 2. Supabase (功能丰富)
1. 访问 https://supabase.com/
2. 创建新项目
3. 到 Settings → Database → Connection string
4. 复制连接字符串

### 3. PlanetScale (MySQL)
1. 访问 https://planetscale.com/
2. 创建数据库
3. 创建分支
4. 获取连接字符串

### 4. Neon (PostgreSQL)
1. 访问 https://neon.tech/
2. 创建数据库
3. 复制连接字符串

## 📝 环境变量设置

无论选择哪个服务，您都需要设置以下环境变量：

```bash
DATABASE_URL=your_database_connection_string_here
GITHUB_TOKEN=your_github_token_here
SECRET_KEY=your_secret_key_here
```

## 🔧 连接字符串格式

- **PostgreSQL**: `postgresql://username:password@host:port/database`
- **MySQL**: `mysql://username:password@host:port/database`

## ⚠️ 注意事项

1. 数据库将在首次部署时自动创建表结构
2. 请确保数据库服务支持外部连接
3. 生产环境请使用强密码
4. 定期备份重要数据

## 🆓 免费方案

以上所有服务都提供免费方案，足够开发和小型项目使用。