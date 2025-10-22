# 商品 RAG 升级到 LangChain ElasticsearchStore

## 升级概述

本次升级将商品 RAG 功能改为使用 **LangChain ElasticsearchStore** 进行向量存储和查询，并简化了前端界面。

## 后端改造

### 1. 使用 LangChain ElasticsearchStore

**文件**: `backend/app/playground/product_rag/service.py`

#### 主要变更：

1. **引入 LangChain 组件**:
   ```python
   from langchain_elasticsearch import ElasticsearchStore
   from langchain_core.documents import Document
   ```

2. **初始化方式改变**:
   ```python
   # 获取 Embedding 实例
   self.embeddings = EmbeddingService.get_embeddings(self.embedding_model)
   
   # 使用 LangChain ElasticsearchStore
   es_params = {
       "es_url": settings.ELASTICSEARCH_URL,
       "index_name": self.index_name,
       "embedding": self.embeddings,
   }
   
   # 添加认证
   if settings.ELASTICSEARCH_API_KEY:
       es_params["es_api_key"] = settings.ELASTICSEARCH_API_KEY
   
   self.vector_store = ElasticsearchStore(**es_params)
   ```

3. **简化文档添加流程**:
   - LangChain 自动处理向量化
   - 使用 `Document` 对象，数据放在 `page_content` 和 `metadata` 中
   - 一次调用完成向量化和存储

4. **向量搜索**:
   - 使用 `similarity_search_with_score()` 方法
   - 自动返回文档和相似度分数
   - 无需手动生成查询向量

### 优势

✅ **更简洁的代码** - LangChain 自动处理向量化  
✅ **更好的性能** - 官方维护的集成  
✅ **更丰富的功能** - 支持混合搜索、过滤等  
✅ **更好的生态集成** - 与其他 LangChain 组件无缝对接  

## 前端改造

### 1. 简化页面结构

**文件**: `frontend/src/playground/productRag/pages/ProductRAGManagement.tsx`

#### 变更：
- ❌ 删除 "单次测试" 标签页
- ❌ 删除 "批量测试" 标签页  
- ❌ 删除 "统计分析" 标签页
- ✅ 保留 "上传管理"，并移除 Tabs 组件

### 2. 增强商品列表功能

**文件**: `frontend/src/playground/productRag/components/ProductList.tsx`

#### 新增功能：

1. **向量搜索框**:
   - 输入关键词进行向量搜索
   - 支持设置返回结果数量（top_k）
   - 回车或点击按钮触发搜索

2. **双模式显示**:
   - **列表模式**（默认）：显示所有商品，支持分页
   - **搜索模式**：显示向量搜索结果，包含相似度分数

3. **搜索结果展示**:
   - 排名标签（蓝色）
   - 相似度分数（绿色>80%，橙色>60%）
   - 匹配内容展示
   - 搜索耗时显示

4. **交互优化**:
   - 一键返回列表模式
   - 清空数据时自动退出搜索模式
   - 提示信息指导用户使用

## 使用说明

### 1. 上传商品数据

1. 准备 JSON 格式的商品数据
2. 点击或拖拽上传文件
3. 系统自动：
   - 提取商品信息（goodsName、brandName 等）
   - 使用 OpenAI Embedding 生成向量
   - 存储到 Elasticsearch

### 2. 查看商品列表

- 页面默认显示所有商品
- 支持分页浏览
- 显示总数统计

### 3. 向量搜索

1. 在搜索框输入关键词（如："安全帽"）
2. 设置返回结果数量（默认 10）
3. 点击"搜索"按钮
4. 查看搜索结果：
   - 排名
   - 相似度分数
   - 商品详细信息
   - 匹配内容

### 4. 返回列表

- 点击"返回列表"按钮
- 或点击"清空所有数据"后自动返回

## 技术栈

### 后端
- **向量存储**: LangChain ElasticsearchStore
- **Embedding**: OpenAI text-embedding-3-small (1536维)
- **索引**: product_rag_test

### 前端
- **框架**: React + TypeScript + Ant Design
- **状态管理**: React Hooks (useState, useEffect)
- **API**: Axios

## 配置要求

### Elasticsearch
确保 `backend/app/core/config.py` 中配置正确：

```python
ELASTICSEARCH_URL: str = "http://localhost:9200"
ELASTICSEARCH_API_KEY: str = "your-api-key"
```

### OpenAI
需要配置 OpenAI API Key：

```python
OPENAI_API_KEY: str = "sk-..."
```

## 已安装依赖

```txt
langchain>=0.3.0
langchain-elasticsearch>=0.1.0
langchain-core
elasticsearch>=8.11.0
```

## 测试步骤

1. **启动后端**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **启动前端**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **访问页面**: `http://localhost:3000/system/product-rag`

4. **上传测试数据**

5. **测试搜索功能**:
   - 输入 "安全帽"
   - 查看相似商品列表
   - 检查相似度分数

## 注意事项

1. ⚠️ 确保 Elasticsearch 服务正在运行
2. ⚠️ 确保 OpenAI API Key 有效且有余额
3. ⚠️ 清空数据会删除 ES 索引，操作不可恢复
4. 💡 搜索结果按相似度分数降序排列
5. 💡 支持中文和英文关键词搜索

## 下一步优化建议

- [ ] 支持混合搜索（向量 + 关键词）
- [ ] 添加过滤条件（品牌、价格区间等）
- [ ] 支持多模态搜索（图片+文本）
- [ ] 添加搜索历史记录
- [ ] 优化 Embedding 模型选择
- [ ] 添加批量导入功能

