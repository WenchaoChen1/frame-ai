# Elasticsearch 认证配置指南

## 问题说明

如果遇到以下错误：
```
elasticsearch.AuthenticationException: AuthenticationException(401, 'security_exception', 
'unable to authenticate with provided credentials and anonymous access is not allowed for this request')
```

说明 Elasticsearch 认证配置不正确。

## 解决方案

### 方案一：使用 API Key 认证（推荐）

1. **生成 API Key**（在 Kibana 中）:
   ```
   Stack Management -> Security -> API Keys -> Create API key
   ```
   
2. **配置 `.env` 文件**:
   ```bash
   ELASTICSEARCH_URL=http://localhost:9200
   ELASTICSEARCH_API_KEY=你的API_Key
   ELASTICSEARCH_USERNAME=
   ELASTICSEARCH_PASSWORD=
   ```

### 方案二：使用用户名密码认证

1. **获取 Elasticsearch 密码**:
   
   如果是首次安装，密码通常在启动日志中：
   ```bash
   # 查看密码
   docker logs elasticsearch 2>&1 | grep "Password for the elastic user"
   ```
   
   或重置密码：
   ```bash
   docker exec -it elasticsearch \
     /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
   ```

2. **配置 `.env` 文件**:
   ```bash
   ELASTICSEARCH_URL=http://localhost:9200
   ELASTICSEARCH_API_KEY=
   ELASTICSEARCH_USERNAME=elastic
   ELASTICSEARCH_PASSWORD=你的密码
   ```

### 方案三：禁用 Elasticsearch 安全认证（仅开发环境）

1. **修改 `docker-compose.yml`**:
   ```yaml
   elasticsearch:
     environment:
       - xpack.security.enabled=false  # 禁用安全认证
   ```

2. **重启服务**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **配置 `.env` 文件**:
   ```bash
   ELASTICSEARCH_URL=http://localhost:9200
   ELASTICSEARCH_API_KEY=
   ELASTICSEARCH_USERNAME=
   ELASTICSEARCH_PASSWORD=
   ```

## 验证配置

### 1. 测试连接

```bash
# 使用 curl 测试（无认证）
curl http://localhost:9200

# 使用用户名密码
curl -u elastic:你的密码 http://localhost:9200

# 使用 API Key
curl -H "Authorization: ApiKey 你的API_Key" http://localhost:9200
```

### 2. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload
```

如果看到以下日志，说明配置成功：
```
✅ ElasticsearchStore 初始化成功
```

## 推荐配置（Docker）

如果使用 Docker 部署 Elasticsearch，推荐以下配置：

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=your_password_here  # 设置密码
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  es_data:
    driver: local
```

然后在 `.env` 中配置：
```bash
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password_here
```

## 常见问题

### Q1: API Key 格式不正确？

API Key 应该是 base64 编码的字符串，类似：
```
VnVhQ2ZHY0JDZGJrU...
```

### Q2: 如何检查当前 ES 是否启用了安全认证？

```bash
curl http://localhost:9200/_cluster/health
```

- 如果返回 `401`，说明启用了安全认证
- 如果返回 JSON 数据，说明未启用安全认证

### Q3: 延迟初始化是什么意思？

系统现在使用**延迟初始化**，即：
- 启动时不会立即连接 Elasticsearch
- 只有在第一次使用（上传或搜索）时才会连接
- 如果连接失败，会显示详细的错误信息

这样可以避免因 ES 配置问题导致整个服务无法启动。

