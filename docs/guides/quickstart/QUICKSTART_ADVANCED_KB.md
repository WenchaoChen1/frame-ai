# 知识库高级配置 - 快速启动指南

## 🚀 5分钟快速开始

### 步骤 1: 数据库迁移

```bash
# 进入后端目录
cd backend

# 运行迁移脚本
python migrations/run_migration_006.py
```

**预期输出**：
```
🚀 开始执行 Migration 006...
✅ 执行成功: CREATE TYPE embedding_provider_enum...
✅ 执行成功: CREATE TYPE embedding_model_enum...
✅ 执行成功: ALTER TABLE knowledge_bases...
✨ Migration 006 执行成功!
```

### 步骤 2: 启动后端服务

```bash
# 确保在 backend 目录
cd backend

# 激活虚拟环境（如果使用）
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 3: 启动前端服务

```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
```

### 步骤 4: 访问系统

打开浏览器访问：`http://localhost:5173`

## 🎯 功能测试

### 测试 1: 创建知识库（系统库）

1. 登录系统
2. 导航到：**系统管理** → **知识库管理**
3. 点击 **创建知识库**
4. 填写信息：
   - **名称**：测试知识库
   - **向量存储**：PostgreSQL + pgvector
   - 看到提示：✓ 使用系统库
   - **嵌入模型厂商**：OpenAI
   - **嵌入模型**：text-embedding-3-small
5. 点击 **确定**

✅ **预期结果**：创建成功，显示在知识库列表中

### 测试 2: 创建知识库（外部 ES）

1. 点击 **创建知识库**
2. 填写信息：
   - **名称**：ES测试知识库
   - **向量存储**：Elasticsearch
   - **选择外部 ES 配置**：选择一个配置
   - **嵌入模型厂商**：OpenAI
   - **嵌入模型**：text-embedding-3-large
3. 点击 **确定**

✅ **预期结果**：创建成功，使用外部 ES 配置

### 测试 3: 上传文档并验证锁定

1. 点击知识库卡片进入详情页
2. 点击 **添加文档** 上传一个文件
3. 等待文档处理完成
4. 点击左侧 **设置** 标签
5. 观察页面变化

✅ **预期结果**：
- 显示黄色警告框："配置已锁定"
- 向量存储类型和嵌入模型字段被禁用
- 字段下方显示："已有文档，不可修改"
- 分块大小和重叠仍可编辑

### 测试 4: 切换不同厂商

1. 创建新知识库
2. **嵌入模型厂商** 选择 **Claude**
3. **嵌入模型** 下拉框自动更新，显示 Claude 的模型
4. 切换到 **Ollama**
5. 观察模型列表变化

✅ **预期结果**：
- 级联选择正常工作
- 每个厂商显示对应的模型列表
- 模型描述和维度信息正确显示

### 测试 5: 召回测试

1. 进入有文档的知识库详情页
2. 点击 **召回测试** 标签
3. 选择检索方式：
   - 问题检索
   - 全文检索
   - 混合检索（推荐）
4. 如选择混合检索，调整权重和 Rerank 设置
5. 设置 Top K 和 Score 阈值
6. 输入测试查询并点击 **测试召回**

✅ **预期结果**：
- 返回相关文档块
- 显示相似度分数
- 可展开查看完整内容

## 🔧 常见问题

### Q1: 迁移脚本报错

**A**: 检查数据库连接配置，确保 `backend/app/core/config.py` 中的 `DATABASE_URL` 正确。

### Q2: 前端显示空白

**A**: 
1. 检查后端服务是否运行：`curl http://localhost:8000/api/providers/embeddings`
2. 查看浏览器控制台错误信息
3. 清除浏览器缓存

### Q3: 无法选择外部 ES

**A**: 当前外部 ES 配置为示例数据，如需实际使用，需要在数据库中配置真实的 ES 连接。

### Q4: 配置锁定不生效

**A**: 确保：
1. 数据库迁移成功执行
2. 知识库确实有上传的文档（`document_count > 0`）
3. 后端服务已重启

## 📊 API 测试

使用 curl 或 Postman 测试 API：

### 获取嵌入模型提供商

```bash
curl http://localhost:8000/api/providers/embeddings
```

### 获取 OpenAI 的模型

```bash
curl http://localhost:8000/api/providers/embeddings?provider=openai
```

### 获取向量存储配置

```bash
curl http://localhost:8000/api/providers/vector-stores
```

### 创建知识库

```bash
curl -X POST http://localhost:8000/api/knowledge-bases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "API测试知识库",
    "vector_store_type": "pgvector",
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "chunk_size": 500,
    "chunk_overlap": 50
  }'
```

## 🎓 下一步

现在你已经掌握了基础功能，可以：

1. **配置真实的 Elasticsearch** - 用于生产环境
2. **配置 Ollama 本地模型** - 用于离线环境
3. **关联知识库到机器人** - 启用 RAG 对话
4. **优化分块策略** - 提高召回效果
5. **测试不同嵌入模型** - 对比性能

查看完整文档：[KNOWLEDGE_BASE_ADVANCED_CONFIG.md](KNOWLEDGE_BASE_ADVANCED_CONFIG.md)

## ✅ 验收清单

- [ ] 数据库迁移成功
- [ ] 后端服务正常启动
- [ ] 前端服务正常启动
- [ ] 可以创建知识库（系统库）
- [ ] 可以创建知识库（外部 ES）
- [ ] 级联选择正常工作
- [ ] 上传文档后配置被锁定
- [ ] 召回测试正常工作
- [ ] API 接口返回正确数据

全部勾选表示功能正常！🎉

## 📞 获取帮助

- 查看详细文档：[KNOWLEDGE_BASE_ADVANCED_CONFIG.md](KNOWLEDGE_BASE_ADVANCED_CONFIG.md)
- 查看 RAG 功能：[RAG_FEATURE_GUIDE.md](RAG_FEATURE_GUIDE.md)
- 查看文档分块：[DOCUMENT_CHUNK_MANAGEMENT.md](DOCUMENT_CHUNK_MANAGEMENT.md)

