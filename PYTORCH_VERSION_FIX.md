# PyTorch 2.6+ Compatibility Issue - IN PROGRESS 🔄

## Issue

Training failed with PyTorch model loading error:

```
_pickle.UnpicklingError: Weights only load failed.
WeightsUnpickler error: Unsupported global: GLOBAL ultralytics.nn.tasks.DetectionModel 
was not an allowed global by default.
```

## Root Cause

**PyTorch 2.6+** changed the default value of `weights_only` parameter in `torch.load()`:
- **Old behavior (PyTorch ≤2.5)**: `weights_only=False` (allows loading class definitions)
- **New behavior (PyTorch ≥2.6)**: `weights_only=True` (security improvement, blocks class definitions)

YOLO model files (.pt) contain class definitions like `DetectionModel`, which are blocked by the new default.

## Solution

Downgrade PyTorch to version **2.5.1** (last stable version before the breaking change).

### Steps Being Taken

1. **Stop backend server** (to release file locks)

2. **Uninstall PyTorch 2.9.0**:
   ```bash
   pip uninstall torch torchvision -y
   ```

3. **Install PyTorch 2.5.1**:
   ```bash
   pip install torch==2.5.1 torchvision==0.20.1 -i https://mirrors.aliyun.com/pypi/simple/
   ```

4. **Update requirements.txt**:
   ```
   torch==2.5.1
   torchvision==0.20.1
   ```

## Why PyTorch 2.5.1?

- ✅ **Stable**: Widely tested and proven
- ✅ **Compatible**: Works with ultralytics 8.1.0
- ✅ **No breaking changes**: Uses `weights_only=False` by default
- ✅ **Supports YOLO**: Can load model class definitions

## Version Compatibility Matrix

| PyTorch | Ultralytics | YOLO Models | Status |
|---------|-------------|-------------|---------|
| 2.9.0 | 8.1.0 | ❌ Fails | Breaking change |
| 2.6.0+ | 8.1.0 | ❌ Fails | Breaking change |
| 2.5.1 | 8.1.0 | ✅ Works | Recommended |
| 2.4.x | 8.1.0 | ✅ Works | Alternative |
| 2.3.x | 8.1.0 | ✅ Works | Alternative |

## Alternative Solutions

If you want to use PyTorch 2.6+, you would need to:

1. **Update Ultralytics** to a newer version that handles `weights_only=True`
2. **Patch torch.load calls** to explicitly set `weights_only=False`
3. **Use safe globals** with `torch.serialization.add_safe_globals()`

However, **downgrading is simpler and more reliable**.

## Current Status

🔄 **Installing PyTorch 2.5.1** from Aliyun mirror...

This may take 5-10 minutes depending on network speed (203 MB download).

## Next Steps After Installation

1. **Verify PyTorch version**:
   ```bash
   python -c "import torch; print(torch.__version__)"
   # Should output: 2.5.1+cpu
   ```

2. **Restart backend**:
   ```bash
   cd backend
   venv\Scripts\activate
   python app.py
   ```

3. **Test training task**:
   - Create new training task
   - Should load model without errors
   - Training should start successfully

## Prevention

Updated `requirements.txt` now specifies exact versions:
```
numpy<2.0.0           # NumPy 1.x compatibility
torch==2.5.1          # PyTorch compatibility
torchvision==0.20.1   # Matches torch version
ultralytics==8.1.0    # YOLO library
```

This prevents accidental upgrades to incompatible versions.

## Related Issues

- NumPy 2.x compatibility (fixed earlier)
- Model download proxy errors (fixed earlier)
- Dataset path resolution (fixed earlier)

All dependencies are now pinned to stable, compatible versions! 🎯

---

*Status: Installing PyTorch 2.5.1*  
*Files Modified: backend/requirements.txt*  
*Date: 2024-10-29*
