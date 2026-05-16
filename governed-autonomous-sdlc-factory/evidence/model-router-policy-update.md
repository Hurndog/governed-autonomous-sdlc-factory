# Model Router Policy Update
**Date:** 2026-05-14
**Status:** ✅ UPDATED for Gemma 4 E4B primary

## Routing Policy v2

### Primary Model: Gemma 4 E4B (LM Studio)
**Endpoint:** http://localhost:1234/v1

| Task Type | Primary | Fallback |
|-----------|---------|----------|
| architecture_reasoning | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |
| governance_reasoning | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |
| specification_generation | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |
| code_generation | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |
| structured_output_generation | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |
| tool_calling_tests | lm_studio/google/gemma-4-e4b | ollama/gpt-oss:20b |

### Fallback Model: gpt-oss:20b (Ollama)
**Endpoint:** http://localhost:11434

| Task Type | Primary | Fallback |
|-----------|---------|----------|
| fallback_heavy_reasoning | ollama/gpt-oss:20b | lm_studio/google/gemma-4-e4b |
| long_generation | ollama/gpt-oss:20b | lm_studio/google/gemma-4-e4b |
| second_opinion | ollama/gpt-oss:20b | null |
| baseline_comparison | ollama/gpt-oss:20b | null |

### Utility Model: qwen2.5:1.5b (Ollama)
**Endpoint:** http://localhost:11434

| Task Type | Primary | Fallback |
|-----------|---------|----------|
| utility_tasks | ollama/qwen2.5:1.5b | ollama/phi3:mini |
| classification | ollama/qwen2.5:1.5b | ollama/phi3:mini |
| metadata_extraction | ollama/qwen2.5:1.5b | ollama/phi3:mini |
| routing_decisions | ollama/qwen2.5:1.5b | null |

### Lightweight Model: phi3:mini (Ollama)
| Task Type | Primary | Fallback |
|-----------|---------|----------|
| lightweight_background_checks | ollama/phi3:mini | null |

### Embeddings: nomic-embed-text-v1.5 (LM Studio)
| Task Type | Primary | Fallback |
|-----------|---------|----------|
| embeddings | lm_studio/text-embedding-nomic-embed-text-v1.5 | null |

## JSON Extraction Logic
Gemma 4 E4B wraps JSON in markdown code blocks:
```
```json
{ ... }
```
```
The API must extract JSON from markdown before parsing. This is handled by the model provider adapter.

## Provider Priority
1. LM Studio (Gemma 4 E4B) — fastest, good quality
2. Ollama (gpt-oss:20b) — most capable, fallback
3. Ollama (qwen2.5:1.5b) — utility tasks
4. Ollama (phi3:mini) — lightweight tasks
