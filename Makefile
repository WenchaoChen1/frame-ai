# Makefile for ChatAI Project
# 使用 Make 命令简化 Docker 操作

.PHONY: help build up down restart logs clean ps

# 默认目标
help:
	@echo "ChatAI Docker 管理命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make build          - 构建所有 Docker 镜像"
	@echo "  make up             - 启动所有服务"
	@echo "  make up-full        - 启动所有服务（包括 Elasticsearch）"
	@echo "  make down           - 停止所有服务"
	@echo "  make restart        - 重启所有服务"
	@echo "  make logs           - 查看所有服务日志"
	@echo "  make logs-backend   - 查看后端日志"
	@echo "  make logs-frontend  - 查看前端日志"
	@echo "  make logs-db        - 查看数据库日志"
	@echo "  make ps             - 查看服务状态"
	@echo "  make clean          - 停止服务并删除数据卷"
	@echo "  make shell-backend  - 进入后端容器"
	@echo "  make shell-frontend - 进入前端容器"
	@echo "  make shell-db       - 进入数据库容器"
	@echo "  make db-backup      - 备份数据库"
	@echo "  make db-restore     - 恢复数据库"
	@echo "  make dev            - 启动开发环境"
	@echo ""

# 构建镜像
build:
	docker-compose build

# 构建镜像（不使用缓存）
build-no-cache:
	docker-compose build --no-cache

# 启动服务
up:
	docker-compose up -d

# 启动所有服务（包括 Elasticsearch）
up-full:
	docker-compose --profile full up -d

# 停止服务
down:
	docker-compose down

# 重启服务
restart:
	docker-compose restart

# 查看日志
logs:
	docker-compose logs -f

# 查看后端日志
logs-backend:
	docker-compose logs -f backend

# 查看前端日志
logs-frontend:
	docker-compose logs -f frontend

# 查看数据库日志
logs-db:
	docker-compose logs -f db

# 查看服务状态
ps:
	docker-compose ps

# 停止服务并删除数据卷
clean:
	docker-compose down -v
	docker system prune -f

# 进入后端容器
shell-backend:
	docker-compose exec backend bash

# 进入前端容器
shell-frontend:
	docker-compose exec frontend sh

# 进入数据库容器
shell-db:
	docker-compose exec db psql -U postgres -d chatai

# 备份数据库
db-backup:
	@echo "备份数据库..."
	docker-compose exec -T db pg_dump -U postgres chatai > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "备份完成！"

# 恢复数据库（需要提供备份文件）
db-restore:
	@if [ -z "$(FILE)" ]; then \
		echo "请指定备份文件: make db-restore FILE=backup.sql"; \
		exit 1; \
	fi
	@echo "恢复数据库..."
	docker-compose exec -T db psql -U postgres chatai < $(FILE)
	@echo "恢复完成！"

# 启动开发环境
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "开发环境已启动！"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"

# 停止开发环境
dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# 重新构建并启动
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# 查看资源使用情况
stats:
	docker stats --no-stream

# 清理未使用的 Docker 资源
prune:
	docker system prune -af
	docker volume prune -f

# 健康检查
health:
	@echo "检查服务健康状态..."
	@echo "\n后端服务:"
	@curl -s http://localhost:8000/api/health || echo "后端服务不可用"
	@echo "\n\n前端服务:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost || echo "前端服务不可用"
	@echo "\n\n数据库服务:"
	@docker-compose exec db pg_isready -U postgres || echo "数据库服务不可用"
	@echo "\n"

