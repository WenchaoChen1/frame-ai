# RAG 实施问题修复记录

## 问题 1：VECTOR 类型导入错误

**错误信息**：
```
ImportError: cannot import name 'VECTOR' from 'sqlalchemy.dialects.postgresql'
```

**原因**：
`VECTOR` 类型不是 SQLAlchemy 内置的，而是由 `pgvector` 扩展提供的。

**解决方案**：
1. 从 `pgvector.sqlalchemy` 导入 `Vector` 类型
2. 添加容错处理，如果 pgvector 未安装也能正常导入模块

**修改文件**：
- `backend/app/models/knowledge_base.py` - 修改导入语句

**需要安装的依赖**：
```bash
pip install pgvector
```

---

## 问题 2：metadata 保留字冲突

**错误信息**：
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**原因**：
`metadata` 是 SQLAlchemy Declarative API 的保留字段名，不能直接用作模型字段。

**解决方案**：
将 `KnowledgeBaseChunk` 模型的 `metadata` 字段重命名为 `meta_data`。

**修改文件**：
1. `backend/app/models/knowledge_base.py` - 字段定义
2. `backend/app/services/vector_store/pgvector_store.py` - 字段使用
3. `backend/app/services/retrieval_service.py` - 字段使用
4. `backend/migrations/005_add_knowledge_base_tables.sql` - 表结构
5. `backend/app/schemas/knowledge_base.py` - API schema（使用 alias 映射）

---

## 问题 3：缺少 RAG 依赖包

**错误信息**：
```
ModuleNotFoundError: No module named 'elasticsearch'
```

**原因**：
新增的 RAG 功能需要额外的依赖包，但还没有安装。

**解决方案**：
安装所有 RAG 相关的依赖包：

```bash
pip install elasticsearch pgvector sentence-transformers pypdf python-docx pdfplumber rank-bm25 faiss-cpu langchain-community langchain-elasticsearch unstructured jieba
```

或者一次性安装所有依赖：

```bash
pip install -r requirements.txt
```

**修改文件**：
- `backend/requirements.txt` - 已包含所有新依赖

---

## 验证修复

运行以下命令验证所有问题已解决：

```bash
# 1. 确保在虚拟环境中
cd backend
.\venv\Scripts\activate

# 2. 安装/更新依赖
pip install pgvector

# 3. 测试导入
python -c "from app.models.knowledge_base import KnowledgeBase; print('✓ 导入成功')"

# 4. 启动应用
python -m app.main
```

如果没有错误，说明修复成功！

---

## 下一步

1. **运行数据库迁移**：
   ```bash
   python migrations/run_migration_005.py
   ```

2. **启动应用**：
   ```bash
   python -m app.main
   ```

3. **访问 API 文档**：
   http://localhost:8000/docs

4. **开始使用 RAG 功能**：
   查看 `QUICK_START.md` 了解如何创建知识库和上传文档

---

## 技术说明

### pgvector 类型系统

pgvector 提供了 PostgreSQL 向量类型的 SQLAlchemy 支持：

```python
from pgvector.sqlalchemy import Vector

# 定义向量字段
embedding = Column(Vector(1536))  # 1536 维向量
```

### SQLAlchemy 保留字

以下字段名在 SQLAlchemy Declarative API 中是保留的：
- `metadata` - 用于表的元数据
- `__tablename__` - 表名
- `__table__` - 表对象
- `__mapper__` - 映射器对象

如果需要使用这些名称，可以：
1. 使用其他名称（如 `meta_data`）
2. 使用 `Column` 的 `name` 参数映射到不同的数据库列名

### Pydantic Field Alias

在 API schema 中，可以使用 `alias` 保持 API 字段名与数据库字段名不同：

```python
metadata: Optional[str] = Field(None, alias='meta_data')

class Config:
    from_attributes = True
    populate_by_name = True  # 允许使用 alias
```

这样，API 仍然使用 `metadata` 字段名，但实际映射到数据库的 `meta_data` 字段。

