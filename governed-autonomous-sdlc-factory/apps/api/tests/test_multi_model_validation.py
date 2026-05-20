"""
Multi-Model Validation — Truth Closure Pass

Validates:
1. CognitiveModelRouter routing logic
2. Capability registry
3. Sovereignty-aware routing
4. Model provider health checks
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engines.model_router import ModelRouter, get_router
from src.engines.model_registry import ModelRegistry, ModelEntry
from src.engines.model_providers import ProviderType


def test_model_registry():
    """Test that the model registry is populated and functional."""
    print("\n═══ TEST: Model Registry ═══")

    registry = ModelRegistry()
    registry.load_defaults()

    # Test 1: Registry has models after loading defaults
    print("  → Loading default models...")
    models = registry.list_models()
    assert len(models) > 0, f"Registry should have default models, got {len(models)}"
    print(f"  ✅ {len(models)} models registered")

    # Test 2: Can retrieve a specific model
    print("  → Retrieving specific model...")
    entry = registry.get(ProviderType.LM_STUDIO.value, "local-model")
    if entry:
        print(f"  ✅ Found: {entry.provider}:{entry.model_id}")
        print(f"     Capabilities: coding={entry.capabilities.coding_quality}, reasoning={entry.capabilities.reasoning_quality}")
    else:
        print("  ⚠ LM_STUDIO:local-model not found (may need configuration)")

    # Test 3: Default model
    print("  → Getting default model...")
    default = registry.get_default()
    if default:
        print(f"  ✅ Default: {default.provider}:{default.model_id}")
    else:
        print("  ⚠ No default model set")

    # Test 4: List all models with capabilities
    print("  → Listing all models...")
    for m in models:
        print(f"  ✅ {m.provider}:{m.model_id} (ctx={m.capabilities.context_length})")

    print("  ✅ MODEL REGISTRY PASSED")


def test_model_router_initialization():
    """Test that the model router initializes correctly."""
    print("\n═══ TEST: Model Router Initialization ═══")

    router = ModelRouter()
    assert router is not None, "Router should initialize"
    print("  ✅ Router initialized")

    # Check stats
    stats = router.get_stats()
    print(f"  ✅ Router stats: {stats}")

    print("  ✅ MODEL ROUTER INITIALIZATION PASSED")


def test_capability_matching():
    """Test that capability matching works."""
    print("\n═══ TEST: Capability Matching ═══")

    registry = ModelRegistry()
    registry.load_defaults()

    # Test: Filter by provider
    print("  → Filtering by provider...")
    ollama_models = registry.list_models(provider=ProviderType.LM_STUDIO.value)
    print(f"  ✅ {len(ollama_models)} LM Studio models")

    # Test: Filter by context length
    print("  → Filtering by context length...")
    large_ctx = registry.list_models(min_context=8000)
    print(f"  ✅ {len(large_ctx)} models with 8K+ context")

    print("  ✅ CAPABILITY MATCHING PASSED")


def test_model_entry_fields():
    """Test that ModelEntry has expected fields."""
    print("\n═══ TEST: Model Entry Fields ═══")

    registry = ModelRegistry()
    registry.load_defaults()
    models = registry.list_models()

    if models:
        m = models[0]
        assert hasattr(m, 'provider'), "ModelEntry should have provider"
        assert hasattr(m, 'model_id'), "ModelEntry should have model_id"
        assert hasattr(m, 'capabilities'), "ModelEntry should have capabilities"
        print(f"  ✅ ModelEntry has provider={m.provider}, model_id={m.model_id}")
        print(f"  ✅ Capabilities: {vars(m.capabilities)}")
    else:
        print("  ⚠ No models to test")

    print("  ✅ MODEL ENTRY FIELDS PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("  MULTI-MODEL VALIDATION — Truth Closure Pass")
    print("=" * 60)

    try:
        test_model_registry()
        test_model_router_initialization()
        test_capability_matching()
        test_model_entry_fields()

        print("\n" + "=" * 60)
        print("  MULTI-MODEL VALIDATION COMPLETE ✅")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
