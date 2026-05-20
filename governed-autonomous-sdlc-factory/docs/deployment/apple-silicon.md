# Apple Silicon Deployment Guide

The Governed Autonomous SDLC Factory runs natively on Apple Silicon (M1/M2/M3/M4) with full Metal GPU acceleration support via Ollama.

## Prerequisites

- macOS 14+ on Apple Silicon
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (ARM64): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

## Install Dependencies

```bash
# Install Python (ARM64 native)
brew install python@3.12

# Install Node.js
brew install node@20

# Install PostgreSQL
brew install postgresql@15

# Install Redis
brew install redis

# Install Ollama (native Apple Silicon with Metal support)
brew install ollama
```

## Pull Local Models

```bash
# Start Ollama
ollama serve

# Pull recommended models (ARM64 optimized)
ollama pull phi3          # ~2.3GB, fast reasoning
ollama pull qwen2.5-coder # ~4.7GB, excellent coding
ollama pull llama3.1      # ~4.7GB, general purpose
ollama pull deepseek-r1   # ~4.7GB, deep reasoning

# Verify models
ollama list
```

## Configure for Apple Silicon

Edit `.env`:

```bash
# Ollama with Metal GPU acceleration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL_PROVIDER=ollama
LOCAL_ONLY_MODE=true

# Apple Silicon optimized settings
# Ollama automatically uses Metal GPU on Apple Silicon
# No additional configuration needed
```

## Performance Expectations

| Model | Size | Speed (M1 Pro) | Speed (M4 Max) |
|-------|------|----------------|----------------|
| phi3:mini | 2.3GB | ~30 tok/s | ~80 tok/s |
| qwen2.5-coder:7b | 4.7GB | ~20 tok/s | ~55 tok/s |
| llama3.1:8b | 4.7GB | ~18 tok/s | ~50 tok/s |
| deepseek-r1:7b | 4.7GB | ~15 tok/s | ~45 tok/s |

## Docker on Apple Silicon

Docker Desktop for Mac (Apple Silicon) uses ARM64 images by default:

```bash
# Install Docker Desktop
brew install --cask docker

# Launch Docker Desktop
open /Applications/Docker.app

# Verify ARM64 images
docker info | grep Architecture
# Should show: Architecture: aarch64

# Launch services
docker-compose up -d postgres redis qdrant
```

## Troubleshooting

### Ollama Metal GPU Not Working

```bash
# Check Ollama is using GPU
ollama logs | grep -i metal

# If not, set environment variable
export OLLAMA_METAL=1
ollama serve
```

### Python Architecture Mismatch

```bash
# Verify Python is ARM64
python3 -c "import platform; print(platform.machine())"
# Should show: arm64

# If it shows x86_64, reinstall:
brew reinstall python@3.12
```

### Node.js Architecture Mismatch

```bash
# Verify Node is ARM64
node -p "process.arch"
# Should show: arm64
```
