# 商品RAG召回测试功能指南

## 概述

商品RAG召回测试是一个独立的功能模块，用于测试商品数据的向量化存储和RAG（Retrieval-Augmented Generation）召回效果。该模块前后端完全独立，方便管理和删除。

## 功能特性

### 核心功能

- ✅ **JSON文件上传**: 支持单个商品或批量商品上传
- ✅ **自动向量化**: 使用 LangChain + OpenAI Embeddings 自动生成向量
- ✅ **Elasticsearch存储**: 高效的向量存储和相似度搜索
- ✅ **单次召回测试**: 实时测试单个查询的召回效果
- ✅ **批量召回测试**: 同时测试多个查询，对比召回效果
- ✅ **结果分析**: 查看排名、相似度分数、召回率等指标
- ✅ **统计信息**: 实时统计商品数量、向量数量等

### 技术栈

**后端:**
- FastAPI
- SQLAlchemy
- LangChain
- Elasticsearch
- OpenAI Embeddings

**前端:**
- React + TypeScript
- Ant Design
- Axios

## 快速开始

### 1. 环境准备

#### 安装依赖

确保已安装项目依赖：

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

#### 启动必要服务

```bash
# 1. PostgreSQL (如果还没启动)
# 使用现有的数据库即可

# 2. Elasticsearch
docker run -d \
  --name elasticsearch \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -p 9200:9200 \
  elasticsearch:8.11.0

# 验证 ES 运行
curl http://localhost:9200
```

#### 配置环境变量

在 `backend/.env` 中添加或确认：

```env
# 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatai

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=

# OpenAI (必须)
OPENAI_API_KEY=your_openai_api_key_here

# 嵌入模型
DEFAULT_EMBEDDING_MODEL=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 2. 运行数据库迁移

```bash
cd backend
python migrations/run_migration_007.py
```

输出应显示：
```
✅ Migration 007 执行成功！

创建的表:
- products (商品表)
```

### 3. 启动服务

```bash
# 启动后端
cd backend
python -m app.main

# 启动前端（新终端）
cd frontend
npm run dev
```

### 4. 访问界面

打开浏览器访问：`http://localhost:5173`

登录后，导航到：**系统管理 > 商品RAG测试**

或直接访问：`http://localhost:5173/system/product-rag`

## 使用流程

### 步骤 1: 准备商品数据

准备一个 JSON 文件，格式如下：

**单个商品:**
```json
{
  "id": "504675972260356096",
  "sellSpuId": "1959914744219435008",
  "goodsName": "安赛瑞 安全帽遮阳板（红）",
  "goodsAlias": "SAFEWARE/安赛瑞 安全帽遮阳板",
  "brandName": "安赛瑞",
  "productSpecifications": "工地安全帽,ABS安全帽",
  "searchKeyWord": "安全帽 遮阳板"
}
```

**多个商品（数组）:**
```json
[
  {
    "id": "1",
    "goodsName": "商品1",
    ...
  },
  {
    "id": "2",
    "goodsName": "商品2",
    ...
  }
]
```

### 步骤 2: 上传商品数据

1. 切换到 **"上传管理"** 标签页
2. 拖拽或点击上传 JSON 文件
3. 等待处理完成（会显示处理时间）
4. 查看商品列表

**处理过程:**
- 解析 JSON 数据
- 组合商品字段生成文本
- 调用 OpenAI API 生成向量
- 存储到 PostgreSQL 和 Elasticsearch

### 步骤 3: 单次召回测试

1. 切换到 **"单次测试"** 标签页
2. 输入查询词，例如："安全帽"
3. 设置返回结果数量（默认10）
4. 点击 **"搜索"** 按钮
5. 查看结果：
   - 排名
   - 商品名称
   - 品牌
   - 相似度分数

**评估指标:**
- **相似度分数**: 0-1之间，越高越相似
- **排名**: 按相似度降序排列
- **召回率**: Top-N 中相关商品的比例

### 步骤 4: 批量召回测试

1. 切换到 **"批量测试"** 标签页
2. 输入多个查询词（每行一个），例如：
   ```
   安全帽
   防护服
   安全鞋
   ```
3. 设置每个查询返回的结果数量
4. 点击 **"批量搜索"**
5. 展开折叠面板查看每个查询的结果

**对比分析:**
- 不同查询的召回效果
- 各查询的耗时对比
- Top-N 结果的相似度分布

### 步骤 5: 查看统计信息

切换到 **"统计分析"** 标签页查看：

- **总商品数**: 数据库中的商品记录数
- **ES向量总数**: Elasticsearch 中的向量数量
- **ES索引名称**: `product_rag_test`
- **嵌入模型**: `openai_small`

## API 文档

### 上传商品

```http
POST /api/product-rag/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: products.json
```

### 获取商品列表

```http
GET /api/product-rag/products?page=1&page_size=20
Authorization: Bearer {token}
```

### 单次搜索

```http
POST /api/product-rag/search
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "安全帽",
  "top_k": 10
}
```

### 批量搜索

```http
POST /api/product-rag/batch-search
Content-Type: application/json
Authorization: Bearer {token}

{
  "queries": ["安全帽", "防护服", "安全鞋"],
  "top_k": 10
}
```

### 获取统计

```http
GET /api/product-rag/stats
Authorization: Bearer {token}
```

### 清空数据

```http
DELETE /api/product-rag/clear
Authorization: Bearer {token}
```

## 测试脚本

使用命令行测试功能：

```bash
cd backend
python test_product_rag.py
```

该脚本会：
1. 上传示例商品数据
2. 执行搜索测试
3. 显示统计信息
4. 可选择清空测试数据

## 目录结构

```
backend/app/playground/product_rag/          # 后端模块
├── __init__.py                   # 模块初始化
├── models.py                     # 数据模型
├── schemas.py                    # Pydantic schemas
├── service.py                    # 核心服务
├── router.py                     # API路由
└── README.md                     # 后端文档

frontend/src/playground/productRag/ # 前端模块
├── components/                   # 组件
│   ├── ProductUpload.tsx
│   ├── ProductList.tsx
│   ├── SearchTest.tsx
│   ├── BatchSearchTest.tsx
│   ├── SearchResults.tsx
│   └── Statistics.tsx
├── pages/                        # 页面
│   └── ProductRAGManagement.tsx
├── services/                     # API服务
│   └── productRagApi.ts
├── types/                        # 类型定义
│   └── index.ts
└── README.md                     # 前端文档

backend/migrations/               # 数据库迁移
├── 007_add_products_table.sql
├── rollback_007.sql
└── run_migration_007.py
```

## 技术细节

### 向量化策略

组合以下字段生成向量：

```python
text = f"{goodsName} {goodsAlias} {brandName} {productSpecifications} {searchKeyWord}"
```

这样可以确保：
- 商品名称有高权重
- 品牌信息被考虑
- 产品规格参与匹配
- 搜索关键词优化召回

### 存储架构

- **PostgreSQL**: 存储商品元数据（id, name, brand等）
- **Elasticsearch**: 存储向量和支持 KNN 搜索
- **索引名称**: `product_rag_test`
- **向量维度**: 1536 (text-embedding-3-small)

### 召回算法

使用 Elasticsearch 的 KNN (K-Nearest Neighbors) 搜索：

```python
query = {
    "knn": {
        "field": "embedding",
        "query_vector": query_embedding,
        "k": top_k,
        "num_candidates": top_k * 2
    }
}
```

## 性能优化建议

1. **批量处理**: 一次上传多个商品，减少 API 调用
2. **异步处理**: 使用 async/await 提高并发
3. **缓存策略**: 频繁查询的结果可以缓存
4. **ES配置**: 根据数据量调整 shard 和 replica

## 故障排查

### 1. Elasticsearch 连接失败

**症状**: 上传或搜索时报错 "Connection refused"

**解决方案**:
```bash
# 检查 ES 是否运行
curl http://localhost:9200

# 重启 ES
docker restart elasticsearch

# 查看 ES 日志
docker logs elasticsearch
```

### 2. OpenAI API 错误

**症状**: "Authentication failed" 或 "Rate limit"

**解决方案**:
```bash
# 检查 API Key
echo $OPENAI_API_KEY

# 检查配额
# 登录 OpenAI 控制台查看使用情况

# 降低并发请求
# 减少 batch 大小或增加延迟
```

### 3. 向量维度不匹配

**症状**: "Dimension mismatch"

**解决方案**:
```bash
# 确保使用相同的 embedding 模型
# 清空 ES 索引重新创建
curl -X DELETE http://localhost:9200/product_rag_test
```

### 4. 数据库表不存在

**症状**: "Table 'products' doesn't exist"

**解决方案**:
```bash
# 运行迁移脚本
cd backend
python migrations/run_migration_007.py
```

## 删除模块

如需完全删除此功能：

### 1. 删除后端

```bash
# 1. 回滚数据库
cd backend
psql -U postgres -d chatai -f migrations/rollback_007.sql

# 2. 删除代码
rm -rf backend/app/playground/product_rag

# 3. 从 application.py 移除路由注册
# 编辑 backend/app/application.py
# 删除: from .playground.product_rag import router as product_rag_router
# 删除: self.app.include_router(product_rag_router.router)
```

### 2. 删除前端

```bash
# 1. 删除代码
rm -rf frontend/src/playground/productRag

# 2. 从路由配置移除
# 编辑 frontend/src/router/routes.tsx
# 删除相关导入和路由配置
```

### 3. 清理 Elasticsearch

```bash
# 删除索引
curl -X DELETE http://localhost:9200/product_rag_test
```

## 扩展建议

1. **增加更多召回策略**:
   - BM25 关键词召回
   - 混合召回（向量 + 关键词）
   - 多路召回融合

2. **添加重排序**:
   - 使用 Cross-Encoder 模型
   - 业务规则重排
   - 个性化排序

3. **增强分析功能**:
   - 召回率曲线
   - A/B 测试对比
   - 错误案例分析

4. **支持更多数据源**:
   - CSV 文件
   - Excel 文件
   - 数据库直连

## 常见问题

**Q: 为什么要组合多个字段？**
A: 单一字段可能信息不足，组合多个字段可以提供更丰富的语义信息，提高召回效果。

**Q: 向量维度可以修改吗？**
A: 可以，但需要修改 `service.py` 中的配置，并清空重建 ES 索引。

**Q: 支持中文分词吗？**
A: OpenAI 的 embedding 模型原生支持中文，无需额外分词。

**Q: 数据量大时如何优化？**
A: 建议批量处理、异步上传、增加 ES 节点、使用更大的 embedding 模型。

## 许可证

本模块遵循项目主许可证。

## 联系支持

如有问题，请参考项目文档或提交 Issue。

