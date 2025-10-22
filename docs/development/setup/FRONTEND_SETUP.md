# 前端知识库功能使用指南

## 🎯 访问路径

知识库管理页面已添加到前端，访问路径：

**侧边栏导航**：
```
系统管理 → 知识库管理
```

**直接 URL**：
```
http://localhost:5173/system/knowledge-bases
```

## 📋 功能说明

### 1. 知识库列表

在知识库管理页面可以看到：
- 所有你创建的知识库
- 公开的知识库
- 每个知识库的统计信息（文档数、块数）
- 向量存储类型和嵌入模型

### 2. 创建知识库

点击**创建知识库**按钮，填写：
- **名称**：知识库名称（必填）
- **描述**：简短描述
- **向量存储**：选择 pgvector 或 Elasticsearch
- **嵌入模型**：
  - OpenAI Small（推荐，速度快）
  - OpenAI Large（高精度）
  - HuggingFace BGE（离线可用）
- **块大小**：500（默认）
- **块重叠**：50（默认）

### 3. 上传文档

在知识库卡片上点击**上传文档**：
- 支持格式：TXT, PDF, DOCX
- 最大大小：50MB
- 上传后自动解析和向量化
- 可以查看处理状态

### 4. 查看文档

点击**查看文档**可以看到：
- 文档列表
- 处理状态（处理中、完成、失败）
- 文件大小和块数量
- 删除文档

### 5. 关联到机器人

在机器人管理页面：
1. 选择一个机器人
2. 在机器人详情中关联知识库（功能正在完善）

或使用 API：
```bash
POST /api/robots/{robot_id}/knowledge-bases
{
  "knowledge_base_ids": [1, 2, 3]
}
```

## 🎨 界面预览

### 知识库列表
- 卡片式展示
- 显示向量存储类型、嵌入模型
- 文档和块的统计数字
- 操作按钮（上传、查看、删除）

### 文档管理
- 列表式展示
- 状态标签（彩色）
- 文件大小和块数
- 删除操作

## 🔧 开发说明

### 已创建的文件

1. **API Service**
   - `frontend/src/services/knowledgeBase.ts`
   - 包含所有知识库相关的 API 调用

2. **管理页面**
   - `frontend/src/pages/KnowledgeBaseManagement.tsx`
   - Material-UI 组件
   - 响应式布局

3. **路由配置**
   - `frontend/src/router/routes.tsx`
   - 已添加到系统管理菜单

### 扩展功能（可选）

如果需要在机器人管理中添加知识库关联：

1. 修改 `RobotDetailModal` 组件
2. 添加知识库选择器
3. 调用 `associateKnowledgeBases` API

示例代码：
```typescript
import { 
  associateKnowledgeBases, 
  getKnowledgeBases 
} from '../services/knowledgeBase';

// 在机器人详情中
const handleAssociateKB = async (robotId: number, kbIds: number[]) => {
  try {
    await associateKnowledgeBases(robotId, kbIds);
    message.success('关联成功');
  } catch (error) {
    message.error('关联失败');
  }
};
```

## 🚀 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 📝 注意事项

1. **后端必须先启动**
   - 确保后端运行在 http://localhost:8000
   - 检查 API 连接是否正常

2. **登录后才能访问**
   - 知识库管理需要登录
   - 位于系统管理菜单下

3. **权限控制**
   - 只能看到自己创建的知识库
   - 可以看到公开的知识库
   - 删除操作仅限自己的知识库

4. **文档处理时间**
   - 小文件（< 1MB）：几秒
   - 大文件（> 10MB）：可能需要几分钟
   - 状态会实时更新

## 🎊 使用流程

完整的 RAG 使用流程：

```
1. 登录系统
   ↓
2. 进入"系统管理" → "知识库管理"
   ↓
3. 创建一个新知识库
   ↓
4. 上传文档（TXT/PDF/DOCX）
   ↓
5. 等待文档处理完成
   ↓
6. 进入"机器人管理"
   ↓
7. 关联知识库到机器人（使用 API 或等待 UI 完善）
   ↓
8. 在聊天页面选择该机器人
   ↓
9. 开始 RAG 对话！
```

## 💡 提示

- 第一次使用建议上传小的 TXT 文件测试
- 查看文档列表确认处理状态
- 如果处理失败，查看错误信息
- 可以删除后重新上传

## 🆘 故障排除

**问题：页面不显示**
- 检查前端是否启动
- 检查路由配置是否正确
- 清除浏览器缓存

**问题：上传失败**
- 检查文件格式是否支持
- 检查文件大小（< 50MB）
- 检查后端日志

**问题：看不到知识库**
- 确认已登录
- 确认有创建的知识库
- 刷新页面

---

**现在可以在前端完整使用 RAG 功能了！** 🎉

