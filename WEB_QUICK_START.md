# Web Application - Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run_web.py
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

## 📋 Complete Workflow

### 1. Upload Your Resume
- Click "Upload Resume" in the navigation
- Drag & drop your PDF/DOCX/TXT resume
- Wait for parsing (profile extracted automatically)

### 2. Search for Jobs
- Click "Search Jobs"
- Enter keywords (e.g., "computational chemistry", "machine learning")
- Set location (e.g., "Singapore")
- Click "Search Jobs" or "Get Search URLs"

### 3. Match Jobs to Your Profile
- Go to "My Jobs"
- Select jobs you're interested in
- Click "Match to Profile" to see match scores

### 4. Apply to Jobs
- Select jobs you want to apply for
- Click "Apply to Selected"
- Cover letters are generated automatically
- Download cover letters and submit manually

### 5. Track Applications
- Go to "Dashboard" to see statistics
- View all your applications in one place

## 🎯 Key Features

✅ **Resume Upload**: Supports PDF, DOCX, TXT  
✅ **Job Search**: Multiple job boards with filters  
✅ **Smart Matching**: AI scores jobs against your profile  
✅ **Cover Letters**: Auto-generated, personalized  
✅ **Dashboard**: Track everything in one place  

## ⚠️ Important Notes

1. **Automated Applications**: Most job boards block automation. The system generates cover letters, but you'll need to submit manually.

2. **Resume Parsing**: Basic parsing is implemented. For best results:
   - Use well-formatted resumes
   - Review extracted profile
   - Manually edit if needed

3. **Job Search**: Automated scraping may be blocked. Use "Get Search URLs" for manual search on job boards.

## 🔧 Troubleshooting

**Can't upload resume?**
- Check file format (PDF, DOCX, or TXT)
- Ensure file size < 16MB
- Try a different file format

**No jobs found?**
- Use "Get Search URLs" button
- Add jobs manually
- Check your keywords

**Cover letters not generating?**
- Ensure resume is uploaded
- Check profile is complete
- Review error messages

## 📚 More Information

- See `WEB_README.md` for detailed documentation
- See `README.md` for CLI usage
- Check code comments for implementation details

## 🎉 You're Ready!

Start the server and begin your automated job search journey!

```bash
python run_web.py
```
