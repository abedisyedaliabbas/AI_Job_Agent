# AI Job Agent 🤖

An intelligent AI agent that helps you find jobs, match them to your profile, and generate personalized, natural-sounding cover letters for applications.

## Features

- 📋 **CV/Profile Management**: Extract and manage your CV data in a structured format
- 🔍 **Multi-Source Job Search**: Search jobs from LinkedIn, Indeed, Glassdoor, and more
- 🎯 **Smart Job Matching**: AI-powered matching algorithm that scores jobs based on your profile
- ✍️ **Natural Cover Letters**: Generate personalized cover letters that don't sound AI-generated
- 📊 **Application Tracking**: Track all your applications with detailed statistics
- 🤖 **Automation Ready**: Prepare applications automatically (manual submission for safety)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize your profile**:
```bash
python cv_parser.py
```
This will create a `profile.json` file from your CV data.

## Quick Start

### Run the Full Workflow
```bash
python ai_job_agent.py --full
```

This will:
1. Load your profile
2. Search for jobs based on your keywords
3. Match jobs to your profile
4. Generate cover letters for matched jobs
5. Show application statistics

### Individual Commands

**Search for jobs:**
```bash
python ai_job_agent.py --search --keywords "computational chemistry" "machine learning" --location "Singapore"
```

**Match existing jobs:**
```bash
python ai_job_agent.py --match
```

**Prepare applications:**
```bash
python ai_job_agent.py --apply --min-score 0.6
```

**View statistics:**
```bash
python ai_job_agent.py --stats
```

## Configuration

Edit `config.json` to customize:

- **search_keywords**: Keywords to search for jobs
- **location**: Preferred job location
- **min_match_score**: Minimum match score (0.0-1.0) for applications
- **api_keys**: API keys for job search platforms (optional)
- **cover_letter_style**: Style of cover letters (professional, enthusiastic, technical)

## How It Works

### 1. Profile Management
Your CV data is parsed and stored in a structured format (`profile.json`). The system extracts:
- Education history
- Work experience
- Skills and expertise
- Publications and achievements
- Contact information

### 2. Job Search
The agent provides multiple ways to find jobs:

**Automated Search (Limited):**
- Indeed (web scraping - may be blocked by anti-bot measures)
- JobStreet (for Singapore/SE Asia)
- LinkedIn (URL generation - requires API for full automation)
- Glassdoor (URL generation - requires API partnership)

**Manual Job Entry (Recommended):**
- Use `job_search_helper.py` to get search URLs for all major job boards
- Visit the URLs to find jobs manually
- Add jobs using `add_jobs_manual.py` or edit `jobs.json` directly

**Why Manual Entry?**
Most job boards block automated scraping to prevent abuse. The system provides:
- Pre-built search URLs for easy access
- Tools to manually add jobs you find
- Full automation for matching and cover letter generation once jobs are added

### 3. Job Matching
Each job is scored based on:
- **Skill matching** (40%): How well your skills match job requirements
- **Experience matching** (30%): Relevance of your work experience
- **Education matching** (15%): Alignment with required education level
- **Title/role matching** (10%): Fit with job title
- **Location matching** (5%): Location preferences

### 4. Cover Letter Generation
The system generates personalized cover letters that:
- Use natural, varied language (not AI-sounding)
- Highlight relevant experience and skills
- Show genuine interest in the role
- Include personal touches and variations
- Are saved as individual files for each application

### 5. Application Management
- Tracks all applications in `applications_log.json`
- Prevents duplicate applications
- Provides statistics on application success
- Prepares all materials for easy submission

## File Structure

```
.
├── ai_job_agent.py          # Main orchestrator
├── profile_manager.py        # Profile data management
├── cv_parser.py             # CV parsing and extraction
├── job_search.py            # Job search engine
├── job_matcher.py           # Job matching algorithm
├── cover_letter_generator.py # Cover letter generation
├── application_automator.py  # Application automation
├── config.json              # Configuration file
├── profile.json             # Your profile data (generated)
├── jobs.json                # Found jobs (generated)
├── applications_log.json    # Application history (generated)
└── requirements.txt         # Python dependencies
```

## API Setup (Optional)

For automated job searching, you'll need API keys:

### LinkedIn
1. Create a LinkedIn app at https://www.linkedin.com/developers/
2. Get OAuth 2.0 credentials
3. Add to `config.json`:
```json
"api_keys": {
  "linkedin": "your_access_token"
}
```

### Indeed
Indeed requires partnership for API access. Alternatively, you can use web scraping with proper rate limiting (be respectful of robots.txt).

## Cover Letter Quality

The cover letter generator uses:
- **Varied openings**: Multiple natural opening phrases
- **Personalized content**: Tailored to each job's requirements
- **Natural transitions**: Human-like sentence flow
- **Relevant examples**: Specific experience and achievements
- **Subtle variations**: Contractions and natural language patterns

## Safety & Ethics

⚠️ **Important Notes**:
- The system prepares applications but **does not auto-submit** by default
- Always review cover letters before submitting
- Respect rate limits when searching job boards
- Follow terms of service for all platforms
- Use responsibly and ethically

## Customization

### Adding Custom Job Sources
Edit `job_search.py` to add new job search methods:
```python
def search_custom_source(self, keywords, location):
    # Your implementation
    pass
```

### Customizing Cover Letter Style
Edit `cover_letter_generator.py` to modify:
- Opening phrases
- Transition words
- Closing statements
- Personalization logic

### Adjusting Match Algorithm
Edit `job_matcher.py` to change:
- Scoring weights
- Matching criteria
- Relevance calculations

## Troubleshooting

**Profile not loading:**
- Run `python cv_parser.py` first to create `profile.json`

**No jobs found:**
- Check your internet connection
- Verify API keys if using external services
- Try different keywords or location
- Check if job boards are accessible

**Cover letters sound too generic:**
- Edit `cover_letter_generator.py` to add more personalization
- Adjust the style in `config.json`
- Add more specific experience points to your profile

## Future Enhancements

- [ ] Automated application submission (with user approval)
- [ ] Email integration for application tracking
- [ ] Interview preparation assistance
- [ ] Salary negotiation guidance
- [ ] Multi-language support
- [ ] Resume customization per job
- [ ] Integration with more job boards

## License

This project is provided as-is for personal use. Please respect the terms of service of all job platforms and use responsibly.

## Support

For issues or questions, please review the code comments or customize the system to your needs.

---

**Good luck with your job search! 🚀**
