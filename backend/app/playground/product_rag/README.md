# 商品RAG召回测试系统

## 概述

本系统**专门使用 Elasticsearch** 进行商品向量化存储和相似度搜索，**完全独立于 PostgreSQL**，不会在数据库中创建或查询商品表。

## 核心特性

- ✅ **纯ES存储**：使用 Elasticsearch 存储商品向量和元数据
- ✅ **不使用PGVector**：已移除所有PostgreSQL向量存储相关代码
- ✅ 支持批量上传商品JSON数据
- ✅ 自动向量化商品信息（OpenAI Embeddings）
- ✅ 高性能向量相似度搜索
- ✅ 完全独立的测试环境，不影响业务数据库

## 数据流程

```
JSON数据 → 文本组合 → OpenAI Embedding → Elasticsearch存储
                ↓
          向量相似度搜索 ← 查询文本
```

## JSON数据格式

系统支持包含 `list` 字段的分页格式：

```json
{
  "list": [
    {
      "id": "504675972260356096",
      "goodsName": "商品名称",
      "goodsAlias": "商品别名",
      "brandName": "品牌名称",
      "productSpecifications": "产品规格",
      "searchKeyWord": "搜索关键词",
      "sellSpuId": "SPU ID",
      ...其他字段
    }
  ]
}
```

## 配置说明

### 1. Elasticsearch配置

确保 Elasticsearch 服务已启动，并在 `.env` 文件中配置：

```bash
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=  # 可选，如果需要认证
```

### 2. OpenAI配置

系统使用 OpenAI 的 `text-embedding-3-small` 模型生成向量：

```bash
OPENAI_API_KEY=your-openai-api-key
```

### 3. 向量存储配置

在 `service.py` 中已配置：

```python
# ES索引名称
PRODUCT_INDEX_NAME = "product_rag_test"
# 使用的embedding模型
EMBEDDING_MODEL = EmbeddingModel.OPENAI_SMALL
# 向量维度
EMBEDDING_DIMENSION = 1536
```

**注意：** 本系统只使用Elasticsearch，不支持PGVector。

## API接口

### 1. 上传商品数据

```
POST /api/product-rag/upload
Content-Type: multipart/form-data
```

上传JSON文件，系统会自动：
- 提取 `list` 字段中的商品数组
- 组合商品文本（商品名称、别名、品牌、规格等）
- 生成向量
- 存储到 Elasticsearch

### 2. 单次召回测试

```
POST /api/product-rag/search
Content-Type: application/json

{
  "query": "安全帽",
  "top_k": 10
}
```

返回最相似的商品列表，包含排名和相似度分数。

### 3. 批量召回测试

```
POST /api/product-rag/batch-search
Content-Type: application/json

{
  "queries": ["安全帽", "工地帽", "防护帽"],
  "top_k": 10
}
```

批量测试多个查询词的召回效果。

### 4. 获取商品列表

```
GET /api/product-rag/products?page=1&page_size=20
```

**从 Elasticsearch 查询商品列表**，支持分页。

### 5. 统计信息

```
GET /api/product-rag/stats
```

返回：
- ES中的商品总数
- 索引名称
- 使用的嵌入模型

### 6. 清空所有数据

```
DELETE /api/product-rag/clear
```

**只删除 Elasticsearch 索引**，不影响 PostgreSQL 数据库。

## 使用流程

### 1. 准备JSON数据

确保JSON数据包含必需字段：
- `id` 或 `goodsSaleId`：商品唯一标识
- `goodsName`：商品名称
- `goodsAlias`：商品别名（可选）
- `brandName`：品牌名称（可选）
- `productSpecifications`：产品规格（可选）
- `searchKeyWord`：搜索关键词（可选）

### 2. 上传数据

在前端页面点击"上传JSON文件"，选择包含商品信息的JSON文件。

系统会：
1. 解析JSON，提取 `list` 字段
2. 为每个商品生成向量
3. 存储到 Elasticsearch

### 3. 查看商品列表

上传成功后，可以在"商品列表"标签页查看已上传的商品（数据来自ES）。

### 4. 测试召回

- **单次测试**：输入查询词，点击"搜索"，查看召回结果
- **批量测试**：输入多个查询词（换行分隔），批量测试召回效果
- **统计分析**：查看召回结果的统计信息

## 向量化字段

系统会组合以下字段进行向量化：

1. `goodsName`：商品名称
2. `goodsAlias`：商品别名
3. `brandName`：品牌名称
4. `productSpecifications`：产品规格
5. `searchKeyWord`：搜索关键词

组合后的文本示例：
```
安赛瑞 安全帽遮阳板（红）... SAFEWARE/安赛瑞... 安赛瑞 工地安全帽,ABS安全帽 安赛瑞 安全帽遮阳板
```

## 存储结构

### Elasticsearch文档结构

```json
{
  "_id": "504675972260356096",
  "_source": {
    "content": "组合后的商品文本",
    "embedding": [0.123, 0.456, ...],  // 1536维向量
    "metadata": {
      "product_id": "504675972260356096",
      "sell_spu_id": "1959914744219435008",
      "goods_name": "商品名称",
      "goods_alias": "商品别名",
      "brand_name": "品牌名称",
      "specifications": "产品规格",
      "original_data": {...}  // 完整的原始商品数据
    }
  }
}
```

## 注意事项

1. **OpenAI API密钥**：需要有效的OpenAI API密钥才能生成向量
2. **Elasticsearch服务**：确保ES服务运行在配置的URL上
3. **数据独立性**：商品数据只存储在ES中，不会写入PostgreSQL
4. **查询性能**：ES的向量搜索性能优异，适合大规模商品库
5. **成本控制**：向量生成会调用OpenAI API，注意成本

## 故障排查

### 1. 上传失败

- 检查JSON格式是否正确
- 确认包含 `list` 字段
- 查看后端日志了解详细错误

### 2. 搜索无结果

- 确认已上传商品数据
- 检查ES索引是否存在：`curl http://localhost:9200/product_rag_test/_count`
- 尝试不同的查询词

### 3. 连接错误

- 检查ES服务状态：`curl http://localhost:9200`
- 确认 `ELASTICSEARCH_URL` 配置正确
- 如果使用API密钥，确认 `ELASTICSEARCH_API_KEY` 正确

## 技术栈

- **向量存储**：Elasticsearch 8.x+ (支持 dense_vector)
- **向量模型**：OpenAI text-embedding-3-small (1536维)
- **相似度算法**：Cosine Similarity
- **后端框架**：FastAPI
- **前端框架**：React + TypeScript

## 开发说明

### 修改向量维度

如果需要使用其他embedding模型，修改 `service.py`：

```python
EMBEDDING_MODEL = EmbeddingModel.OPENAI_LARGE  # 或其他模型
EMBEDDING_DIMENSION = 3072  # 对应的维度
```

### 修改索引名称

```python
PRODUCT_INDEX_NAME = "your_index_name"
```

### 关于PGVector

本系统已经移除了PGVector支持，**只使用Elasticsearch**。如果需要使用PGVector，请参考 `vector_store_pgvector.py` 文件自行实现。

选择Elasticsearch的原因：
- 高性能向量搜索
- 易于扩展和部署
- 与业务数据库完全隔离
- 不需要在PostgreSQL上安装额外扩展

## 参考资料

- [Elasticsearch Vector Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
