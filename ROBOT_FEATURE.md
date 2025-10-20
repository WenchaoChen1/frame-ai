# 机器人管理功能说明

## 功能概述

机器人管理功能允许用户创建和管理AI机器人，每个机器人可以配置默认的AI模型、系统提示词等参数，用于特定场景的对话。

## 主要特性

### 1. 机器人管理
- ✅ 创建、编辑、删除机器人
- ✅ 配置机器人的基本信息（名称、描述、头像）
- ✅ 配置AI参数（默认provider、默认model、系统提示词、温度、最大token数）
- ✅ 支持全局机器人（管理员创建，所有用户可用）和私有机器人（仅创建者可用）

### 2. 机器人卡片式展示
- ✅ 仿照 eSapiens 风格的卡片布局
- ✅ 显示机器人头像、名称、描述、模型信息
- ✅ 筛选功能：全部/全局/我的
- ✅ 快速操作：配置、删除

### 3. 对话集成
- ✅ 点击机器人卡片查看该机器人的对话历史
- ✅ 创建新对话时可关联机器人
- ✅ 对话自动使用机器人的默认配置
- ✅ 聊天界面显示当前使用的机器人信息

## 使用方式

### 作为普通用户

1. **访问机器人管理**
   - 登录系统后，点击侧边栏「系统管理」→「机器人管理」

2. **查看可用机器人**
   - 页面显示所有全局机器人和你创建的私有机器人
   - 使用筛选器切换显示：全部/全局/我的

3. **创建私有机器人**
   - 点击右上角「新建机器人」按钮
   - 填写机器人信息：
     - 名称：机器人的显示名称
     - 头像：选择一个emoji作为头像
     - 描述：简要描述机器人的功能
     - 系统提示词：定义机器人的角色和行为（例如："你是一个Python编程专家..."）
     - 默认提供商和模型：选择AI服务商和模型
     - 温度：控制回复的随机性（0-2，默认0.7）
     - 最大Token数：限制回复长度（可选）
   - 点击保存

4. **使用机器人对话**
   - **方式一**：点击机器人卡片，查看该机器人的对话历史，点击「新建对话」
   - **方式二**：在对话历史页面，点击具体对话进入聊天

5. **管理机器人**
   - 编辑：点击机器人卡片上的「配置」按钮
   - 删除：点击机器人卡片上的「删除」按钮

### 作为管理员

管理员除了普通用户的所有功能外，还可以：

1. **创建全局机器人**
   - 在创建机器人时，选择「全局机器人」选项
   - 全局机器人对所有用户可见和可用

2. **管理所有机器人**
   - 可以编辑和删除任何用户创建的机器人
   - 可以将私有机器人设置为全局机器人

## 技术实现

### 后端

#### 新增文件
- `backend/app/models/robot.py` - 机器人数据模型
- `backend/app/schemas/robot.py` - 机器人Schema定义
- `backend/app/routers/robots.py` - 机器人API路由

#### 修改文件
- `backend/app/models/conversation.py` - 添加robot_id字段
- `backend/app/schemas/conversation.py` - 添加robot_id字段
- `backend/app/routers/conversations.py` - 创建对话时验证机器人
- `backend/app/application.py` - 注册机器人路由
- `backend/app/models/__init__.py` - 导出Robot模型
- `backend/app/schemas/__init__.py` - 导出Robot Schema

#### API端点
```
GET    /api/robots                        - 获取机器人列表
POST   /api/robots                        - 创建机器人
GET    /api/robots/{robot_id}             - 获取机器人详情
PUT    /api/robots/{robot_id}             - 更新机器人
DELETE /api/robots/{robot_id}             - 删除机器人
GET    /api/robots/{robot_id}/conversations - 获取机器人的对话列表
```

### 前端

#### 新增文件
- `frontend/src/services/robot.ts` - 机器人服务层
- `frontend/src/pages/RobotManagement.tsx` - 机器人管理页面
- `frontend/src/pages/RobotConversations.tsx` - 机器人对话列表页面

#### 修改文件
- `frontend/src/router/routes.tsx` - 添加机器人相关路由
- `frontend/src/services/conversation.ts` - 支持robot_id
- `frontend/src/components/Chat/ChatWindowX.tsx` - 显示机器人信息，使用机器人默认配置
- `frontend/src/pages/ChatPage.tsx` - 支持从robot_id创建对话

#### 路由
```
/system/robots                       - 机器人管理页面
/robots/:robotId/conversations       - 机器人对话列表页面
/chat?robot_id=:robotId             - 创建与机器人的新对话
/chat/:conversationId               - 进入具体对话
```

## 数据库变更

### 新增表：robots
```sql
CREATE TABLE robots (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    avatar VARCHAR,
    default_provider VARCHAR NOT NULL,
    default_model VARCHAR NOT NULL,
    system_prompt TEXT,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER,
    is_global BOOLEAN NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 更新表：conversations
```sql
ALTER TABLE conversations ADD COLUMN robot_id INTEGER;
```

详细迁移说明请参考 `backend/ROBOT_MIGRATION.md`

## 使用场景示例

### 场景1：Python编程助手
```
名称：Python编程助手
头像：🐍
描述：专业的Python编程顾问，帮助解决编程问题
系统提示词：你是一个专业的Python编程专家。你精通Python语言的各个方面，包括语法、标准库、第三方库、最佳实践等。你会用清晰、简洁的方式回答问题，并提供可运行的代码示例。
默认模型：openai / gpt-4
```

### 场景2：英语翻译助手
```
名称：英语翻译助手
头像：🌍
描述：中英互译，提供准确流畅的翻译
系统提示词：你是一个专业的翻译助手，精通中文和英文。你的任务是提供准确、流畅、符合语境的翻译。翻译时要注意保持原文的语气和风格。
默认模型：openai / gpt-3.5-turbo
温度：0.3（较低温度保证翻译稳定）
```

### 场景3：创意写作助手
```
名称：创意写作助手
头像：✍️
描述：激发创意，帮助撰写各类文案
系统提示词：你是一个富有创意的写作助手。你擅长各种文体的创作，包括故事、诗歌、广告文案等。你的回复要有想象力、有感染力，能够激发读者的共鸣。
默认模型：claude / claude-3-opus
温度：0.9（较高温度增加创意性）
```

## 注意事项

1. **权限控制**
   - 全局机器人只能由管理员创建
   - 用户只能编辑和删除自己创建的机器人
   - 管理员可以管理所有机器人

2. **对话关联**
   - 一个对话可以关联一个机器人
   - 对话创建后，机器人关联不可修改
   - 删除机器人不会删除相关对话（对话的robot_id会保留）

3. **默认配置**
   - 机器人的默认配置仅在对话开始时使用
   - 对话过程中用户仍可手动切换模型
   - 系统提示词会在发送给AI时自动添加到上下文中

4. **性能考虑**
   - 建议为常用场景创建专门的机器人
   - 避免创建过多相似的机器人
   - 系统提示词不宜过长（建议500字以内）

## 未来扩展

可能的功能扩展方向：

1. 机器人模板市场
2. 机器人分享功能
3. 机器人使用统计
4. 更复杂的提示词工程（多轮对话模板）
5. 机器人分类和标签
6. 机器人评分和评论
7. 支持上传自定义图片作为头像

## 故障排查

### 问题1：无法创建机器人
- 检查是否选择了有效的provider和model
- 确认provider是否已正确配置（环境变量中的API密钥）

### 问题2：对话没有使用机器人的默认配置
- 检查对话是否正确关联了机器人（查看robot_id）
- 刷新页面重新加载机器人信息

### 问题3：无法创建全局机器人
- 确认当前用户是否为管理员角色
- 检查后端日志是否有权限错误

## 反馈与支持

如有问题或建议，请联系开发团队或提交Issue。

