# 知识库功能调试指南

## 🔍 问题：页面不显示知识库列表

### 步骤 1：检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 "Console" 标签
3. 刷新知识库管理页面
4. 查看控制台输出：

**正常情况应该看到：**
```
✅ 知识库数据: []
```

**如果有错误会看到：**
```
❌ 加载知识库失败: [错误信息]
```

### 步骤 2：检查网络请求

1. 在开发者工具中切换到 "Network" 标签
2. 刷新页面
3. 查找 `knowledge-bases` 请求
4. 检查：
   - **URL**: 应该是 `http://localhost:3000/api/knowledge-bases`
   - **Status**: 应该是 `200 OK`
   - **Response**: 应该是 `[]` 或知识库数组

### 步骤 3：检查后端是否运行

确保后端正在运行：

```bash
# 检查后端进程
# 访问：http://localhost:8000/health

# 应该返回：
{
  "status": "healthy",
  "version": "1.1.0",
  "database": "connected"
}
```

### 步骤 4：检查数据库表是否创建

连接数据库并检查：

```sql
-- 检查表是否存在
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('knowledge_bases', 'knowledge_base_documents', 'knowledge_base_chunks');

-- 检查知识库数据
SELECT * FROM knowledge_bases;
```

如果表不存在，运行迁移：

```bash
cd backend
python migrations/run_migration_005.py
```

### 步骤 5：测试 API 直接访问

在浏览器中直接访问（需要先登录）：

```
http://localhost:8000/api/knowledge-bases
```

或使用 API 文档测试：

```
http://localhost:8000/docs
```

找到 `/api/knowledge-bases` 接口，点击 "Try it out" → "Execute"

## 🎯 常见问题解决

### 问题 1：显示 "Not Found"

**原因**：路由配置错误或页面组件未正确导入

**解决**：
1. 检查 `frontend/src/router/routes.tsx` 是否包含知识库路由
2. 检查 `frontend/src/components/Layout/MainLayout.tsx` 是否包含菜单项

### 问题 2：API 返回 404

**原因**：后端路由未注册或 URL 错误

**检查**：
1. 后端 `app/application.py` 是否包含：
   ```python
   self.app.include_router(knowledge_bases.router)
   ```

2. API URL 是否正确（不应该有 `/api/api/`）

### 问题 3：API 返回 401 Unauthorized

**原因**：未登录或 token 过期

**解决**：
1. 重新登录
2. 检查 localStorage 中是否有 token：
   ```javascript
   localStorage.getItem('token')
   ```

### 问题 4：显示空白但无错误

**原因**：CSS 或组件渲染问题

**检查**：
1. 浏览器控制台是否有 React 错误
2. Elements 标签中检查 DOM 是否正确渲染

### 问题 5：后端返回数据库错误

**原因**：数据库表未创建或 pgvector 扩展未启用

**解决**：

```sql
-- 1. 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 运行迁移
cd backend
python migrations/run_migration_005.py

-- 3. 验证表创建
SELECT * FROM knowledge_bases;
```

## 📊 调试检查清单

按顺序检查：

- [ ] 后端服务正在运行 (http://localhost:8000/health)
- [ ] 前端服务正在运行 (http://localhost:5173)
- [ ] 已登录系统（有有效 token）
- [ ] 数据库表已创建（运行过迁移）
- [ ] pgvector 扩展已启用
- [ ] 浏览器控制台无错误
- [ ] Network 请求返回 200
- [ ] API 文档可以正常测试 (/docs)

## 🔧 快速修复命令

```bash
# 1. 重启后端
cd backend
python -m app.main

# 2. 重启前端
cd frontend
npm run dev

# 3. 运行数据库迁移
cd backend
python migrations/run_migration_005.py

# 4. 检查数据库连接
psql -U postgres -d chatai -c "SELECT version();"

# 5. 启用 pgvector
psql -U postgres -d chatai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 🎊 成功标志

当一切正常时，你应该看到：

1. **空状态页面**（如果还没创建知识库）：
   - 显示数据库图标
   - "暂无知识库"提示
   - "点击右上角创建知识库按钮"提示

2. **控制台输出**：
   ```
   ✅ 知识库数据: []
   ```

3. **Network 请求**：
   ```
   GET /api/knowledge-bases
   Status: 200 OK
   Response: []
   ```

## 💡 下一步

如果显示空状态页面，说明一切正常！

1. 点击 "创建知识库" 按钮
2. 填写表单
3. 创建第一个知识库
4. 上传文档测试

## 📞 获取更多帮助

如果以上步骤都无法解决问题：

1. 复制完整的错误信息（控制台 + Network）
2. 检查后端日志输出
3. 查看 `FIXES.md` 中的常见问题
4. 参考 `RAG_FEATURE_GUIDE.md` 完整文档

