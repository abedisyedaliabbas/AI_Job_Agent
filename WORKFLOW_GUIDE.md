# Complete Workflow Guide

## Overview

Since most job boards block automated scraping, here's the recommended workflow:

## Step 1: Get Search URLs

```bash
python job_search_helper.py "computational chemistry" "machine learning"
```

This generates search URLs for:
- LinkedIn
- Indeed Singapore
- JobStreet Singapore
- Glassdoor
- MyCareersFuture (Singapore government job portal)
- JobsDB Singapore

## Step 2: Find Jobs Manually

1. Visit the URLs provided
2. Browse and find jobs that interest you
3. For each job, note:
   - Job title
   - Company name
   - Location
   - Job URL
   - Description (copy from the posting)
   - Requirements (list key requirements)

## Step 3: Add Jobs

### Option A: Interactive Entry
```bash
python add_jobs_manual.py
```
Follow the prompts to enter job details.

### Option B: Edit jobs.json Directly
Open `jobs.json` and add entries like this:

```json
{
  "title": "Computational Chemistry Research Scientist",
  "company": "Tech Research Labs",
  "location": "Singapore",
  "description": "We are seeking a computational chemistry researcher...",
  "requirements": [
    "PhD in Computational Chemistry",
    "Experience with DFT calculations",
    "Python programming skills"
  ],
  "url": "https://example.com/job/123",
  "source": "manual"
}
```

## Step 4: Match Jobs to Your Profile

```bash
python ai_job_agent.py --match
```

This will:
- Score each job against your profile (0-100%)
- Show top matches
- Save match scores

## Step 5: Generate Cover Letters

```bash
python ai_job_agent.py --apply --min-score 0.6
```

This will:
- Generate personalized cover letters for jobs with match score ≥ 60%
- Save each cover letter as a separate file
- Track applications in `applications_log.json`

## Step 6: Review and Submit

1. Review generated cover letters in `cover_letter_*.txt` files
2. Customize if needed
3. Submit applications manually through the job board websites

## Quick Commands Reference

```bash
# Get search URLs
python job_search_helper.py "keyword1" "keyword2"

# Add jobs manually
python add_jobs_manual.py

# Match jobs
python ai_job_agent.py --match

# Generate cover letters
python ai_job_agent.py --apply --min-score 0.6

# View statistics
python ai_job_agent.py --stats

# Full workflow (if automated search works)
python ai_job_agent.py --full
```

## Tips

1. **Start with high match scores**: Use `--min-score 0.7` for jobs that closely match your profile
2. **Review cover letters**: Always customize before submitting
3. **Track applications**: Check `applications_log.json` to avoid duplicates
4. **Update profile**: Keep `profile.json` updated with new skills/experience
5. **Use multiple sources**: Check all the job boards for best coverage

## Troubleshooting

**No jobs found?**
- This is normal - job boards block automated scraping
- Use manual entry instead
- Run `python job_search_helper.py` to get search URLs

**Cover letters sound generic?**
- Edit `cover_letter_generator.py` to add more personalization
- Add more specific experience points to your profile

**Match scores too low?**
- Lower the `min_match_score` in `config.json`
- Or use `--min-score 0.4` when applying
