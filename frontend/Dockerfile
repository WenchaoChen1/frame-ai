# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json ./

# 安装依赖（使用 npm ci 更快且更可靠）
RUN npm ci

# 复制源代码
COPY . .

# 构建时环境变量（可以在构建时通过 --build-arg 传递）
ARG VITE_API_URL=""
ARG VITE_PORT=9101
ARG VITE_HOST=0.0.0.0

# 设置环境变量供 Vite 使用
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_PORT=$VITE_PORT
ENV VITE_HOST=$VITE_HOST

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 创建非 root 用户（可选）
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

CMD ["nginx", "-g", "daemon off;"]

