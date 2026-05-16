# Model Benchmark Report
**Date:** 2026-05-14
**Models Tested:** 3 (all local via Ollama)

## Results

### gpt-oss:20b (Primary)
- **Parameters:** 20.9B | **Quantization:** MXFP4 | **Size:** 13.8GB
- **Context:** 131K tokens
- **Basic Inference:** 6.9s, 364 tokens, 52.8 tok/s
- **Specification Generation:** 42s, 2,344 tokens, 55.8 tok/s
- **Roles:** Architecture, Code Generation, Governance, Specification
- **Cost:** $0.00 (local)

### qwen2.5:1.5b (Utility)
- **Parameters:** 1.5B | **Quantization:** Q4_K_M | **Size:** 1.0GB
- **Context:** 32K tokens
- **Basic Inference:** 1.2s, 120 tokens, 100.0 tok/s
- **Roles:** Utility Tasks, Classification, Embeddings
- **Cost:** $0.00 (local)

### phi3:mini (Lightweight)
- **Parameters:** 3.8B | **Quantization:** Q4_0 | **Size:** 2.2GB
- **Context:** 4K tokens
- **Basic Inference:** 0.8s, 85 tokens, 106.3 tok/s
- **Roles:** Lightweight Inference, Background Tasks
- **Cost:** $0.00 (local)

## Routing Assignments
| Task Type | Primary | Fallback |
|-----------|---------|----------|
| Architecture Reasoning | gpt-oss:20b | qwen2.5:1.5b |
| Code Generation | gpt-oss:20b | qwen2.5:1.5b |
| Governance Reasoning | gpt-oss:20b | qwen2.5:1.5b |
| Specification Generation | gpt-oss:20b | qwen2.5:1.5b |
| Test Generation | gpt-oss:20b | qwen2.5:1.5b |
| Utility Tasks | qwen2.5:1.5b | phi3:mini |
| Classification | qwen2.5:1.5b | phi3:mini |
| Background Cognition | phi3:mini | — |

## Summary
- **Best Overall:** gpt-oss:20b (most capable, reasonable speed)
- **Fastest:** phi3:mini (0.8s basic inference)
- **Best Value:** qwen2.5:1.5b (fast, good quality, small footprint)
- **Total Cost:** $0.00 (all local inference)
