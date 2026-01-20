# Railway Build Optimization Guide

## Why Builds Take Long

Your build is installing **very large ML/AI packages**:
- **PyTorch** (~2-3 GB) - Deep learning framework
- **CUDA libraries** (~1-2 GB) - GPU support (nvidia-* packages)
- **Transformers** (~500 MB) - Hugging Face models
- **Sentence Transformers** (~300 MB) - ML models
- **Scikit-learn, SciPy, NumPy** (~200 MB) - Scientific computing

**Total download size: ~4-6 GB** - This is why it takes 5-10 minutes!

## Solution 1: Make ML Dependencies Optional (Recommended)

Create two requirements files:

### `requirements.txt` (Core - Fast Build)
```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.15.0
playwright>=1.40.0
webdriver-manager>=4.0.0
python-dotenv>=1.0.0
flask>=3.0.0
werkzeug>=3.0.0
PyPDF2>=3.0.0
python-docx>=1.1.0
pdfplumber>=0.10.0
flask-login>=0.6.3
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
gunicorn>=21.2.0
```

### `requirements-ml.txt` (ML Dependencies - Optional)
```txt
# Install only if ML features are needed
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.24.0
transformers>=4.30.0
torch>=2.0.0
```

Then update your code to gracefully handle missing ML libraries.

## Solution 2: Use CPU-Only PyTorch (Faster)

Replace in `requirements.txt`:
```txt
# Instead of: torch>=2.0.0
# Use CPU-only version (much smaller):
torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
```

This removes CUDA libraries (~1-2 GB saved).

## Solution 3: Accept the Wait (Current Approach)

The current build is **normal** - ML packages are just huge. Railway will cache dependencies after first build, making subsequent builds faster.

## Current Build Status

✅ **What's happening:**
- Installing 100+ packages
- Downloading ~4-6 GB of ML libraries
- This is **normal** and expected

⏱️ **Expected time:**
- First build: 5-10 minutes
- Subsequent builds: 2-5 minutes (cached)

## Recommendation

**For production:** Keep current setup - ML features are valuable
**For faster builds:** Use Solution 1 (optional ML) or Solution 2 (CPU-only PyTorch)
