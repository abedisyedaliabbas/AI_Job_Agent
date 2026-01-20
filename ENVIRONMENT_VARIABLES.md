# Environment Variables for Railway Deployment

Copy these to **Railway → Your Project → Variables** tab:

```
SECRET_KEY=f2b3d949f6b0faacc83a7a2d41d56baa2f1c166c76a16eb01c988b6149d43a4d
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FLASK_ENV=production
```

## How to Generate SECRET_KEY

If you need a new SECRET_KEY, run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Notes

- `SECRET_KEY` is **REQUIRED** - Flask uses this for session security
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are **OPTIONAL** - only needed for Google Sign-in
- `FLASK_ENV=production` enables production mode
- `PORT` is automatically set by Railway
