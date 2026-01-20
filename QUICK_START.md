# Quick Start Guide

## Setup (One-Time)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize your profile:**
   ```bash
   python cv_parser.py
   ```
   This creates `profile.json` from your CV data.

## Usage

### Recommended Workflow: Manual Job Entry

**1. Get search URLs:**
```bash
python job_search_helper.py "computational chemistry" "machine learning"
```
This shows you search URLs for LinkedIn, Indeed, JobStreet, and more.

**2. Find jobs manually:**
- Visit the URLs provided
- Browse and find jobs you're interested in
- Copy job URLs

**3. Add jobs:**
```bash
python add_jobs_manual.py
```
Follow the prompts to add jobs, or edit `jobs.json` directly.

**4. Match and generate cover letters:**
```bash
python ai_job_agent.py --match
python ai_job_agent.py --apply --min-score 0.6
```

### Alternative: Automated Search (Limited)

**Full workflow:**
```bash
python ai_job_agent.py --full
```

**Step-by-step:**
```bash
# Search (may find 0 jobs due to anti-scraping measures)
python ai_job_agent.py --search --keywords "computational chemistry" "machine learning" --location "Singapore"

# Match existing jobs
python ai_job_agent.py --match

# Generate cover letters
python ai_job_agent.py --apply --min-score 0.6

# View statistics
python ai_job_agent.py --stats
```

**Note:** Automated scraping often gets blocked. Use manual entry for best results!

## Configuration

Edit `config.json` to customize:
- Search keywords
- Location preferences
- Minimum match score
- API keys (for automated job searching)

## Output Files

- `profile.json` - Your profile data
- `jobs.json` - Found jobs
- `applications_log.json` - Application history
- `cover_letter_*.txt` - Generated cover letters

## Next Steps

1. **Review generated cover letters** - Always review and customize before submitting
2. **Add API keys** - For automated job searching from LinkedIn, Indeed, etc.
3. **Customize keywords** - Update `config.json` with your preferred job search terms
4. **Adjust match score** - Lower the `min_match_score` to see more jobs, or raise it for higher quality matches

## Tips

- Cover letters are saved as individual files for easy review
- The system prevents duplicate applications
- Match scores help you prioritize which jobs to apply for
- You can manually add jobs to `jobs.json` if you find them elsewhere

## Need Help?

- Check `README.md` for detailed documentation
- Review `example_usage.py` for code examples
- Customize the modules in the source code to fit your needs
