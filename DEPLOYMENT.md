# 🚀 Vercel部署步骤指南

## 📋 部署前准备清单

### ✅ 您需要准备的账户和信息：
1. **GitHub账户** - 项目代码仓库
2. **Vercel账户** - 免费部署平台 (https://vercel.com)
3. **云数据库** - 选择一个云数据库服务 (见DATABASE_SETUP.md)
4. **GitHub Token** - 用于AI功能 (https://github.com/settings/tokens)

## 🎯 详细部署步骤

### 第一步：准备云数据库
1. 根据 `DATABASE_SETUP.md` 选择并配置云数据库
2. 获取数据库连接字符串 (DATABASE_URL)
3. 保存连接字符串，稍后在Vercel中使用

### 第二步：获取GitHub Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置名称：`NoteTaker AI功能`
4. 选择权限：无需特殊权限 (使用默认)
5. 点击 "Generate token"
6. **重要：立即复制token，刷新页面后将无法再看到**

### 第三步：推送代码到GitHub
```bash
# 如果还没有推送到GitHub
git add .
git commit -m "准备Vercel部署：添加配置文件和云数据库支持"
git push origin main
```

### 第四步：在Vercel上部署
1. 访问 https://vercel.com
2. 使用GitHub账户登录
3. 点击 "New Project"
4. 选择您的 `note-taking-app-celvelzel` 仓库
5. 点击 "Import"

### 第五步：配置环境变量
在Vercel项目设置中添加以下环境变量：

1. **DATABASE_URL**
   - 值：您的数据库连接字符串
   - 示例：`postgresql://username:password@host:port/database`

2. **GITHUB_TOKEN**
   - 值：您刚才获取的GitHub Token
   - 示例：`ghp_xxxxxxxxxxxxxxxxxxxx`

3. **SECRET_KEY**
   - 值：任意复杂字符串
   - 示例：`your-super-secret-key-change-this-in-production`

### 第六步：部署设置
- **Framework Preset**: Other
- **Build Command**: (留空)
- **Output Directory**: (留空)
- **Install Command**: `pip install -r requirements.txt`

### 第七步：部署
1. 点击 "Deploy"
2. 等待部署完成 (通常需要2-5分钟)
3. 部署成功后会显示访问链接

## 🔍 部署后验证

访问您的应用并测试以下功能：
- ✅ 页面正常加载
- ✅ 能够创建笔记
- ✅ 能够编辑和删除笔记
- ✅ 搜索功能正常
- ✅ AI信息提取功能正常 (需要GitHub Token)
- ✅ 分页功能正常

## 🚨 常见问题解决

### 部署失败
- 检查 `requirements.txt` 是否正确 
- 确保所有必要文件都已提交到GitHub

### 数据库连接失败
- 检查 DATABASE_URL 格式是否正确
- 确保数据库服务允许外部连接

### AI功能不工作
- 检查 GITHUB_TOKEN 是否设置正确
- 确保token有效且未过期

### 404错误
- 检查 `vercel.json` 配置
- 确保 `api/index.py` 文件存在

## 🔄 更新部署

每次推送到GitHub的main分支都会自动触发重新部署：
```bash
git add .
git commit -m "更新功能"
git push origin main
```

## 📞 需要帮助？

如果遇到问题，请检查：
1. Vercel的部署日志
2. 浏览器开发者工具的控制台
3. 确保所有环境变量都已正确设置

---
🎉 **恭喜！您的NoteTaker应用现在已经部署到云端了！**