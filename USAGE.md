# DataGPU Usage Guide

## Quick Reference

### Running Commands

Since you have a virtual environment, always use one of these methods:

**Option 1: Activate venv first (Recommended)**
```bash
source .venv/bin/activate
python examples/quickstart.py
datagpu compile data.csv
```

**Option 2: Use venv python directly**
```bash
.venv/bin/python examples/quickstart.py
.venv/bin/python -m datagpu.cli compile data.csv
```

**Option 3: Use the helper script**
```bash
./run.sh examples/quickstart.py
```

### Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run quickstart
python examples/quickstart.py

# Generate sample data
python examples/generate_sample_data.py

# Run benchmarks
python examples/benchmark.py

# Compile a dataset
datagpu compile examples/data/small_test.csv --out compiled/

# View dataset info
datagpu info compiled/manifest.yaml

# List cache
datagpu cache-list

# Run tests
pytest
```

### Troubleshooting

**Error: ModuleNotFoundError: No module named 'datagpu'**

This means you're using the wrong Python interpreter. Solutions:

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Or use the venv Python directly:
   ```bash
   .venv/bin/python your_script.py
   ```

3. Verify which Python you're using:
   ```bash
   which python
   # Should show: /home/kcelestinomaria/startuprojects/datagpu/.venv/bin/python
   ```

**Error: command not found: datagpu**

The CLI is only available when the venv is activated:
```bash
source .venv/bin/activate
datagpu version
```

Or use:
```bash
.venv/bin/python -m datagpu.cli version
```

### Development Workflow

```bash
# 1. Activate venv
source .venv/bin/activate

# 2. Make changes to code

# 3. Test changes
pytest

# 4. Run examples
python examples/quickstart.py

# 5. Deactivate when done
deactivate
```

### Installation Reminder

If you need to reinstall:
```bash
source .venv/bin/activate
pip install -e .
```

Or create a fresh venv:
```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
