# 快速开始指南

5分钟快速启动AI聊天系统！

## 前置条件

确保你的系统已安装：
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 快速启动步骤

### 1. 下载项目

```bash
git clone <repository-url>
cd fangying-ai
```

### 2. 配置API密钥

创建 `.env` 文件：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，添加至少一个AI提供商的API密钥：

```env
# 至少配置一个
OPENAI_API_KEY=sk-your-openai-api-key
# 或
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
# 或使用本地Ollama（无需API密钥）
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**获取API密钥**：
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 3. 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows（使用Git Bash或WSL）
bash start.sh

# Windows（PowerShell）
docker-compose up -d
```

#### 方式二：使用Docker Compose

```bash
docker-compose up -d
```

### 4. 访问应用

打开浏览器访问：
- **前端应用**: http://localhost
- **API文档**: http://localhost:8000/docs

### 5. 注册并登录

1. 点击"注册账号"
2. 填写用户名、邮箱、密码
3. 自动登录到聊天界面

### 6. 开始聊天

1. 点击"新建对话"创建会话
2. 选择AI提供商和模型
3. 输入消息，按Enter发送
4. 享受流式AI响应！

## 停止服务

```bash
# 使用脚本
./stop.sh

# 或使用Docker Compose
docker-compose down
```

## 常见问题

### Q: 启动失败？

查看日志：
```bash
docker-compose logs -f
```

### Q: 前端无法访问？

1. 检查服务状态：`docker-compose ps`
2. 确保端口80和8000未被占用
3. 尝试重启：`docker-compose restart`

### Q: AI响应错误？

1. 检查API密钥是否正确配置
2. 确认API密钥有额度
3. 查看后端日志：`docker-compose logs backend`

### Q: 使用本地Ollama？

1. 安装Ollama: https://ollama.ai/
2. 下载模型: `ollama pull llama2`
3. 确保Ollama运行在11434端口
4. 在聊天界面选择"ollama"提供商

## 下一步

- 阅读 [完整文档](./README.md)
- 查看 [API文档](./API.md)
- 了解 [部署指南](./DEPLOYMENT.md)

## 需要帮助？

- 查看 [README.md](./README.md) 常见问题部分
- 提交 Issue
- 查看 [API文档](http://localhost:8000/docs)

祝你使用愉快！🎉

