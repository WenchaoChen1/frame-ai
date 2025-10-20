# 贡献指南

感谢你对本项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告Bug

如果你发现了Bug，请创建一个Issue，并包含以下信息：

1. **Bug描述**：清晰简洁地描述问题
2. **复现步骤**：如何复现这个问题
3. **期望行为**：你期望发生什么
4. **实际行为**：实际发生了什么
5. **环境信息**：
   - 操作系统（Windows/Linux/Mac）
   - Docker版本
   - 浏览器版本
6. **截图**：如果可能，提供截图

### 提出新功能

如果你有好的想法，请创建一个Issue：

1. **功能描述**：描述你想要的功能
2. **使用场景**：为什么需要这个功能
3. **建议实现**：如果有想法，可以描述实现方式

### 提交代码

#### 开发环境设置

1. Fork本项目
2. 克隆你的Fork
```bash
git clone https://github.com/your-username/fangying-ai.git
cd fangying-ai
```

3. 创建新分支
```bash
git checkout -b feature/your-feature-name
```

4. 设置开发环境

**后端**：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**前端**：
```bash
cd frontend
npm install
```

#### 开发规范

**代码风格**：

- **Python**：遵循PEP 8规范
- **TypeScript/React**：使用ESLint和Prettier
- **提交信息**：使用清晰的提交信息

**提交信息格式**：
```
类型: 简短描述

详细描述（可选）

类型可以是：
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具链更新
```

示例：
```
feat: 添加会话搜索功能

- 添加搜索框组件
- 实现搜索API
- 添加搜索结果高亮
```

#### 测试

在提交PR之前，请确保：

1. 代码可以正常运行
2. 没有引入新的错误
3. 格式符合规范

```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm test
```

#### 提交Pull Request

1. 推送你的分支
```bash
git push origin feature/your-feature-name
```

2. 在GitHub上创建Pull Request
3. 填写PR模板，描述你的改动
4. 等待代码审查

**PR标题格式**：
```
[类型] 简短描述
```

示例：
```
[Feature] 添加会话搜索功能
[Fix] 修复消息流式显示问题
[Docs] 更新API文档
```

**PR描述应包含**：
- 改动说明
- 相关Issue编号（如果有）
- 测试说明
- 截图（如果是UI改动）

## 代码审查流程

1. 提交PR后，维护者会进行代码审查
2. 如有需要修改的地方，会在PR中评论
3. 修改完成后，更新PR
4. 审查通过后，PR会被合并

## 开发指南

### 项目结构

```
fangying-ai/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── routers/     # API路由
│   │   ├── schemas/     # Pydantic模式
│   │   └── services/    # 业务逻辑
│   └── tests/           # 后端测试
└── frontend/            # 前端代码
    ├── src/
    │   ├── components/  # React组件
    │   ├── services/    # API服务
    │   └── store/       # 状态管理
    └── tests/           # 前端测试
```

### 添加新的AI提供商

1. 在 `backend/app/services/` 创建新服务类
2. 继承 `AIProvider` 基类
3. 实现 `chat_stream` 和 `get_available_models` 方法
4. 在 `ai_manager.py` 中注册新提供商
5. 添加配置项到 `config.py`
6. 更新文档

示例：
```python
# backend/app/services/new_provider_service.py
from typing import AsyncGenerator, List, Dict
from .ai_provider import AIProvider

class NewProviderService(AIProvider):
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        # 实现流式响应
        pass
    
    def get_available_models(self) -> List[str]:
        return ["model-1", "model-2"]
```

### 添加新的前端组件

1. 在 `frontend/src/components/` 相应目录创建组件
2. 使用TypeScript类型定义
3. 遵循Ant Design设计规范
4. 添加适当的错误处理
5. 考虑响应式设计

### 数据库迁移

使用Alembic管理数据库迁移：

```bash
# 创建迁移
cd backend
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```

## 社区准则

### 行为准则

- 尊重他人
- 接受建设性批评
- 专注于对项目最有利的事情
- 对新手友好

### 沟通

- Issue和PR使用中文
- 代码注释使用中文
- 文档使用中文

## 获取帮助

- 查看 [文档](./README.md)
- 在Issue中提问
- 加入讨论

## 许可证

贡献的代码将采用MIT许可证。

再次感谢你的贡献！🎉

