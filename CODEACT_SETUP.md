# CodeAct Setup Guide

Based on the official CodeAct repository: https://github.com/xingyaoww/code-act

## What is CodeAct?

CodeAct is a framework that enables LLM agents to perform actions by generating and executing Python code. It was introduced in the paper "Executable Code Actions Elicit Better LLM Agents" (ICML 2024, arXiv:2402.01030).

Key features:
- LLM agents generate Python code as actions
- Code is executed in a Python interpreter
- Agents can revise actions based on execution results
- Multi-turn interactions for complex tasks
- Self-debugging capabilities

## Installation Methods

### Method 1: Install from GitHub Repository

```bash
# Clone the repository
git clone https://github.com/xingyaoww/code-act.git
cd code-act

# Install dependencies and the package
pip install -e .

# Or install specific requirements
pip install -r requirements.txt
```

### Method 2: Check Repository Structure

The actual import structure may vary. Common patterns:

```python
# Option 1: Direct import
from codeact import CodeActAgent

# Option 2: From a submodule
from codeact.agent import CodeActAgent

# Option 3: Different class name
from codeact import Agent
```

### Method 3: Use Pre-trained Models

CodeAct provides pre-trained models on Hugging Face:
- `xingyaoww/CodeActAgent-Mistral-7b-v0.1`
- `xingyaoww/CodeActAgent-Llama2-7b-v0.1`

These can be loaded using:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
# Or using CodeAct's custom loader
```

## Repository Structure

Based on the GitHub repository, the structure typically includes:

```
code-act/
├── codeact/          # Main package
│   ├── agent.py      # CodeActAgent class
│   ├── interpreter.py # Python interpreter integration
│   └── ...
├── models/           # Model definitions
├── data/             # Datasets
├── requirements.txt  # Dependencies
└── README.md         # Documentation
```

## Dependencies

CodeAct typically requires:
- Python 3.8+
- transformers
- torch
- numpy
- pandas
- (Other dependencies as specified in requirements.txt)

## Usage Pattern

The typical usage pattern for CodeAct:

```python
from codeact import CodeActAgent

# Initialize agent
agent = CodeActAgent.from_pretrained("xingyaoww/CodeActAgent-Mistral-7b-v0.1")

# Run a task
result = agent.run("Your task description here")

# The agent will:
# 1. Generate Python code
# 2. Execute it
# 3. Observe results
# 4. Revise if needed
# 5. Return final result
```

## Integration with Our Trading System

Our `TraderCodeAct` class wraps CodeAct to:
1. Fetch OHLC data from your API
2. Format it for CodeAct
3. Create prompts for trading analysis
4. Execute CodeAct agent
5. Parse and format results

## Troubleshooting

### Issue: Import Error

If you get `ModuleNotFoundError: No module named 'codeact'`:

1. Check if you're in the code-act directory
2. Verify installation: `pip list | grep codeact`
3. Try: `pip install -e .` from the code-act directory
4. Check Python path: `python -c "import sys; print(sys.path)"`

### Issue: Model Loading Error

If model loading fails:

1. Check Hugging Face access (may need authentication)
2. Verify model name is correct
3. Ensure sufficient disk space (models are large)
4. Check internet connection

### Issue: API Mismatch

If the API doesn't match our code:

1. Check the actual repository structure
2. Review the repository's examples
3. Update our `codeact_trader.py` to match the actual API
4. Check the repository's README for usage examples

## Alternative: Manual Code Execution

If CodeAct installation is problematic, you can create a simpler version that:
1. Uses an LLM API (OpenAI, Anthropic, etc.) to generate code
2. Executes the code in a sandboxed environment
3. Returns results

This would require modifying `codeact_trader.py` to use a different backend.

## References

- **Repository**: https://github.com/xingyaoww/code-act
- **Paper**: https://arxiv.org/abs/2402.01030
- **ICML 2024**: "Executable Code Actions Elicit Better LLM Agents"

## Next Steps

1. Clone the CodeAct repository
2. Review the README and examples
3. Install following their instructions
4. Test with a simple example
5. Integrate with our trading system

