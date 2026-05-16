# Gemma 4 E4B Evaluation Report
**Date:** 2026-05-14
**Model:** google/gemma-4-e4b via LM Studio
**Status:** ✅ APPROVED as primary model

## Executive Summary
Gemma 4 E4B is a **fast, capable 4B parameter model** that outperforms gpt-oss:20b on latency while maintaining good output quality. It is now the **primary model** for architecture, governance, specification, and code generation tasks.

## Benchmark Results

### Latency Comparison
| Task | Gemma 4 E4B | gpt-oss:20b | Winner |
|------|-------------|-------------|--------|
| Basic Inference | 1.2s | 6.9s | **Gemma** (5.7x faster) |
| Spec Generation | 17.9s (895 tok) | 34.0s (1395 tok) | **Gemma** (1.9x faster) |
| Architecture | 23.7s (1085 tok) | — | **Gemma** |
| Governance | 26.0s (1277 tok) | — | **Gemma** |
| Code Generation | 32.1s (1560 tok) | — | **Gemma** |

### Token Throughput
| Model | Avg tok/s |
|-------|-----------|
| Gemma 4 E4B | 45-50 |
| gpt-oss:20b | 41-53 |
| qwen2.5:1.5b | 100 |
| phi3:mini | 106 |

### Output Quality

#### Specification Generation
- **Gemma**: 6 FR, 4 NFR, 5 AC, 5 Gov areas — good structure, slightly less detailed
- **gpt-oss**: 10 FR, 5 NFR, 15 AC, 5 Gov areas — more comprehensive
- **Verdict**: gpt-oss produces more detailed specs, but Gemma is faster and still good

#### Architecture Reasoning
- **Gemma**: Produces components, decisions, Mermaid diagrams — wraps in ```json markdown
- **Verdict**: Good quality, requires JSON extraction from markdown

#### Code Generation
- **Gemma**: 122 lines of Python with FastAPI + SQLAlchemy — complete and correct
- **Verdict**: Excellent code quality

#### Governance Reasoning
- **Gemma**: Produces governance concerns, security findings, compliance gaps
- **Verdict**: Good quality, well-structured

### JSON Output Behavior
⚠️ **Important**: Gemma 4 E4B wraps JSON responses in markdown code blocks:
```
```json
{ ... }
```
```
The model router's JSON extraction logic must handle this. The `json_output_format` is set to `markdown_wrapped` in the registry.

### Vision Support
❌ **Not available** via LM Studio endpoint. The model may be vision-capable but LM Studio's OpenAI-compatible endpoint does not support image input.

### Streaming Support
✅ **Available** — LM Studio supports streaming via `stream: true`.

## Recommendation
**APPROVE as primary model** for:
- Architecture reasoning
- Governance reasoning
- Specification generation
- Code generation
- Structured output (with markdown extraction)

**Use gpt-oss:20b as fallback** for:
- Heavy reasoning requiring more detail
- Direct JSON output (no markdown wrapping)
- Second opinion / baseline comparison
- Long-form generation

## Known Issues
1. JSON wrapped in markdown code blocks — requires extraction
2. Vision not available via LM Studio endpoint
3. Context length not yet determined
