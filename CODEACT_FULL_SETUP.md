# CodeAct Full Setup Guide

Based on the official CodeAct repository, CodeAct requires a multi-component architecture.

## 🏗️ Architecture Overview

CodeAct consists of three main components:

1. **LLM Serving** - Serves the model via OpenAI-compatible API
   - Option A: vLLM (requires NVIDIA GPU)
   - Option B: llama.cpp (works on Mac/CPU)

2. **Code Execution Engine** - Executes code in isolated Docker containers
   - Jupyter Kernel Gateway in Docker
   - One container per chat session

3. **Interaction Interface** - User interface
   - Option A: Chat-UI (web interface)
   - Option B: Python script (command line)

## 📋 Setup Options

### Option 1: Full CodeAct Setup (Recommended for Production)

This requires:
- Docker installed
- NVIDIA GPU (for vLLM) OR Mac with llama.cpp
- Model download (~14GB)

### Option 2: Simplified Setup (Current Implementation)

Our current implementation uses `SimpleTrader` which works without CodeAct infrastructure:
- ✅ Works immediately
- ✅ No GPU required
- ✅ No Docker required
- ⚠️ Limited to predefined strategies

### Option 3: Hybrid Approach

Use our SimpleTrader now, add CodeAct later when infrastructure is ready.

## 🚀 Quick Start: Full CodeAct Setup

### Step 1: Clone CodeAct Repository

```bash
cd /path/to/your/projects
git clone https://github.com/xingyaoww/code-act.git
cd code-act
git submodule update --init --recursive
```

### Step 2: Download Model

```bash
# Install git-lfs if not already installed
git lfs install

# Download the model (choose one)
# Option A: Mistral-based
git clone https://huggingface.co/xingyaoww/CodeActAgent-Mistral-7b-v0.1

# Option B: Llama-based
git clone https://huggingface.co/xingyaoww/CodeActAgent-Llama-7b
```

### Step 3: Serve the Model

#### Option A: Using vLLM (NVIDIA GPU Required)

```bash
cd code-act
./scripts/chat/start_vllm.sh /path/to/CodeActAgent-Mistral-7b-v0.1
```

This starts the model server on `http://localhost:8080/v1`

#### Option B: Using llama.cpp (Mac/CPU)

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make

# Convert model (if needed)
python convert.py /path/to/CodeActAgent-Mistral-7b-v0.1 --outtype f16 --outfile model.f16.gguf
./quantize model.f16.gguf model.q8_0.gguf Q8_0

# Serve model
./server -m model.q8_0.gguf -c 8192 --port 8080
```

### Step 4: Start Code Execution Engine

```bash
cd code-act
./scripts/chat/code_execution/start_jupyter_server.sh 8081
```

This starts the code execution server on `http://localhost:8081`

### Step 5: Test the Setup

```bash
cd code-act
python3 scripts/chat/demo.py \
  --model_name xingyaoww/CodeActAgent-Mistral-7b-v0.1 \
  --openai_api_base http://localhost:8080/v1 \
  --jupyter_kernel_url http://localhost:8081/execute
```

## 🔌 Integrating with Our Trading System

Once CodeAct is set up, we can integrate it with our trading system.

### Update Our CodeAct Trader

We need to modify `finbytes/codeact_trader.py` to use the OpenAI-compatible API instead of direct model loading.

### Configuration

Create a config file or environment variables:

```bash
export CODEACT_API_BASE=http://localhost:8080/v1
export CODEACT_MODEL_NAME=xingyaoww/CodeActAgent-Mistral-7b-v0.1
export CODEACT_JUPYTER_URL=http://localhost:8081/execute
```

## 📝 Simplified Alternative

If you don't want to set up the full CodeAct infrastructure right now:

1. **Use SimpleTrader** (already implemented)
   - Works immediately
   - Supports common strategies
   - No additional setup needed

2. **Add CodeAct later** when you have:
   - GPU access OR Mac with llama.cpp
   - Docker installed
   - Time to set up the infrastructure

## 🎯 Recommended Path

1. **Start with SimpleTrader** - Get the system working now
2. **Test and validate** - Make sure everything works
3. **Add CodeAct later** - When you need advanced natural language capabilities

## 📚 Resources

- **CodeAct Repository**: https://github.com/xingyaoww/code-act
- **vLLM Documentation**: https://docs.vllm.ai/
- **llama.cpp**: https://github.com/ggerganov/llama.cpp
- **Paper**: https://arxiv.org/abs/2402.01030

## ⚠️ Requirements Summary

### Full CodeAct Setup:
- ✅ Docker
- ✅ NVIDIA GPU (vLLM) OR Mac (llama.cpp)
- ✅ ~14GB disk space for model
- ✅ Good internet connection
- ⏱️ 1-2 hours setup time

### SimpleTrader (Current):
- ✅ Python 3.11+
- ✅ pip packages
- ✅ ~500MB disk space
- ⏱️ 5 minutes setup time

