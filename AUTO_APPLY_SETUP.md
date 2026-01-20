# Auto-Apply Setup Guide

## What Changed

The system now **actually submits applications** using browser automation! No more manual work - the AI agent fills forms and you just review and click submit.

## How It Works

1. **Browser Automation**: Uses Selenium to open job postings and fill application forms
2. **Smart Form Detection**: Automatically detects and fills common fields (name, email, phone, cover letter)
3. **Multi-Platform Support**: Works with LinkedIn, Indeed, Greenhouse, Lever, SmartRecruiters, and generic forms
4. **Review & Submit**: Browser opens with form pre-filled - you review and click submit

## Setup Instructions

### 1. Install ChromeDriver

```bash
pip install webdriver-manager
```

Or manually:
- Download ChromeDriver from: https://chromedriver.chromium.org/
- Make sure Chrome browser is installed
- Add ChromeDriver to your PATH

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test Auto-Apply

1. Upload your resume
2. Search for jobs
3. Click "Apply All" or "Apply Selected"
4. Review the modal - it now says "Auto-Apply Enabled"
5. Click "Confirm & Prepare Application"
6. Browser windows will open with forms pre-filled
7. Review each form and click submit

## What Happens

### Success Cases:
- ✅ **Form Filled**: Browser opens with all fields filled → You review and submit
- ✅ **Partially Filled**: Some fields filled → You complete the rest
- ✅ **Submitted**: Fully automated (rare, depends on job board)

### Fallback Cases:
- ⚠️ **Manual Required**: If automation fails, you get download links for cover letters
- ⚠️ **CAPTCHA**: Some sites require human verification (you'll need to solve it)

## Supported Job Boards

- ✅ **LinkedIn**: Easy Apply forms
- ✅ **Indeed**: Standard application forms
- ✅ **Greenhouse**: ATS forms
- ✅ **Lever**: ATS forms
- ✅ **SmartRecruiters**: Application forms
- ✅ **Generic**: Tries to detect and fill common fields

## Important Notes

1. **Browser Windows**: The system opens browser windows - don't close them until you've reviewed/submitted
2. **Review Required**: Always review filled forms before submitting (check for errors)
3. **CAPTCHAs**: Some sites show CAPTCHAs - you'll need to solve them manually
4. **Rate Limiting**: Don't apply to too many jobs at once (may trigger anti-bot measures)

## Troubleshooting

### "Browser automation not available"
- Install ChromeDriver: `pip install webdriver-manager`
- Make sure Chrome browser is installed
- Check that ChromeDriver is in your PATH

### "Could not find application form"
- The job may use a non-standard form
- Try applying manually using the cover letter download

### "Selenium not installed"
```bash
pip install selenium webdriver-manager
```

## Privacy & Ethics

- ✅ Only uses your provided information
- ✅ You review before submitting
- ✅ Respects job board terms of service
- ✅ No spam or mass applications

## Next Steps

1. Install ChromeDriver
2. Test with 1-2 jobs first
3. Review the filled forms
4. Submit if everything looks good
5. Scale up once comfortable

Enjoy automated job applications! 🚀
