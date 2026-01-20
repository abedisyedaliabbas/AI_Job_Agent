# AI Job Agent 🤖

An intelligent, AI-powered job search and application automation platform that helps job seekers find and apply to positions worldwide using machine learning and browser automation.

## ✨ Features

- **🤖 AI-Powered Job Discovery**: ML-based semantic search across 10+ job boards
- **🎯 Intelligent Job Matching**: 85-95% accuracy using sentence transformers and vector embeddings
- **📄 Smart Resume Parsing**: Multi-parser system with OCR error correction and skill extraction
- **🌍 Global Job Search**: Searches LinkedIn, Indeed, Glassdoor, JobStreet, Reed, and more
- **✍️ Cover Letter Generation**: Personalized, natural-sounding cover letters
- **🚀 Automated Applications**: End-to-end browser automation for job applications
- **📊 Analytics Dashboard**: Skill insights, market trends, and job statistics
- **🔐 Secure Authentication**: Email/password and Google OAuth 2.0

## 🛠️ Tech Stack

- **Backend**: Flask, Python 3.12
- **AI/ML**: Sentence Transformers, Scikit-learn, Transformers, PyTorch
- **Frontend**: Bootstrap 5, Chart.js, jQuery
- **Automation**: Selenium, BeautifulSoup, WebDriver Manager
- **Authentication**: Flask-Login, Google OAuth 2.0
- **Deployment**: Gunicorn, Railway/Heroku ready

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Chrome/Chromium (for browser automation)
- Google OAuth credentials (optional, for Google Sign-in)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI_Job_Agent.git
cd AI_Job_Agent

# Install dependencies
pip install -r requirements.txt

# Optional: Install ML dependencies for enhanced matching
pip install sentence-transformers scikit-learn torch
```

### Configuration

1. **Create `.env` file**:
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Create .env file with:
SECRET_KEY=your_generated_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id (optional)
GOOGLE_CLIENT_SECRET=your_google_client_secret (optional)
```

2. **Google OAuth Setup** (Optional):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `http://localhost:5000/auth/google/callback`

### Run Locally

```bash
python run_web.py
```

Visit: `http://localhost:5000`

## 📁 Project Structure

```
├── app.py                      # Main Flask application
├── auto_job_agent.py           # AI agent orchestrator
├── ml_job_matcher.py           # ML-powered job matching
├── ai_job_search.py            # AI-based job search
├── ai_job_discovery.py         # ML job discovery
├── comprehensive_job_search.py  # Multi-source job search (10+ boards)
├── auto_apply_engine.py        # Browser automation
├── resume_parser_v2.py         # Intelligent resume parsing
├── enhanced_skill_parser.py    # Advanced skill extraction
├── google_job_search.py        # Google-based job search
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
├── data/                       # User data (gitignored)
└── uploads/                    # Resume uploads (gitignored)
```

## 🎯 Key Components

### ML Job Matcher
- **Semantic Similarity**: Sentence transformers for profile-job matching
- **Vector Embeddings**: FAISS-based similarity search
- **Weighted Scoring**: 60% semantic, 25% skills, 15% experience
- **Automatic Fallback**: Falls back to keyword matching if ML unavailable

### Comprehensive Job Search
- **10+ Sources**: LinkedIn, Indeed, Glassdoor, Monster, ZipRecruiter, JobStreet, Reed, Adzuna, MyCareersFuture, JobsDB
- **Parallel Processing**: Concurrent searches for speed
- **Smart Prioritization**: Company websites > Job boards > LinkedIn
- **Deduplication**: URL and title-based duplicate removal

### Auto Apply Engine
- **End-to-End Automation**: Login, form filling, submission
- **Multi-Step Forms**: Handles complex application flows
- **Platform Support**: LinkedIn Easy Apply, Indeed, Greenhouse, generic forms
- **Error Recovery**: Automatic retry and fallback mechanisms

### Intelligent Resume Parser
- **Multi-Parser System**: V2 → Intelligent → Improved → Original
- **OCR Error Correction**: Fixes common PDF parsing errors
- **Skill Extraction**: 200+ known technical skills database
- **Section Detection**: Education, experience, publications, skills

## 🌐 Deployment

### Railway

1. **Connect Repository**:
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Set Environment Variables**:
   ```
   SECRET_KEY=your_secret_key
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   FLASK_ENV=production
   PORT=5000
   ```

3. **Deploy**:
   - Railway auto-detects `Procfile` and `runtime.txt`
   - App will be live at `https://your-app.railway.app`

### Heroku

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your_secret_key
git push heroku main
```

### Render

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables

## 📊 Features in Detail

### AI Job Discovery
- Uses ML to discover company websites
- Semantic search for job opportunities
- Extracts jobs from company career pages

### Smart Keyword Extraction
- Filters out generic words (successfully, performance, etc.)
- Prioritizes technical skills and compound terms
- Automatic fallback to simpler keywords

### Dashboard Analytics
- Resume quality score
- Profile completeness
- Skill distribution charts
- Global market insights
- Job opportunities by country

## 🔒 Security

- Environment variables for sensitive data
- Flask-Login for session management
- Password hashing (bcrypt)
- OAuth 2.0 for Google authentication
- User data isolation (per-user files)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using AI and Machine Learning**
