"""
快速检查模型注册中心的导入是否正常
"""
import sys

print("🔍 检查模型注册中心导入...")
print("=" * 60)

# 检查 1: 基础导入
print("\n1️⃣ 检查基础导入...")
try:
    from app.ai.models import AIProvider, ModelType, ChatModel, EmbeddingModel
    print("   ✅ 枚举导入成功")
except ImportError as e:
    print(f"   ❌ 枚举导入失败: {e}")
    sys.exit(1)

# 检查 2: 元数据类
print("\n2️⃣ 检查元数据类...")
try:
    from app.ai.models import ModelMetadata
    print("   ✅ ModelMetadata 导入成功")
except ImportError as e:
    print(f"   ❌ ModelMetadata 导入失败: {e}")
    sys.exit(1)

# 检查 3: 工具函数
print("\n3️⃣ 检查工具函数...")
try:
    from app.ai.models import (
        get_chat_model_metadata,
        get_embedding_model_metadata,
        get_provider_chat_models,
        get_provider_embedding_models,
        get_all_chat_models,
        get_all_embedding_models,
        get_model_provider,
        is_model_available,
    )
    print("   ✅ 工具函数导入成功")
except ImportError as e:
    print(f"   ❌ 工具函数导入失败: {e}")
    sys.exit(1)

# 检查 4: 向后兼容
print("\n4️⃣ 检查向后兼容...")
try:
    from app.ai.models import EmbeddingProvider, MODEL_DIMENSIONS
    assert EmbeddingProvider == AIProvider
    print("   ✅ 向后兼容别名有效")
except (ImportError, AssertionError) as e:
    print(f"   ❌ 向后兼容检查失败: {e}")
    sys.exit(1)

# 检查 5: 注册表
print("\n5️⃣ 检查模型注册表...")
try:
    from app.ai.models import PROVIDER_CHAT_MODELS, PROVIDER_EMBEDDING_MODELS
    print(f"   - 对话模型服务商数量: {len(PROVIDER_CHAT_MODELS)}")
    print(f"   - 嵌入模型服务商数量: {len(PROVIDER_EMBEDDING_MODELS)}")
    print("   ✅ 模型注册表导入成功")
except ImportError as e:
    print(f"   ❌ 模型注册表导入失败: {e}")
    sys.exit(1)

# 检查 6: 测试功能
print("\n6️⃣ 测试基本功能...")
try:
    model = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
    metadata = get_embedding_model_metadata(model)
    print(f"   - 模型: {model.value}")
    print(f"   - 名称: {metadata.name}")
    print(f"   - 维度: {metadata.dimensions}")
    provider = get_model_provider(model)
    print(f"   - 服务商: {provider.value}")
    print("   ✅ 功能测试通过")
except Exception as e:
    print(f"   ❌ 功能测试失败: {e}")
    sys.exit(1)

# 检查 7: EmbeddingService
print("\n7️⃣ 检查 EmbeddingService...")
try:
    from app.services.embedding_service import EmbeddingService
    print("   ✅ EmbeddingService 导入成功")
except ImportError as e:
    print(f"   ❌ EmbeddingService 导入失败: {e}")
    sys.exit(1)

# 检查 8: knowledge_base 模型
print("\n8️⃣ 检查 knowledge_base 模型...")
try:
    from app.models.knowledge_base import KnowledgeBase
    print("   ✅ KnowledgeBase 模型导入成功")
except ImportError as e:
    print(f"   ❌ KnowledgeBase 模型导入失败: {e}")
    sys.exit(1)

# 检查 9: schemas
print("\n9️⃣ 检查 schemas...")
try:
    from app.schemas.knowledge_base import KnowledgeBaseCreate
    print("   ✅ schemas 导入成功")
except ImportError as e:
    print(f"   ❌ schemas 导入失败: {e}")
    sys.exit(1)

# 检查 10: routers
print("\n🔟 检查 routers...")
try:
    from app.routers.providers import router
    print("   ✅ providers router 导入成功")
except ImportError as e:
    print(f"   ❌ providers router 导入失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有导入检查通过！")
print("=" * 60)

