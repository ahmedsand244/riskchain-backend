# Deployment Guide - RiskChain Backend

## Quick Deploy to Render (Free)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/riskchain-backend.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will detect `render.yaml` and create:
   - Web Service (Python)
   - PostgreSQL Database (Free)
5. Click "Apply" - it auto-deploys!

### 3. Set Environment Variables (in Render Dashboard)
- `SECRET_KEY` - Auto-generated
- `ALLOWED_HOSTS` - `.onrender.com` (or your custom domain)
- `DEBUG` - `False`
- `DJANGO_SETTINGS_MODULE` - `riskchain_backend.settings`

### 4. Run Migrations (in Render Shell)
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # optional
```

---

## Alternative: Railway

1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Add PostgreSQL plugin
4. Set env vars (same as above)
5. Deploy!

---

## Local Development

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your values

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

---

## Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | `True` for dev, `False` for prod | Yes |
| `ALLOWED_HOSTS` | Comma-separated hosts | Yes |
| `DATABASE_URL` | PostgreSQL URL (auto-set by Render/Railway) | Prod only |
| `GOOGLE_CLIENT_ID` | For Google OAuth | Optional |
| `GOOGLE_CLIENT_SECRET` | For Google OAuth | Optional |

---

## Project Structure
```
riskchain_backend/
├── api/                 # Main app
├── riskchain_backend/   # Django project settings
├── media/               # Uploaded files
├── staticfiles/         # Collected static files
├── manage.py
├── requirements.txt
├── render.yaml          # Render deployment config
└── .env.example         # Environment template
```

---

## Troubleshooting

**Static files not loading?**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATICFILES_STORAGE` in settings

**Database errors?**
- Check `DATABASE_URL` format: `postgres://user:pass@host:port/db`
- Run migrations: `python manage.py migrate`

**CORS errors?**
- Update `CORS_ALLOWED_ORIGINS` in settings for production domains