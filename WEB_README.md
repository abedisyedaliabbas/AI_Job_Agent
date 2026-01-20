# Web Application - AI Job Agent

A web-based interface for automated job search and application.

## Features

- 📄 **Resume Upload**: Upload PDF, DOCX, or TXT resumes
- 🔍 **Job Search**: Search jobs worldwide with filters
- 🎯 **Smart Matching**: AI matches jobs to your profile
- ✍️ **Cover Letters**: Auto-generate personalized cover letters
- 📊 **Dashboard**: Track all your applications
- 🌐 **Multi-Source**: Search across multiple job boards

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create necessary directories:**
```bash
mkdir -p uploads static/cover_letters data
```

3. **Set environment variable (optional):**
```bash
export SECRET_KEY='your-secret-key-here'
```

## Running the Application

### Development Mode

```bash
python run_web.py
```

Or directly:
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Usage

### 1. Upload Resume

1. Go to **Upload Resume** page
2. Drag & drop or select your resume file (PDF, DOCX, or TXT)
3. Wait for parsing to complete
4. Review extracted profile information

### 2. Search Jobs

1. Go to **Search Jobs** page
2. Enter keywords (e.g., "computational chemistry", "machine learning")
3. Set location, job type, salary filters
4. Click "Search Jobs" or "Get Search URLs" for manual search

### 3. Match Jobs

1. Go to **My Jobs** page
2. Select jobs you're interested in
3. Click "Match to Profile" to see match scores
4. Jobs are automatically scored based on your profile

### 4. Apply

1. Select jobs you want to apply for
2. Click "Apply to Selected"
3. Cover letters are generated automatically
4. Download cover letters and submit manually (most job boards block automation)

### 5. Dashboard

- View statistics
- Track applications
- Monitor job search progress

## API Endpoints

- `GET /` - Home page
- `GET/POST /upload` - Upload resume
- `GET/POST /search` - Search jobs
- `GET /jobs` - List all jobs
- `POST /match` - Match jobs to profile
- `POST /apply` - Apply to jobs
- `GET /dashboard` - User dashboard
- `POST /api/search_urls` - Get search URLs

## File Structure

```
.
├── app.py                 # Main Flask application
├── run_web.py            # Run script
├── resume_parser.py       # Resume parsing (PDF/DOCX/TXT)
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── search.html
│   ├── jobs.html
│   └── dashboard.html
├── uploads/              # Uploaded resumes
├── static/               # Static files
│   └── cover_letters/   # Generated cover letters
└── data/                 # User data
```

## Limitations

1. **Automated Applications**: Most job boards block automated submissions. The system generates cover letters, but you'll need to submit manually.

2. **Resume Parsing**: Basic parsing is implemented. For better results, consider:
   - Using ML-based resume parsers
   - Manual profile editing
   - Structured resume formats

3. **Job Search**: Automated scraping is often blocked. Use "Get Search URLs" for manual search.

## Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Implement proper user authentication
- Validate all file uploads
- Sanitize user inputs

## Troubleshooting

**Resume not parsing correctly?**
- Try a different file format
- Ensure resume is well-formatted
- Manually edit profile in `data/profile_*.json`

**No jobs found?**
- Use "Get Search URLs" for manual search
- Add jobs manually via the interface
- Check your search keywords

**Cover letters not generating?**
- Ensure resume is uploaded
- Check that profile data is complete
- Review error messages in console

## Future Enhancements

- [ ] User authentication and accounts
- [ ] Advanced resume parsing with ML
- [ ] Email notifications
- [ ] Application status tracking
- [ ] Integration with more job boards
- [ ] Resume customization per job
- [ ] Interview preparation tools

## Support

For issues or questions, check the main README.md or review the code comments.
