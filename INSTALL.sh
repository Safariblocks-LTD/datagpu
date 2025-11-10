#!/bin/bash
# DataGPU Installation Script

set -e

echo "=================================="
echo "DataGPU Installation"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.11+
required_version="3.11"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11 or higher is required"
    exit 1
fi

echo "Python version OK"
echo ""

# Create virtual environment (optional)
read -p "Create virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment activated"
    echo ""
fi

# Install package
echo "Installing DataGPU..."
pip install --upgrade pip
pip install -e .

echo ""
echo "Installation complete!"
echo ""

# Verify installation
echo "Verifying installation..."
if command -v datagpu &> /dev/null; then
    datagpu version
    echo ""
    echo "=================================="
    echo "Installation successful!"
    echo "=================================="
    echo ""
    echo "Quick start:"
    echo "  1. Generate sample data:"
    echo "     python examples/generate_sample_data.py"
    echo ""
    echo "  2. Run quickstart example:"
    echo "     python examples/quickstart.py"
    echo ""
    echo "  3. Compile a dataset:"
    echo "     datagpu compile examples/data/small_test.csv --out compiled/"
    echo ""
    echo "  4. Run tests:"
    echo "     pytest"
    echo ""
    echo "Documentation: README.md"
    echo "Quick guide: QUICKSTART.md"
    echo ""
else
    echo "Warning: datagpu command not found in PATH"
    echo "You may need to restart your shell or add pip's bin directory to PATH"
fi
