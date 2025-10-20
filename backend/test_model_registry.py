"""
测试模型注册中心导入和功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("🧪 测试模型注册中心")
print("=" * 60)

# 测试 1: 导入枚举
print("\n✅ 测试 1: 导入枚举类型")
try:
    from app.ai.models import AIProvider, ModelType, ChatModel, EmbeddingModel
    print(f"  - AIProvider: {list(AIProvider)}")
    print(f"  - ModelType: {list(ModelType)}")
    print(f"  - ChatModel 数量: {len(list(ChatModel))}")
    print(f"  - EmbeddingModel 数量: {len(list(EmbeddingModel))}")
    print("  ✅ 枚举导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 测试 2: 导入元数据类
print("\n✅ 测试 2: 导入元数据类")
try:
    from app.ai.models import ModelMetadata
    print(f"  - ModelMetadata: {ModelMetadata}")
    print("  ✅ 元数据类导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 测试 3: 导入工具函数
print("\n✅ 测试 3: 导入工具函数")
try:
    from app.ai.models import (
        get_chat_model_metadata,
        get_embedding_model_metadata,
        get_provider_chat_models,
        get_provider_embedding_models,
        get_model_provider,
        is_model_available,
    )
    print("  ✅ 工具函数导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 测试 4: 获取嵌入模型元数据
print("\n✅ 测试 4: 获取嵌入模型元数据")
try:
    model = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
    metadata = get_embedding_model_metadata(model)
    print(f"  - 模型: {model.value}")
    print(f"  - 名称: {metadata.name}")
    print(f"  - 服务商: {metadata.provider.value}")
    print(f"  - 维度: {metadata.dimensions}")
    print(f"  - 价格: ${metadata.price_input}/1M tokens")
    print(f"  - 可用: {metadata.is_available}")
    print("  ✅ 元数据获取成功")
except Exception as e:
    print(f"  ❌ 获取失败: {e}")
    sys.exit(1)

# 测试 5: 获取服务商的所有嵌入模型
print("\n✅ 测试 5: 获取服务商的所有嵌入模型")
try:
    provider = AIProvider.OPENAI
    models = get_provider_embedding_models(provider)
    print(f"  - 服务商: {provider.value}")
    print(f"  - 模型数量: {len(models)}")
    for meta in models:
        print(f"    · {meta.name} ({meta.id}) - {meta.dimensions}维")
    print("  ✅ 服务商模型获取成功")
except Exception as e:
    print(f"  ❌ 获取失败: {e}")
    sys.exit(1)

# 测试 6: 根据模型获取服务商
print("\n✅ 测试 6: 根据模型获取服务商")
try:
    model = EmbeddingModel.OLLAMA_NOMIC_EMBED_TEXT
    provider = get_model_provider(model)
    print(f"  - 模型: {model.value}")
    print(f"  - 服务商: {provider.value}")
    print("  ✅ 服务商获取成功")
except Exception as e:
    print(f"  ❌ 获取失败: {e}")
    sys.exit(1)

# 测试 7: 向后兼容性 (EmbeddingProvider)
print("\n✅ 测试 7: 向后兼容性 (EmbeddingProvider)")
try:
    from app.ai.models import EmbeddingProvider
    print(f"  - EmbeddingProvider: {list(EmbeddingProvider)}")
    assert EmbeddingProvider.OPENAI == AIProvider.OPENAI
    print("  ✅ 向后兼容别名有效")
except Exception as e:
    print(f"  ❌ 兼容性测试失败: {e}")
    sys.exit(1)

# 测试 8: MODEL_DIMENSIONS 兼容性
print("\n✅ 测试 8: MODEL_DIMENSIONS 向后兼容性")
try:
    from app.ai.models import MODEL_DIMENSIONS
    model = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
    dimension = MODEL_DIMENSIONS.get(model)
    print(f"  - 模型: {model.value}")
    print(f"  - 维度: {dimension}")
    assert dimension == 1536
    print("  ✅ MODEL_DIMENSIONS 兼容")
except Exception as e:
    print(f"  ❌ 兼容性测试失败: {e}")
    sys.exit(1)

# 测试 9: 测试 EmbeddingService
print("\n✅ 测试 9: 测试 EmbeddingService 导入")
try:
    from app.services.embedding_service import EmbeddingService
    print(f"  - EmbeddingService: {EmbeddingService}")
    print("  ✅ EmbeddingService 导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 所有测试通过！模型注册中心工作正常！")
print("=" * 60)

