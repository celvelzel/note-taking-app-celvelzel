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

## API
Base URL (local): http://localhost:5001/api

This section documents the HTTP API implemented by the Flask app (routes live in `src/routes/`). All endpoints return JSON unless noted otherwise. Example curl/PowerShell requests show how to call each endpoint.

Summary of endpoints

- Notes: `/notes` (list/create), `/notes/<id>` (get/update/delete), `/notes/search` (query), `/notes/extract-info` (AI extraction)
- Users: `/users` (list/create), `/users/<id>` (get/update/delete)

Common responses

- Success list/object: 200 OK (or 201 Created on successful POST)
- Validation client error: 400 Bad Request
- Not found: 404 Not Found
- Server error: 500 Internal Server Error

Notes model schema (JSON representation)

Returned note objects use the `Note.to_dict()` shape:

```json
{
  "id": integer,
  "title": string,
  "content": string,
  "extracted_info": string | null,
  "extracted_at": ISO8601 datetime string | null,
  "translations": object (map of language to translated text),
  "translation_updated_at": ISO8601 datetime string | null,
  "quiz_question": string | null,
  "quiz_options": array of {label: string, text: string},
  "quiz_answer": string | null,
  "quiz_explanation": string | null,
  "quiz_generated_at": ISO8601 datetime string | null,
  "created_at": ISO8601 datetime string | null,
  "updated_at": ISO8601 datetime string | null
}
```

Users model schema (JSON representation)

{
	"id": integer,
	"username": string,
	"email": string
}

Detailed endpoints

1) GET /notes

- Description: Return all notes ordered by `updated_at` descending.
- Query params: none
- Response: 200 OK, JSON array of note objects

Example (bash):

```bash
curl -s http://localhost:5001/api/notes | jq '.'
```

2) POST /notes

- Description: Create a new note.
- Body (JSON, required): { "title": "...", "content": "..." }
- Responses:
	- 201 Created: returns the created note object
	- 400 Bad Request: missing title/content
	- 500 Internal Server Error: server-side error

Example (PowerShell):

```powershell
$body = @{ title = 'Shopping'; content = 'Buy milk and eggs' } | ConvertTo-Json
curl -Method Post -ContentType 'application/json' -Body $body http://localhost:5001/api/notes
```

3) GET /notes/<id>

- Description: Retrieve a single note by ID.
- Path param: `id` (integer)
- Responses:
	- 200 OK: note object
	- 404 Not Found: if note id does not exist

1) GET /notes

```bash
curl http://localhost:5001/api/notes/1
```

4) PUT /notes/<id>

- Description: Update a note's `title` and/or `content`.
- Path param: `id` (integer)
- Body (JSON): any subset of { "title": "...", "content": "..." }
- Responses:
2) POST /notes
	- 400 Bad Request: no data provided
	- 404 Not Found: if note id does not exist

5) DELETE /notes/<id>
 - 201 Created: returns the created note object
 - 400 Bad Request: missing title/content
 - 500 Internal Server Error: server-side error
- Responses:
	- 204 No Content: success (empty body)
	- 404 Not Found: if note id does not exist

6) GET /notes/search?q=...

- Description: Search notes by title or content. Performs a SQL-like contains() search on `title` and `content` and returns matching notes ordered by `updated_at` desc.
- Query params:
3) GET /notes/<id>
- Responses:
	- 200 OK: JSON array of matching note objects

Example:

```bash
curl "http://localhost:5001/api/notes/search?q=shopping"
```

7) POST /notes/extract-info

- Description: Use the AI service to extract key information from a free-text document. This calls the GitHub AI/OpenAI-compatible client wrapper in `src/services/ai_service.py`.
- Body (JSON, required):
  - `content` (string) — the raw text to analyze (required)
  - `note_id` (integer) — optional; if provided and the note exists, the returned extracted text will be saved into that note's `extracted_info` and `extracted_at` fields
- Responses:
  - 200 OK: { "success": true, "extracted_info": string, "saved": boolean }
  - 400 Bad Request: missing or empty `content`
  - 404 Not Found: provided `note_id` does not exist
  - 500 Internal Server Error: errors committing to DB or unexpected server errors

8) POST /notes/translate

- Description: Translate note content to a specified target language using GitHub AI service. Translations are cached per language in the note's `translations` field.
- Body (JSON, required):
  - `content` (string) — the text to translate (required)
  - `language` (string) — target language name (required, e.g., "简体中文", "English", "日本語", "Español", "Français", "Deutsch")
  - `note_id` (integer) — optional; if provided and the note exists, the translation will be saved to the note's translations map
- Responses:
  - 200 OK: { "success": true, "translation": string, "language": string, "saved": boolean }
  - 400 Bad Request: missing content or language
  - 404 Not Found: provided `note_id` does not exist
  - 500 Internal Server Error: translation failed or DB error

Example:

```bash
curl -X POST http://localhost:5001/api/notes/translate \
  -H "Content-Type: application/json" \
  -d '{"note_id": 1, "content": "Hello World", "language": "简体中文"}'
```

9) POST /notes/generate-quiz

- Description: Generate a multiple-choice quiz question based on note content to help reinforce learning. The quiz includes question text, 4 options (A-D), the correct answer, and an explanation.
- Body (JSON, required):
  - `content` (string) — the note content to base the quiz on (required)
  - `note_id` (integer) — optional; if provided and the note exists, the generated quiz will be saved to the note
- Responses:
  - 200 OK: { "success": true, "quiz": { "question": string, "options": array, "answer": string, "explanation": string }, "saved": boolean }
  - 400 Bad Request: missing content
  - 404 Not Found: provided `note_id` does not exist
  - 500 Internal Server Error: quiz generation failed or DB error

Example:

```bash
curl -X POST http://localhost:5001/api/notes/generate-quiz \
  -H "Content-Type: application/json" \
  -d '{"note_id": 1, "content": "Python is a high-level programming language..."}'
```

Notes and error behavior for the AI endpoint

- The AI service expects a `GITHUB_TOKEN` environment variable. If not set the service returns a helpful error message instead of raising an unhandled exception.
- The AI client uses a GitHub-hosted OpenAI-compatible endpoint; see `src/services/ai_service.py` for details (model name, base URL).
- The extract endpoint always returns a JSON object on success and returns JSON error messages with appropriate HTTP status codes on failure.

Users endpoints

1) GET /users

- Description: Return a list of all users
- Response: 200 OK — JSON array of users

2) POST /users

- Description: Create a new user
- Body (JSON, required): { "username": "...", "email": "..." }
- Responses:
	- 201 Created: created user object

3) GET /users/<id>

- Description: Get user by id
- Responses: 200 OK or 404 Not Found

4) PUT /users/<id>

- Description: Update user's `username` and/or `email`.
- Body (JSON): any subset of { "username": "...", "email": "..." }
- Response: 200 OK: updated user object

5) DELETE /users/<id>

- Description: Delete a user
- Response: 204 No Content on success

## AI extraction behavior and configuration

- The AI service in `src/services/ai_service.py` expects `GITHUB_TOKEN` and uses a GitHub-hosted OpenAI-compatible endpoint. If `GITHUB_TOKEN` is not set, the service raises an error and the extract endpoint returns a helpful message.
- The app uses the `openai` package (or OpenAI-compatible client) configured with a custom base_url. Verify `openai` is in `requirements.txt`.
- The AI service provides three main capabilities:
  1. **Key Information Extraction**: Analyzes document content and extracts structured information (summaries, key points, data, action items, insights)
  2. **Multi-language Translation**: Translates content to target languages (Chinese, English, Japanese, Spanish, French, German) with caching
  3. **Quiz Generation**: Creates multiple-choice questions with options, answers, and explanations to help reinforce learning

## Frontend Features

The single-page application (`src/static/index.html`) provides:

- **Split-panel editor**: Left sidebar for note list with pagination, right main area with note editor and AI assistant panel
- **AI Assistant Panel**: Side-by-side display for translations and quiz interactions
  - Language selector dropdown with 6 supported languages
  - Real-time translation display with language switching
  - Interactive quiz with click-to-answer and immediate feedback
- **Responsive design**: Adapts to mobile and desktop screens
- **Visual indicators**: Icons (🧠) mark notes with AI-extracted information
- **Auto-save**: Debounced saving as you type

## Database notes

- By default the app checks `DATABASE_URL` environment variable. If present it will be used (Postgres/MySQL supported via SQLAlchemy).
- If `DATABASE_URL` is not set, the app will fall back to an in-memory SQLite DB: `sqlite:///:memory:`. This is ephemeral and good for quick testing but not for production.
- On first run the app calls `db.create_all()` to create tables.

## Deployment

- The project includes `api/index.py` which is a minimal Vercel adapter. On Vercel, the `api` folder is used to expose serverless functions; `api/index.py` imports the Flask `app` and exports `wsgi_handler` to let Vercel serve the Flask app.
- For production, set `DATABASE_URL` to a persistent database and set `GITHUB_TOKEN` for AI features.

## Next steps / improvements

- Add authentication and per-user data separation
- Persist the database in CI/production with `DATABASE_URL`
- Add automated unit tests and a simple CI workflow
- Improve frontend UX and add offline support
