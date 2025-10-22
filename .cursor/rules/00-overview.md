# 项目概述

这是一个基于 FastAPI + React + TypeScript 的 AI 聊天对话系统，支持多种 AI 提供商（OpenAI、Claude、Ollama），包含 RAG、知识库、Text-to-SQL 等功能。

---

## 🛠️ 技术栈

> 版本信息以 `package.json` 和 `requirements.txt` 为准

### 后端技术栈
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL
- **AI框架**: LangChain + LangGraph
- **认证**: JWT (PyJWT)
- **向量存储**: Elasticsearch + pgvector
- **日志**: Python logging
- **测试**: pytest + pytest-asyncio

### 前端技术栈
- **框架**: React
- **语言**: TypeScript
- **构建工具**: Vite
- **状态管理**: Zustand
- **路由**: React Router
- **HTTP客户端**: Axios
- **UI组件**: Ant Design + Ant Design X
- **AI组件**: @ant-design/x (专用 AI 对话组件)
- **测试**: Vitest + React Testing Library

