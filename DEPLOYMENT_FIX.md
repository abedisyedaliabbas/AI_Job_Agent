# Railway Build Timeout Fix

## Problem
The Railway build was timing out during Docker image upload because ML dependencies (PyTorch, transformers, etc.) create a ~4-6 GB image that takes too long to upload.

## Solution Applied
Temporarily disabled ML dependencies in `requirements.txt` to reduce image size. The app already handles missing ML libraries gracefully and will use keyword-based matching as a fallback.

## Current Status
- ✅ Build should now complete successfully
- ✅ App will work with reduced ML features (keyword matching)
- ⚠️ Advanced ML matching temporarily disabled

## To Re-enable ML Features (After Successful Deploy)

### Option 1: Install CPU-only PyTorch (Recommended)
This reduces image size by ~2-3 GB:

1. Add to Railway environment variables or build script:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

2. Then uncomment ML dependencies in `requirements.txt`

### Option 2: Use Separate ML Service
- Keep main app lightweight
- Deploy ML features as separate microservice
- Call ML service via API when needed

### Option 3: Upgrade Railway Plan
- Paid plans have longer build timeouts
- Allows full ML dependencies

## Files Modified
- `requirements.txt` - Commented out ML dependencies
- `.railwayignore` - Added to exclude unnecessary files from build

## Testing
After deployment, verify:
1. App starts successfully
2. Job search works (keyword-based matching)
3. Job matching works (fallback mode)
4. No errors in logs about missing ML libraries

