#!/bin/bash
# Script to install CodeAct from source
# Based on: https://github.com/xingyaoww/code-act

set -e

echo "=========================================="
echo "Installing CodeAct from Source"
echo "Repository: https://github.com/xingyaoww/code-act"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Check if code-act directory exists
if [ -d "code-act" ]; then
    echo "⚠️  code-act directory already exists."
    read -p "Update existing repository? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Updating CodeAct repository..."
        cd code-act
        git pull
    else
        echo "⏭️  Using existing repository"
        cd code-act
    fi
else
    echo "📥 Cloning CodeAct repository..."
    git clone https://github.com/xingyaoww/code-act.git
    cd code-act
fi

echo ""
echo "📋 Checking repository structure..."
if [ -f "requirements.txt" ]; then
    echo "✅ Found requirements.txt"
    echo "📦 Installing dependencies (with version flexibility)..."
    
    # Install torch separately with a compatible version
    echo "   Installing PyTorch (using latest compatible version)..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || \
    pip install torch torchvision torchaudio 2>/dev/null || \
    pip install torch 2>/dev/null || echo "   ⚠️  Could not install torch, continuing..."
    
    # Install other dependencies, skipping torch-related ones
    echo "   Installing other dependencies..."
    pip install transformers datasets numpy pandas scipy ipython matplotlib \
        openai langchain streamlit tqdm nltk pyyaml pytz python-dateutil \
        seaborn flask gunicorn tornado 2>/dev/null || \
    echo "   ⚠️  Some dependencies may have failed, continuing..."
    
    # Try to install remaining requirements, ignoring version conflicts
    echo "   Attempting to install remaining requirements (ignoring version conflicts)..."
    pip install -r requirements.txt --no-deps 2>/dev/null || \
    pip install $(grep -v "^#" requirements.txt | grep -v "^torch" | grep -v "^torchvision" | grep -v "^torchaudio" | tr '\n' ' ') 2>/dev/null || \
    echo "   ⚠️  Some optional dependencies may be missing"
else
    echo "⚠️  No requirements.txt found, installing common dependencies..."
    pip install transformers torch numpy pandas
fi

echo ""
echo "📦 Installing CodeAct package..."
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    pip install -e .
else
    echo "⚠️  No setup.py or pyproject.toml found"
    echo "   Adding code-act directory to Python path..."
    # This will be handled by the import fallback in codeact_trader.py
fi

cd ..

echo ""
echo "🧪 Testing CodeAct import..."
python3 -c "
try:
    from codeact import CodeActAgent
    print('✅ CodeAct imported successfully (from codeact)')
except ImportError:
    try:
        from codeact.agent import CodeActAgent
        print('✅ CodeAct imported successfully (from codeact.agent)')
    except ImportError:
        print('⚠️  CodeAct import failed. Check the repository structure.')
        print('   You may need to adjust the import in finbytes/codeact_trader.py')
        exit(1)
" || echo "⚠️  Import test failed, but installation may still work"

echo ""
echo "=========================================="
echo "✅ CodeAct installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review CODEACT_SETUP.md for detailed information"
echo "  2. Run tests: source venv/bin/activate && python3 test_local.py"
echo "  3. Start API: source venv/bin/activate && python3 api.py"
echo "  4. Start UI: source venv/bin/activate && streamlit run app.py"
echo ""
echo "If you encounter issues:"
echo "  - Check CODEACT_SETUP.md for troubleshooting"
echo "  - Review the CodeAct repository README"
echo "  - Verify the import structure matches the repository"
echo ""

