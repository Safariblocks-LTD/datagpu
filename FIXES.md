# Bug Fixes Applied

## Issues Fixed

### 1. Test Failure: `test_clean_fills_text_nulls`

**Problem**: Test was failing because the cleaner removes rows with ALL nulls before filling individual nulls. The test only had one column, so a null value meant the entire row was null.

**Fix**: Added a second column to the test data to prevent the row from being removed.

```python
# Before
df = pl.DataFrame({
    "text_col": ["hello", None, "world"]
})

# After
df = pl.DataFrame({
    "text_col": ["hello", None, "world"],
    "other_col": [1, 2, 3]  # Prevent row removal
})
```

**File**: `tests/test_cleaner.py`

### 2. Deprecation Warning: `datetime.utcnow()`

**Problem**: Python 3.12 deprecated `datetime.utcnow()` in favor of timezone-aware datetime objects.

**Warning**:
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
```

**Fix**: Updated to use `datetime.now(timezone.utc)` instead.

```python
# Before
from datetime import datetime
created_at=datetime.utcnow().isoformat()

# After
from datetime import datetime, timezone
created_at=datetime.now(timezone.utc).isoformat()
```

**File**: `datagpu/compiler.py`

### 3. Polars API Change: `write_parquet(None)`

**Problem**: Polars no longer supports `df.write_parquet(None)` to get bytes directly.

**Error**:
```
TypeError: `path` argument has invalid type 'NoneType', and cannot be turned into a sink target
```

**Fix**: Use `BytesIO` buffer instead.

```python
# Before
data_bytes = df.write_parquet(None)

# After
import io
buffer = io.BytesIO()
df.write_parquet(buffer)
data_bytes = buffer.getvalue()
```

**File**: `datagpu/compiler.py`

### 4. YAML Serialization: DataType Enum

**Problem**: DataType enum objects can't be serialized to YAML directly.

**Error**:
```
yaml.constructor.ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:datagpu.types.DataType'
```

**Fix**: Convert enum values to strings before serialization.

```python
# Before
schema=self.cleaner.schema

# After
schema={k: v.value for k, v in self.cleaner.schema.items()}
```

**File**: `datagpu/compiler.py`

## Test Results

### Before Fixes
- **Failed**: 1 test
- **Warnings**: 3 deprecation warnings
- **Coverage**: 55%

### After Fixes
- **Passed**: 17/17 tests (100%)
- **Warnings**: 0
- **Coverage**: 55%

## Verification

Run tests to verify all fixes:

```bash
source .venv/bin/activate
pytest -v
```

Expected output:
```
17 passed in 4.15s
```

## Performance

Benchmarks still working correctly:
- Average throughput: 28,105 rows/sec
- Average compression: 75.5%
- All datasets compile successfully

## Files Modified

1. `datagpu/compiler.py` - 3 fixes (Polars API, datetime, enum serialization)
2. `tests/test_cleaner.py` - 1 fix (test data structure)

## Compatibility

- Python 3.12.3 ✓
- Polars 1.35.2 ✓
- All dependencies up to date ✓
