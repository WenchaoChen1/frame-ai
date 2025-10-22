# 商品RAG召回测试 - 前端模块

商品RAG召回测试的前端实现，提供完整的用户界面。

## 目录结构

```
product-rag/
├── components/          # 组件目录
│   ├── ProductUpload.tsx       # 文件上传组件
│   ├── ProductList.tsx         # 商品列表组件
│   ├── SearchTest.tsx          # 单次搜索测试
│   ├── BatchSearchTest.tsx     # 批量搜索测试
│   ├── SearchResults.tsx       # 搜索结果展示
│   └── Statistics.tsx          # 统计信息组件
├── pages/              # 页面目录
│   └── ProductRAGManagement.tsx # 主管理页面
├── services/           # 服务目录
│   └── productRagApi.ts        # API调用服务
├── types/              # 类型定义
│   └── index.ts               # TypeScript类型
└── README.md          # 本文件
```

## 功能说明

### 1. 上传管理 (ProductUpload + ProductList)

- **文件上传**：支持拖拽上传 JSON 文件
- **格式验证**：自动验证 JSON 格式
- **进度显示**：实时显示上传进度
- **商品列表**：分页展示已上传的商品
- **自动刷新**：上传成功后自动刷新列表

### 2. 单次测试 (SearchTest)

- **实时搜索**：输入查询词，立即返回结果
- **结果展示**：表格形式展示，包含排名、分数
- **可配置**：支持自定义返回结果数量 (top_k)
- **高亮显示**：高分结果使用不同颜色标识

### 3. 批量测试 (BatchSearchTest)

- **批量输入**：支持多个查询词（每行一个）
- **并行搜索**：后端并行处理多个查询
- **对比展示**：折叠面板展示每个查询的结果
- **统计信息**：显示总耗时和每个查询的耗时

### 4. 统计分析 (Statistics)

- **实时统计**：显示商品总数、向量总数
- **配置信息**：显示使用的索引和模型
- **数据管理**：一键清空所有数据
- **确认对话框**：危险操作需要二次确认

## 使用方式

### 访问页面

1. 登录系统
2. 导航到：系统管理 > 商品RAG测试
3. 或直接访问：`/system/product-rag`

### 上传数据

1. 切换到"上传管理"标签页
2. 拖拽或点击上传 JSON 文件
3. 等待处理完成
4. 查看商品列表

### 测试召回

**单次测试：**
1. 切换到"单次测试"标签页
2. 输入查询词（如：安全帽）
3. 设置返回结果数量
4. 点击搜索查看结果

**批量测试：**
1. 切换到"批量测试"标签页
2. 输入多个查询词（每行一个）
3. 设置返回结果数量
4. 点击批量搜索
5. 展开查看每个查询的结果

### 查看统计

1. 切换到"统计分析"标签页
2. 查看各项统计信息
3. 需要时可以清空所有数据

## 组件 API

### ProductUpload

```tsx
interface ProductUploadProps {
  onUploadSuccess?: () => void;  // 上传成功回调
}
```

### ProductList

```tsx
interface ProductListProps {
  refreshTrigger?: number;  // 刷新触发器
}
```

### SearchResults

```tsx
interface SearchResultsProps {
  results: SearchResult[];  // 搜索结果
  searchTime?: number;      // 搜索耗时
  query?: string;           // 查询词
  loading?: boolean;        // 加载状态
}
```

### Statistics

```tsx
interface StatisticsProps {
  refreshTrigger?: number;   // 刷新触发器
  onDataCleared?: () => void; // 清空数据回调
}
```

## API 服务

### uploadProductFile

```typescript
uploadProductFile(file: File): Promise<any>
```

上传商品 JSON 文件。

### getProducts

```typescript
getProducts(page: number, pageSize: number): Promise<ProductListResponse>
```

获取商品列表（分页）。

### searchProducts

```typescript
searchProducts(request: SearchRequest): Promise<SearchResponse>
```

单次搜索商品。

### batchSearchProducts

```typescript
batchSearchProducts(request: BatchSearchRequest): Promise<BatchSearchResponse>
```

批量搜索商品。

### getStats

```typescript
getStats(): Promise<StatsResponse>
```

获取统计信息。

### clearAllData

```typescript
clearAllData(): Promise<any>
```

清空所有数据。

## 类型定义

详见 `types/index.ts`：

- `Product` - 商品信息
- `ProductListResponse` - 商品列表响应
- `SearchRequest` - 搜索请求
- `SearchResult` - 搜索结果
- `SearchResponse` - 搜索响应
- `BatchSearchRequest` - 批量搜索请求
- `BatchSearchResponse` - 批量搜索响应
- `StatsResponse` - 统计信息响应

## 样式和交互

- 使用 Ant Design 组件库
- 响应式布局，适配不同屏幕
- 加载状态提示
- 错误信息提示
- 成功操作反馈

## 依赖项

- React
- Ant Design
- Axios (通过 api 服务)
- React Router

## 删除模块

如需删除此模块：

1. 删除 `frontend/src/playground/productRag/` 目录
2. 从 `frontend/src/router/routes.tsx` 移除以下代码：
   - 导入语句
   - 路由配置（`product-rag` 路由）
   - 图标导入（`ExperimentOutlined`）

## 开发建议

- 组件保持单一职责
- 使用 TypeScript 类型检查
- 遵循 React Hooks 最佳实践
- 适当的错误处理和用户反馈
- 代码注释清晰

## 故障排查

### 上传失败

- 检查文件格式是否为 JSON
- 检查文件大小是否超过 50MB
- 查看网络请求是否正常
- 检查后端服务是否运行

### 搜索无结果

- 确认已上传商品数据
- 检查查询词是否合适
- 查看后端日志
- 确认 Elasticsearch 正常运行

### 页面报错

- 检查浏览器控制台错误信息
- 确认 API 请求是否成功
- 检查后端服务状态
- 清除浏览器缓存

