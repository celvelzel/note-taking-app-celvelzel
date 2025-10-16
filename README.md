# NoteTaker - Personal Note Management Application

A lightweight Flask-based notes API and single-page frontend. The project provides CRUD for notes plus AI-powered features including key information extraction, multi-language translation, and intelligent quiz generation powered by GitHub AI (OpenAI-compatible) client wrapper.

The application is deployed and accessible at: https://note-taking-app-celvelzel.vercel.app/

## Key points (what's actually implemented)

- Backend: Flask app in `src/main.py`, exposed to Vercel via `api/index.py` which imports the Flask `app` and provides a WSGI `wsgi_handler`.
- Data models: `src/models/note.py` and `src/models/user.py` using SQLAlchemy (db instance in `src/models/user.py`).
- Routes (blueprints): `src/routes/note.py` (notes CRUD, search, AI extract, translation, quiz) and `src/routes/user.py` (basic user CRUD).
- AI service: `src/services/ai_service.py` implements a GitHub AI client wrapper that requires `GITHUB_TOKEN` and uses an OpenAI-compatible client to call GitHub's inference endpoint.

## Features

- **Notes CRUD** (create/read/update/delete)
- **Search** by title/content
- **AI Information Extraction** (`POST /api/notes/extract-info`) - calls GitHub AI to extract structured info from note content and saves it to `extracted_info` field
- **AI Translation** (`POST /api/notes/translate`) - translate note content to multiple languages (Chinese, English, Japanese, Spanish, French, German) with persistent storage
- **AI Quiz Generation** (`POST /api/notes/generate-quiz`) - automatically generate multiple-choice questions based on note content to help reinforce learning
- **Interactive Frontend** - serves a responsive single-page application from `src/static/` with split-panel layout for original content and AI-assisted features

## Project structure

```
note-taking-app-celvelzel/
├─ api/
│  └─ index.py            # Vercel adapter (exports Flask app + wsgi_handler)
├─ src/
│  ├─ main.py             # Flask app entry (registers blueprints, DB init)
│  ├─ static/             # Frontend files served by Flask
│  ├─ models/
│  │  ├─ user.py          # SQLAlchemy db instance and User model
│  │  └─ note.py          # Note model (with extracted_info/extracted_at)
│  ├─ routes/
│  │  ├─ note.py          # Notes API (CRUD, search, extract-info)
│  │  └─ user.py          # Users API (basic CRUD)
│  └─ services/
│     └─ ai_service.py    # GitHub AI / OpenAI-compatible client wrapper
├─ requirements.txt       # Python dependencies
├─ README.md
└─ other docs 
```

## Quick start (development)

These instructions assume you're on Windows (PowerShell) since that's the common environment for this workspace. Adjust commands for macOS/Linux as needed.

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell prevents running scripts, run (as admin) `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` and re-open the shell.

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Configure environment variables

- The AI feature requires `GITHUB_TOKEN` environment variable. On PowerShell set it like:

```powershell
$env:GITHUB_TOKEN = 'your_github_token_here'
```

- Optionally set `DATABASE_URL` to use a persistent database (Postgres/MySQL). If not set the app uses an in-memory SQLite database (ephemeral) which is suitable for quick testing but will not persist between runs or across serverless invocations.

4) Run the app locally

```powershell
python src/main.py
```

The Flask app will start on port 5001 by default; open http://localhost:5001 in your browser. The app serves the static SPA from `src/static/index.html` and exposes API endpoints under `/api`.


## AI extraction behavior and configuration

- The AI service in `src/services/ai_service.py` expects `GITHUB_TOKEN` and uses a GitHub-hosted OpenAI-compatible endpoint. If `GITHUB_TOKEN` is not set, the service raises an error and the extract endpoint returns a helpful message.
- The app uses the `openai` package (or OpenAI-compatible client) configured with a custom base_url. Verify `openai` is in `requirements.txt`.
- The AI service provides three main capabilities:
  1. **Key Information Extraction**: Analyzes document content and extracts structured information (summaries, key points, data, action items, insights)
  2. **Multi-language Translation**: Translates content to target languages (Chinese, English, Japanese, Spanish, French, German) with caching
  3. **Quiz Generation**: Creates multiple-choice questions with options, answers, and explanations to help reinforce learning


## Deployment

- The project includes `api/index.py` which is a minimal Vercel adapter. On Vercel, the `api` folder is used to expose serverless functions; `api/index.py` imports the Flask `app` and exports `wsgi_handler` to let Vercel serve the Flask app.
- For production, set `DATABASE_URL` to a persistent database and set `GITHUB_TOKEN` for AI features.
- **IMPORTANT**: After deploying to Vercel with an existing database, you must run the database migration to add new fields. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for instructions.


## Next steps / improvements

- Add authentication and per-user data separation
- Persist the database in CI/production with `DATABASE_URL`
- Add automated unit tests and a simple CI workflow
- Improve frontend UX and add offline support
