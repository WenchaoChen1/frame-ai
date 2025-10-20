# API接口文档

本文档详细描述了AI聊天系统的所有API接口。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 认证接口

### 1. 用户注册

**POST** `/auth/register`

创建新用户账号。

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 2. 用户登录

**POST** `/auth/login`

用户登录获取访问令牌。

**请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 3. 获取当前用户信息

**GET** `/auth/me`

获取当前登录用户的信息。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

## 会话管理接口

### 1. 获取会话列表

**GET** `/conversations`

获取当前用户的所有会话。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "新对话",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:10:00"
  }
]
```

### 2. 创建新会话

**POST** `/conversations`

创建新的对话会话。

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "title": "我的新对话"
}
```

**响应**:
```json
{
  "id": 2,
  "user_id": 1,
  "title": "我的新对话",
  "created_at": "2024-01-01T00:15:00",
  "updated_at": "2024-01-01T00:15:00",
  "messages": []
}
```

### 3. 获取会话详情

**GET** `/conversations/{conversation_id}`

获取指定会话及其所有消息。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "新对话",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:10:00",
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "role": "user",
      "content": "你好",
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "created_at": "2024-01-01T00:05:00"
    },
    {
      "id": 2,
      "conversation_id": 1,
      "role": "assistant",
      "content": "你好！有什么我可以帮助你的吗？",
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "created_at": "2024-01-01T00:05:02"
    }
  ]
}
```

### 4. 删除会话

**DELETE** `/conversations/{conversation_id}`

删除指定会话及其所有消息。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "会话已删除"
}
```

### 5. 更新会话标题

**PATCH** `/conversations/{conversation_id}/title?title=新标题`

更新会话的标题。

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `title`: 新的会话标题

**响应**:
```json
{
  "message": "标题已更新",
  "title": "新标题"
}
```

## 消息接口

### 1. 获取消息列表

**GET** `/conversations/{conversation_id}/messages`

获取指定会话的所有消息。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "你好",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "created_at": "2024-01-01T00:05:00"
  }
]
```

### 2. 发送消息（流式）

**POST** `/conversations/{conversation_id}/messages/stream`

发送消息并接收AI的流式响应。

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "content": "介绍一下人工智能",
  "provider": "openai",
  "model": "gpt-3.5-turbo"
}
```

**响应** (Server-Sent Events):

流式响应使用SSE (Server-Sent Events)格式：

```
data: {"type": "user_message", "data": {...}}

data: {"type": "content", "data": "人工"}

data: {"type": "content", "data": "智能"}

data: {"type": "content", "data": "（AI）"}

data: {"type": "done", "data": {...}}
```

事件类型：
- `user_message`: 用户消息已保存
- `content`: AI响应的内容片段
- `done`: AI响应完成，包含完整消息对象
- `error`: 发生错误

## AI提供商接口

### 1. 获取可用提供商

**GET** `/providers`

获取所有可用的AI提供商和模型列表。

**响应**:
```json
{
  "providers": [
    {
      "name": "openai",
      "models": [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-mini"
      ]
    },
    {
      "name": "claude",
      "models": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022"
      ]
    },
    {
      "name": "ollama",
      "models": [
        "llama2",
        "llama3",
        "mistral",
        "mixtral",
        "codellama"
      ]
    }
  ]
}
```

## 错误响应

所有接口在发生错误时返回标准错误格式：

```json
{
  "detail": "错误描述信息"
}
```

常见HTTP状态码：
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权或token无效
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 认证流程

1. 用户注册或登录获取 `access_token`
2. 在后续请求中，在请求头中添加：
   ```
   Authorization: Bearer <access_token>
   ```
3. Token默认有效期为7天
4. Token过期后需要重新登录

## 使用示例

### JavaScript / Fetch

```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});

const { access_token } = await loginResponse.json();

// 获取会话列表
const conversationsResponse = await fetch('http://localhost:8000/api/conversations', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const conversations = await conversationsResponse.json();
```

### Python / requests

```python
import requests

# 登录
login_response = requests.post('http://localhost:8000/api/auth/login', json={
    'username': 'testuser',
    'password': 'password123'
})

access_token = login_response.json()['access_token']

# 获取会话列表
headers = {'Authorization': f'Bearer {access_token}'}
conversations_response = requests.get(
    'http://localhost:8000/api/conversations',
    headers=headers
)

conversations = conversations_response.json()
```

### cURL

```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 获取会话列表
curl -X GET http://localhost:8000/api/conversations \
  -H "Authorization: Bearer <access_token>"
```

## 流式响应处理

前端处理SSE流式响应的示例：

```javascript
const response = await fetch('/api/conversations/1/messages/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    content: '你好',
    provider: 'openai',
    model: 'gpt-3.5-turbo'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      if (data.type === 'content') {
        // 处理内容片段
        console.log(data.data);
      } else if (data.type === 'done') {
        // 响应完成
        console.log('完成', data.data);
      } else if (data.type === 'error') {
        // 错误处理
        console.error('错误', data.data);
      }
    }
  }
}
```

## 限流和配额

当前版本暂无API限流，生产环境建议实施以下限制：

- 登录失败：5次/分钟
- 消息发送：20次/分钟
- 会话创建：10次/分钟
- 其他接口：100次/分钟

## 更多信息

- 交互式API文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

