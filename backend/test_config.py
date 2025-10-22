"""
测试配置读取优先级
检查是从 config.py 默认值读取还是从 .env 文件读取
"""
import os
from pathlib import Path

# 显示当前工作目录
print("=" * 60)
print("📂 当前工作目录:", os.getcwd())
print("=" * 60)

# 检查 .env 文件是否存在
env_file = Path(__file__).parent / ".env"
print(f"\n🔍 检查 .env 文件: {env_file}")
print(f"   存在: {env_file.exists()}")

if env_file.exists():
    print(f"\n📄 .env 文件内容（前20行）:")
    print("-" * 60)
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:20]
        for i, line in enumerate(lines, 1):
            # 隐藏敏感信息
            if any(key in line for key in ['API_KEY', 'PASSWORD', 'SECRET']):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0]
                    value = parts[1].strip()
                    if value:
                        masked_value = value[:10] + "..." if len(value) > 10 else "***"
                        print(f"{i:2d}: {key}={masked_value}")
                    else:
                        print(f"{i:2d}: {line.rstrip()}")
                else:
                    print(f"{i:2d}: {line.rstrip()}")
            else:
                print(f"{i:2d}: {line.rstrip()}")
else:
    print("   ⚠️  .env 文件不存在，将使用 config.py 中的默认值")

# 导入配置
print("\n" + "=" * 60)
print("📥 导入配置模块...")
print("=" * 60)

from app.core.config import settings

# 关键配置项
configs = {
    "Elasticsearch": {
        "ELASTICSEARCH_URL": settings.ELASTICSEARCH_URL,
        "ELASTICSEARCH_API_KEY": settings.ELASTICSEARCH_API_KEY,
        "ELASTICSEARCH_USERNAME": settings.ELASTICSEARCH_USERNAME,
        "ELASTICSEARCH_PASSWORD": settings.ELASTICSEARCH_PASSWORD,
    },
    "OpenAI": {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
    },
    "Database": {
        "DATABASE_URL": settings.DATABASE_URL,
    },
}

# 显示配置值
print("\n📊 当前配置值:")
print("=" * 60)

for category, items in configs.items():
    print(f"\n【{category}】")
    for key, value in items.items():
        # 检查是否为空
        is_empty = not value or value == ""
        
        # 隐藏敏感信息
        if any(keyword in key for keyword in ['KEY', 'PASSWORD', 'SECRET']):
            if is_empty:
                display_value = "❌ 未配置 (空值)"
            else:
                display_value = f"✅ 已配置 ({value[:15]}...)" if len(value) > 15 else f"✅ 已配置 ({value}...)"
        else:
            display_value = value if not is_empty else "❌ 未配置 (空值)"
        
        print(f"  • {key}: {display_value}")

# 判断配置来源
print("\n" + "=" * 60)
print("🔍 配置来源分析:")
print("=" * 60)

# 读取 config.py 中的默认值
print("\n从 config.py 源码读取默认值:")
config_file = Path(__file__).parent / "app" / "core" / "config.py"
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 提取默认值
    import re
    defaults = {}
    patterns = [
        (r'ELASTICSEARCH_URL:\s*str\s*=\s*["\']([^"\']*)["\']', 'ELASTICSEARCH_URL'),
        (r'ELASTICSEARCH_API_KEY:\s*str\s*=\s*["\']([^"\']*)["\']', 'ELASTICSEARCH_API_KEY'),
        (r'ELASTICSEARCH_USERNAME:\s*str\s*=\s*["\']([^"\']*)["\']', 'ELASTICSEARCH_USERNAME'),
        (r'OPENAI_API_KEY:\s*str\s*=\s*["\']([^"\']*)["\']', 'OPENAI_API_KEY'),
    ]
    
    for pattern, key in patterns:
        match = re.search(pattern, content)
        if match:
            defaults[key] = match.group(1)
    
    print("\nconfig.py 默认值:")
    for key, default_value in defaults.items():
        current_value = getattr(settings, key, None)
        
        # 比较
        if not default_value:
            default_display = "空字符串"
        elif any(keyword in key for keyword in ['KEY', 'PASSWORD']):
            default_display = f"{default_value[:15]}..." if len(default_value) > 15 else f"{default_value}..."
        else:
            default_display = default_value
            
        # 判断是否被覆盖
        if current_value == default_value:
            status = "📌 使用默认值"
            source = "config.py"
        elif not current_value and not default_value:
            status = "📌 都为空"
            source = "config.py"
        else:
            status = "🔄 已被 .env 覆盖"
            source = ".env 文件"
        
        print(f"  • {key}:")
        print(f"      默认值: {default_display}")
        print(f"      当前值: {current_value[:15] + '...' if current_value and len(str(current_value)) > 15 else current_value or '空'}")
        print(f"      状态: {status}")
        print(f"      来源: {source}")
        print()

# 结论
print("=" * 60)
print("📝 结论:")
print("=" * 60)

if env_file.exists():
    print("""
✅ .env 文件存在

配置读取优先级:
  1️⃣  首先读取 .env 文件中的配置
  2️⃣  如果 .env 中没有，则使用 config.py 中的默认值
  3️⃣  也可以通过环境变量覆盖（优先级最高）

建议:
  • 敏感信息（API Key、密码）应该放在 .env 文件中
  • config.py 中只保留默认值和类型定义
  • .env 文件不要提交到 Git（已加入 .gitignore）
""")
else:
    print("""
⚠️  .env 文件不存在

当前使用 config.py 中的默认值

建议:
  1. 复制 .env.example 为 .env
     cp .env.example .env
  
  2. 修改 .env 文件中的配置
  
  3. 重启服务
""")

# 测试 Elasticsearch 连接可行性
print("\n" + "=" * 60)
print("🔌 Elasticsearch 连接配置检查:")
print("=" * 60)

has_api_key = bool(settings.ELASTICSEARCH_API_KEY)
has_username = bool(settings.ELASTICSEARCH_USERNAME)
has_password = bool(settings.ELASTICSEARCH_PASSWORD)

print(f"\nURL: {settings.ELASTICSEARCH_URL}")
print(f"API Key: {'✅ 已配置' if has_api_key else '❌ 未配置'}")
print(f"用户名: {'✅ 已配置' if has_username else '❌ 未配置'}")
print(f"密码: {'✅ 已配置' if has_password else '❌ 未配置'}")

if has_api_key:
    print("\n认证方式: API Key ✅")
elif has_username and has_password:
    print("\n认证方式: 用户名密码 ✅")
else:
    print("\n认证方式: 无认证 ⚠️")
    print("警告: 如果 Elasticsearch 启用了安全认证，连接将失败！")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)

