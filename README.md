# AI Job Agent

An intelligent job search and application automation platform powered by AI and machine learning.

## Features

- **AI-Powered Job Matching**: Uses semantic similarity and ML algorithms for accurate job matching (85-95% accuracy)
- **Intelligent Resume Parsing**: Multi-parser system with OCR error correction
- **Automated Job Search**: Searches across 10+ job boards (LinkedIn, Indeed, Glassdoor, etc.)
- **Smart Application**: Browser automation for end-to-end application submission
- **Cover Letter Generation**: Personalized, natural-sounding cover letters
- **User Dashboard**: Analytics, skill insights, and global market trends

## Tech Stack

- **Backend**: Flask, Python
- **AI/ML**: Sentence Transformers, Scikit-learn, Transformers
- **Frontend**: Bootstrap, Chart.js, jQuery
- **Automation**: Selenium, BeautifulSoup
- **Authentication**: Flask-Login, Google OAuth 2.0

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`
2. Generate `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Add your Google OAuth credentials (optional)

### Run

```bash
python run_web.py
```

Visit: `http://localhost:5000`

## Project Structure

```
├── app.py                      # Main Flask application
├── ml_job_matcher.py           # ML-powered job matching
├── ai_job_search.py            # AI-based job search
├── auto_apply_engine.py         # Browser automation
├── comprehensive_job_search.py # Multi-source job search
├── resume_parser_v2.py         # Intelligent resume parsing
├── templates/                  # HTML templates
├── static/                     # Static files
└── data/                       # User data (gitignored)
```

## Key Components

### ML Job Matcher
- Semantic similarity using sentence transformers
- Vector embeddings for profile and job descriptions
- Weighted scoring: 60% semantic, 25% skills, 15% experience

### Auto Apply Engine
- End-to-end browser automation
- Handles login, form filling, and submission
- Supports LinkedIn, Indeed, Greenhouse, and generic forms

### Comprehensive Job Search
- Searches 10+ job boards in parallel
- Prioritizes company websites over job boards
- Handles 1000+ jobs with deduplication

## Deployment

See deployment configuration files:
- `Procfile` - Railway/Heroku
- `gunicorn_config.py` - Production server
- `runtime.txt` - Python version

## License

MIT License
