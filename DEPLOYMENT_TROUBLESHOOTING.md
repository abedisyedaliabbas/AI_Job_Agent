# Deployment Troubleshooting Guide

## Common Deployment Failures

### 1. Build Succeeds but Deployment Fails

**Symptoms:**
- Build logs show "Successfully installed..."
- Deployment shows "Failed"

**Common Causes:**

#### Missing Environment Variables
- Check Railway → Variables tab
- Ensure all required variables are set:
  - `SECRET_KEY` (REQUIRED)
  - `FLASK_ENV=production`
  - `GOOGLE_CLIENT_ID` (optional)
  - `GOOGLE_CLIENT_SECRET` (optional)

#### Import Errors
- Check "Deploy Logs" (not Build Logs)
- Look for `ModuleNotFoundError` or `ImportError`
- Ensure all Python files are committed to GitHub

#### Port Binding Issues
- Railway sets `PORT` automatically
- Ensure `gunicorn_config.py` uses: `os.environ.get('PORT', '5000')`

#### Missing Directories
- App creates directories automatically, but check:
  - `uploads/` directory exists
  - `data/` directory exists
  - `static/cover_letters/` exists

### 2. How to Check Deploy Logs

1. Go to Railway → Your Project
2. Click on the failed deployment
3. Click "Deploy Logs" tab (NOT "Build Logs")
4. Scroll to the bottom for the error message

### 3. Common Error Messages

#### "ModuleNotFoundError: No module named 'X'"
- **Fix:** Add missing package to `requirements.txt`
- **Fix:** Ensure file is committed to GitHub

#### "Address already in use"
- **Fix:** Railway handles this automatically, but check `PORT` variable

#### "SECRET_KEY not set"
- **Fix:** Add `SECRET_KEY` to Railway Variables

#### "ImportError: cannot import name 'X'"
- **Fix:** Check import statements in `app.py`
- **Fix:** Ensure all dependencies are in `requirements.txt`

### 4. Quick Fixes

#### Rebuild from Scratch
1. Railway → Settings → Delete Service
2. Create new service
3. Deploy from GitHub again

#### Check File Structure
Ensure these files exist:
- `app.py`
- `Procfile`
- `requirements.txt`
- `runtime.txt`
- `gunicorn_config.py`

#### Verify Procfile
Should contain:
```
web: gunicorn --config gunicorn_config.py app:app
```

### 5. Testing Locally Before Deploy

```bash
# Test with Gunicorn (same as production)
pip install gunicorn
gunicorn --config gunicorn_config.py app:app

# Check for import errors
python -c "from app import app; print('OK')"
```

### 6. Railway-Specific Issues

#### Build Timeout
- ML packages are large (~4-6 GB)
- First build: 5-10 minutes is normal
- Subsequent builds: 2-5 minutes (cached)

#### Memory Issues
- Railway free tier: 512 MB RAM
- ML models can use 200-300 MB
- If crashes, consider removing ML dependencies

#### Disk Space
- Railway free tier: 1 GB disk
- ML packages use ~500 MB
- Should be fine, but monitor usage

### 7. Getting Help

1. **Check Deploy Logs** - Most errors are here
2. **Check Build Logs** - For dependency issues
3. **Test Locally** - Reproduce error locally
4. **Railway Support** - Use "Get Help" button in Railway dashboard
