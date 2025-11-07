# CodeAct Integration Guide

## Overview

This project integrates [CodeAct](https://github.com/xingyaoww/code-act) - a framework for LLM agents that generate and execute Python code - with a trading analysis system.

## What is CodeAct?

CodeAct is a research framework from ICML 2024 that enables LLM agents to:
- Generate Python code as actions
- Execute code in a Python interpreter
- Observe execution results
- Revise code based on errors or new information
- Perform complex multi-step tasks autonomously

**Paper**: [Executable Code Actions Elicit Better LLM Agents](https://arxiv.org/abs/2402.01030)

## How It Works in Our System

```
User Query (Natural Language)
    ↓
TraderCodeAct.analyze()
    ↓
1. Fetch OHLC data from API
2. Save to CSV
3. Create prompt for CodeAct
    ↓
CodeAct Agent
    ↓
1. Generates Python code
2. Executes code (pandas, vectorbt, ta, matplotlib)
3. Observes results
4. Revises if needed
    ↓
Returns JSON with:
- Summary
- Metrics (return, Sharpe, drawdown, etc.)
- Plot path
```

## Installation

### Step 1: Clone CodeAct Repository

```bash
git clone https://github.com/xingyaoww/code-act.git
cd code-act
```

### Step 2: Install CodeAct

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Step 3: Verify Installation

```bash
python -c "from codeact import CodeActAgent; print('Success!')"
```

Or use our install script:

```bash
./install_codeact.sh
```

## Usage Example

```python
from finbytes.codeact_trader import TraderCodeAct

# Initialize
trader = TraderCodeAct()

# Analyze
result = trader.analyze(
    user_query="Backtest RSI(14) + SMA(20) crossover strategy",
    symbol="AAPL",
    interval="1w",
    start_date="2024-01-01",
    end_date="2024-03-31"
)

print(result)
```

## CodeAct Agent Behavior

When you give CodeAct a task, it:

1. **Understands** the task in natural language
2. **Generates** Python code to solve it
3. **Executes** the code
4. **Observes** the results
5. **Revises** if there are errors or unexpected results
6. **Returns** the final output

For example, if you ask: "Calculate RSI(14) and plot it"

CodeAct might generate:
```python
import pandas as pd
import ta
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv', index_col='Date', parse_dates=True)
df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
df['RSI'].plot()
plt.savefig('/tmp/result.png')
```

If there's an error, CodeAct will:
- See the error message
- Understand what went wrong
- Generate corrected code
- Try again

## Model Options

CodeAct provides pre-trained models:

- `xingyaoww/CodeActAgent-Mistral-7b-v0.1` (Default)
- `xingyaoww/CodeActAgent-Llama2-7b-v0.1`

Change the model in `TraderCodeAct.__init__()`:

```python
trader = TraderCodeAct(model_name="xingyaoww/CodeActAgent-Llama2-7b-v0.1")
```

## Customization

### Modify Prompts

Edit the prompt template in `finbytes/codeact_trader.py` (around line 88) to:
- Change the instruction style
- Add domain-specific guidance
- Include examples
- Set output format requirements

### Add Libraries

CodeAct can use any Python library. To ensure availability, add to the prompt:

```python
"Available libraries: pandas, numpy, matplotlib, vectorbt, ta, scipy, sklearn"
```

### Change Output Format

Modify the JSON schema in the prompt (around line 110) to include/exclude fields.

## Troubleshooting

### Import Errors

If `from codeact import CodeActAgent` fails:

1. Check you're in the virtual environment
2. Verify CodeAct is installed: `pip list | grep codeact`
3. Check the actual import path in the repository
4. Try alternative imports (see `codeact_trader.py`)

### Model Loading Issues

- Ensure internet connection (models download from Hugging Face)
- Check disk space (models are 7-13GB)
- Verify model name is correct
- May need Hugging Face authentication

### Execution Errors

CodeAct generates and executes code. If it fails:

1. Check the error in logs
2. CodeAct should self-correct, but you can improve prompts
3. Ensure required libraries are installed
4. Check file permissions for temp files

## Alternative Approaches

If CodeAct installation is problematic, consider:

1. **Direct LLM API**: Use OpenAI/Anthropic to generate code, execute manually
2. **Simpler Agent**: Use LangChain or similar with code execution
3. **Template-based**: Pre-written code templates with parameter substitution

## References

- **Repository**: https://github.com/xingyaoww/code-act
- **Paper**: https://arxiv.org/abs/2402.01030
- **Hugging Face Models**: https://huggingface.co/xingyaoww

## Support

For CodeAct-specific issues:
- Check the repository README
- Review the paper for methodology
- Open an issue on the CodeAct repository

For integration issues:
- Check `CODEACT_SETUP.md`
- Review `TESTING.md`
- Check logs for detailed error messages

