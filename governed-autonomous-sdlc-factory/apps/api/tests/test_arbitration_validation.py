"""
Arbitration Validation — Phase 3

Tests the CognitiveArbitrationEngine with various scenarios.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engines.cognitive_governance import (
    CognitiveArbitrationEngine,
    ArbitrationResult,
    TaskType,
    get_arbitration_engine,
)


def test_arbitration_agreement():
    """Test agreement case — models produce similar outputs."""
    print("\n═══ TEST: Arbitration Agreement ═══")

    engine = CognitiveArbitrationEngine(
        consensus_threshold=0.7,
        contradiction_threshold=0.5,
    )

    outputs = [
        {"provider": "ollama", "model": "phi3:mini", "output": "The system should use JWT tokens for authentication", "success": True},
        {"provider": "ollama", "model": "qwen2.5:1.5b", "output": "The system should use JWT tokens for authentication", "success": True},
    ]

    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.arbitrate(outputs, TaskType.CODE_GENERATION))
    loop.close()

    print(f"  Consensus score: {result.consensus_score:.2f}")
    print(f"  Contradiction score: {result.contradiction_score:.2f}")
    print(f"  Decision: {result.arbitration_decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Escalation: {result.escalation_required}")
    print(f"  Human review: {result.human_review_required}")

    assert result.consensus_score > 0.7, f"Expected high consensus, got {result.consensus_score}"
    assert result.arbitration_decision == "consensus", f"Expected consensus, got {result.arbitration_decision}"
    assert result.escalation_required is False, "Should not escalate on agreement"
    print("  ✅ AGREEMENT CASE PASSED")


def test_arbitration_disagreement():
    """Test disagreement case — models produce different outputs."""
    print("\n═══ TEST: Arbitration Disagreement ═══")

    engine = CognitiveArbitrationEngine(
        consensus_threshold=0.7,
        contradiction_threshold=0.5,
    )

    outputs = [
        {"provider": "ollama", "model": "phi3:mini", "output": "Use JWT tokens for authentication", "success": True},
        {"provider": "ollama", "model": "qwen2.5:1.5b", "output": "Use session cookies instead of tokens", "success": True},
    ]

    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.arbitrate(outputs, TaskType.CODE_GENERATION))
    loop.close()

    print(f"  Consensus score: {result.consensus_score:.2f}")
    print(f"  Contradiction score: {result.contradiction_score:.2f}")
    print(f"  Decision: {result.arbitration_decision}")
    print(f"  Divergence: {result.divergence_categories}")
    print(f"  Escalation: {result.escalation_required}")

    assert result.contradiction_score > 0.3, f"Expected some contradiction, got {result.contradiction_score}"
    assert result.arbitration_decision in ("disagreement_detected", "partial_consensus"), f"Expected disagreement, got {result.arbitration_decision}"
    print("  ✅ DISAGREEMENT CASE PASSED")


def test_arbitration_governance_divergence():
    """Test governance divergence — disagreement on governance task."""
    print("\n═══ TEST: Arbitration Governance Divergence ═══")

    engine = CognitiveArbitrationEngine(
        consensus_threshold=0.7,
        contradiction_threshold=0.5,
    )

    outputs = [
        {"provider": "ollama", "model": "phi3:mini", "output": "This change complies with all governance policies", "success": True},
        {"provider": "ollama", "model": "qwen2.5:1.5b", "output": "This change violates security policy section 4.2", "success": True},
    ]

    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.arbitrate(outputs, TaskType.GOVERNANCE_ANALYSIS))
    loop.close()

    print(f"  Consensus score: {result.consensus_score:.2f}")
    print(f"  Contradiction score: {result.contradiction_score:.2f}")
    print(f"  Decision: {result.arbitration_decision}")
    print(f"  Divergence: {result.divergence_categories}")
    print(f"  Governance risk: {result.governance_risk:.2f}")
    print(f"  Escalation: {result.escalation_required}")
    print(f"  Human review: {result.human_review_required}")

    assert "governance_divergence" in result.divergence_categories, "Should detect governance divergence"
    assert result.governance_risk > 0.0, "Should have governance risk"
    assert result.escalation_required is True, "Should escalate on governance disagreement"
    assert result.human_review_required is True, "Should require human review"
    print("  ✅ GOVERNANCE DIVERGENCE CASE PASSED")


def test_arbitration_single_model():
    """Test single model case — no arbitration needed."""
    print("\n═══ TEST: Arbitration Single Model ═══")

    engine = CognitiveArbitrationEngine()

    outputs = [
        {"provider": "ollama", "model": "phi3:mini", "output": "Use JWT tokens", "success": True},
    ]

    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.arbitrate(outputs, TaskType.CODE_GENERATION))
    loop.close()

    print(f"  Consensus score: {result.consensus_score:.2f}")
    print(f"  Decision: {result.arbitration_decision}")

    assert result.consensus_score == 1.0, "Single model should have perfect consensus"
    assert result.arbitration_decision == "single_model", "Should be marked as single model"
    print("  ✅ SINGLE MODEL CASE PASSED")


def test_arbitration_all_failed():
    """Test all models failed case."""
    print("\n═══ TEST: Arbitration All Failed ═══")

    engine = CognitiveArbitrationEngine()

    outputs = [
        {"provider": "ollama", "model": "phi3:mini", "output": "", "success": False, "error": "timeout"},
        {"provider": "ollama", "model": "qwen2.5:1.5b", "output": "", "success": False, "error": "timeout"},
    ]

    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(engine.arbitrate(outputs, TaskType.CODE_GENERATION))
    loop.close()

    print(f"  Consensus score: {result.consensus_score:.2f}")
    print(f"  Decision: {result.arbitration_decision}")
    print(f"  Escalation: {result.escalation_required}")

    assert result.arbitration_decision == "all_failed", "Should be marked as all failed"
    assert result.escalation_required is True, "Should escalate when all fail"
    print("  ✅ ALL FAILED CASE PASSED")


def test_arbitration_result_persistence():
    """Test that arbitration results can be serialized."""
    print("\n═══ TEST: Arbitration Result Persistence ═══")

    result = ArbitrationResult(
        participating_models=[{"provider": "ollama", "model": "phi3:mini"}],
        outputs=[{"output": "test"}],
        consensus_score=0.85,
        contradiction_score=0.15,
        arbitration_decision="consensus",
        confidence=0.85,
    )

    # Verify all fields are accessible
    assert len(result.participating_models) == 1
    assert result.consensus_score == 0.85
    assert result.arbitration_decision == "consensus"
    assert result.escalation_required is False
    print("  ✅ RESULT PERSISTENCE PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("  ARBITRATION VALIDATION — Phase 3")
    print("=" * 60)

    try:
        test_arbitration_agreement()
        test_arbitration_disagreement()
        test_arbitration_governance_divergence()
        test_arbitration_single_model()
        test_arbitration_all_failed()
        test_arbitration_result_persistence()

        print("\n" + "=" * 60)
        print("  ARBITRATION VALIDATION COMPLETE ✅")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
