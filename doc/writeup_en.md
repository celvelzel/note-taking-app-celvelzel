# Vercel Deployment Guide: Steps, Issues Summary, and Solutions Review

This document details the steps for deploying a Flask note-taking app to the Vercel platform, along with the main issues encountered during deployment and their solutions. It's for quick reference in future projects.

---

## Table of Contents
- [Vercel Deployment Guide: Steps, Issues Summary, and Solutions Review](#vercel-deployment-guide-steps-issues-summary-and-solutions-review)
  - [Table of Contents](#table-of-contents)
  - [1. Adding New Features and Refactoring the App](#1-adding-new-features-and-refactoring-the-app)
    - [1. Analyze Project Structure and Existing Code](#1-analyze-project-structure-and-existing-code)
    - [2. Update the Frontend Interface](#2-update-the-frontend-interface)
    - [3. Implement Frontend Interaction Logic](#3-implement-frontend-interaction-logic)
    - [4. Create Backend API Endpoints](#4-create-backend-api-endpoints)
    - [5. Integrate GitHub Large Language Model API](#5-integrate-github-large-language-model-api)
    - [6. Update Dependencies and Configuration](#6-update-dependencies-and-configuration)
    - [7. Add Persistent Storage for Extracted Information](#7-add-persistent-storage-for-extracted-information)
    - [8. Optimize the Frontend Page](#8-optimize-the-frontend-page)
    - [9. Prepare for Vercel Cloud Deployment](#9-prepare-for-vercel-cloud-deployment)
  - [2. Configure Supabase and Vercel](#2-configure-supabase-and-vercel)
    - [1. Create a Vercel Project](#1-create-a-vercel-project)
    - [2. Create a New Supabase Project and Save the Connection String](#2-create-a-new-supabase-project-and-save-the-connection-string)
  - [3. Lessons Learned and Best Practices](#3-lessons-learned-and-best-practices)
    - [Key Lessons](#key-lessons)
    - [Common Error Quick Diagnosis Table](#common-error-quick-diagnosis-table)
    - [Deployment Checklist](#deployment-checklist)
- [Issues Encountered During Deployment](#issues-encountered-during-deployment)
  - [1. Vercel Configuration File Issues](#1-vercel-configuration-file-issues)
    - [Issue Description](#issue-description)
    - [Root Cause](#root-cause)
    - [Solution](#solution)
  - [2. Referencing Secrets in Vercel Environment Variables](#2-referencing-secrets-in-vercel-environment-variables)
    - [Issue Description](#issue-description-1)
    - [Root Cause](#root-cause-1)
    - [Solution](#solution-1)
  - [3. Python Version and Dependency Issues](#3-python-version-and-dependency-issues)
    - [Issue Description](#issue-description-2)
    - [Root Cause](#root-cause-2)
    - [Solution](#solution-2)
  - [4. Flask `@before_first_request` Decorator Deprecation](#4-flask-before_first_request-decorator-deprecation)
    - [Issue Description](#issue-description-3)
    - [Root Cause](#root-cause-3)
    - [Solution](#solution-3)
  - [5. Switching Database from Local SQLite to Remote PostgreSQL](#5-switching-database-from-local-sqlite-to-remote-postgresql)
    - [Issue Description](#issue-description-4)
    - [Root Cause](#root-cause-4)
    - [Solution](#solution-4)
  - [6. Evolution of the `api/index.py` Entry File](#6-evolution-of-the-apiindexpy-entry-file)
    - [Issue Description](#issue-description-5)
    - [Root Cause Analysis](#root-cause-analysis)
    - [Solution Evolution Process](#solution-evolution-process)
      - [Phase 1: Initial Attempt (Failed)](#phase-1-initial-attempt-failed)
      - [Phase 2: Implement Proxy Class (Partial Success)](#phase-2-implement-proxy-class-partial-success)
      - [Phase 3: Final Solution (Success)](#phase-3-final-solution-success)
    - [Key Takeaways](#key-takeaways)

---

## 1. Adding New Features and Refactoring the App

### 1. Analyze Project Structure and Existing Code
- Reviewed key files: `main.py`, `models/note.py`, `routes/note.py`, `static/index.html`
- Understood the Flask app architecture, SQLAlchemy data models, and frontend structure
- Confirmed existing API endpoints and frontend features

### 2. Update the Frontend Interface
- Added an "Extract Information" button to the editor area, with hover effects and disabled state styles
- Added a new AI assistant panel on the right: dropdown for target translation language, translation button, and side-by-side display of original and translated text.
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)

### 3. Implement Frontend Interaction Logic
- Added JS methods to handle button click events
- Implemented API calls and loading state management
- Created a modal window to display extracted information
- Added full error handling and user feedback

### 4. Create Backend API Endpoints
- Added new API endpoints in `src/routes/note.py`: `/api/notes/extract-info`, `/api/notes/translate`, and `/api/notes/generate-quiz`
- Endpoints support optional `note_id` parameter; on success, they write to the database and return structured data; on failure, they provide clear error messages
- Implemented POST methods for handling extraction requests
- Added error handling and input validation

### 5. Integrate GitHub Large Language Model API
- Created `src/services/` directory and AI service module
- Implemented `GitHubAIService` class to call the GitHub Models API
- Configured professional prompts to extract key document information
- Added full error handling and timeout controls
- Added `translate_content()` and `generate_quiz()` methods
- Introduced Chinese prompts to constrain response format and added fallback parsing for JSON results
- Exposed `translate_note_content()` and `generate_quiz_question()` for easy route access

### 6. Update Dependencies and Configuration
- Added `requests==2.31.0` to `requirements.txt`
- Created `.env.example` file for environment variable setup examples
- Updated `README.md` with new feature descriptions and setup guides

### 7. Add Persistent Storage for Extracted Information
- Added `extracted_info` and `extracted_at` fields to the Note model, plus fields for translations, questions, and explanations—all stored as JSON text and timestamps for history tracking
- Updated `Note.to_dict()` to deserialize JSON output, ensuring the frontend gets structured data ready to use
- Updated database schema to store AI-extracted information
- Modified API endpoints to save extracted info to the database

### 8. Optimize the Frontend Page
- Implemented auto-resizing content windows for dynamic layouts
- Added note list pagination (10 notes per page)
- Improved responsive design for various screen sizes
- Enhanced UI space usage and interaction experience

### 9. Prepare for Vercel Cloud Deployment
- Created `vercel.json` config file and runtime settings
- Built `index.py` API entry file adapted for serverless environments
- Integrated cloud database support (using PostgreSQL on Supabase)
  
---

## 2. Configure Supabase and Vercel

### 1. Create a Vercel Project
- Create the project and link it to GitHub
- Create `vercel.json` config file in the project root
- Create `api/index.py` entry file in the project root
- Add environment variables in Vercel project settings, including GitHub token and secrets
  ![alt text](image-1.png)
- Deploy to production via GitHub push
- Set the Vercel project to public for user access
  
### 2. Create a New Supabase Project and Save the Connection String
![alt text](image.png)
- Use the transaction pooler to fit Vercel's serverless architecture
- Add `DATABASE_URL` environment variable in Vercel project settings, with the connection string as the value

## 3. Lessons Learned and Best Practices

### Key Lessons
1. **Vercel Configuration**:
   - Explicitly declare serverless function configs in `functions`
   - Add environment variables in Vercel project settings

2. **Database Selection**:
   - Serverless environments require remote databases
   - Inject connection strings via `DATABASE_URL` environment variable
   - Avoid creating local database files in read-only file systems

3. **Entry File Design**:
   - Keep `api/index.py` as a lightweight adapter—just import and export
   - Prioritize exporting WSGI callables (`app` or `wsgi_handler`)
   - Avoid exporting incomplete `handler` classes

4. **Debugging Tips**:
   - Add `print()` statements or logs in key paths
   - Use `traceback.print_exc()` to capture full error stacks
   - Wrap optional dependencies in try/except for graceful handling
   - Return clear error messages (e.g., 503 Service Unavailable + setup tips) instead of 500 Internal Error
   - Print tracebacks in Vercel logs for quick issue spotting

### Common Error Quick Diagnosis Table

| Error Message | Possible Cause | Solution |
|---------------|----------------|----------|
| `TypeError: issubclass() arg 1 must be a class` | Exported a non-class object as `handler` | Remove `handler` export; keep only `app`/`wsgi_handler` |
| `501 Unsupported method` | `handler` class lacks HTTP method implementations | Remove `handler` or add full proxy logic |
| `OSError: Read-only file system` | Writing to read-only directory in serverless container | Switch to remote database; remove local file writes |
| `No module named 'xxx'` | Missing dependency in `requirements.txt` | Add the missing package to `requirements.txt` |
| `DATABASE_URL not set` | Environment variable not configured | Add it in Vercel project settings |
| `DeprecationWarning: before_first_request` | Using deprecated Flask decorator | Switch to `with app.app_context()` for init |
| `psycopg2.OperationalError` | PostgreSQL connection failure | Check `DATABASE_URL` format and database accessibility |

### Deployment Checklist
- [ ] `requirements.txt` includes all runtime dependencies
- [ ] `vercel.json` routing is correct (static → API → fallback)
- [ ] Environment variables are set in Vercel project settings (Production/Preview)
- [ ] `api/index.py` only exports `app` and `wsgi_handler`
- [ ] Database uses remote PostgreSQL (via `DATABASE_URL`)
- [ ] Removed deprecated decorators like `@before_first_request`
- [ ] No hardcoded sensitive info in code
- [ ] Local `vercel dev` tests pass
- [ ] Check Vercel logs after deployment for errors

---

# Issues Encountered During Deployment

## 1. Vercel Configuration File Issues

### Issue Description
Initial deployment failed due to improper `vercel.json` setup:
- Configured both `functions` and `builds` at the same time

### Root Cause
Vercel allows only one of `functions` or `builds` for function config—they can't be used together.

### Solution
Use `functions` for config, as it supports more features.

## 2. Referencing Secrets in Vercel Environment Variables

### Issue Description
The "GITHUB_TOKEN" environment variable referenced a Secret "github_token" that didn't exist. Vercel supports `@secret_name` syntax in `vercel.json` for Secrets, which must be created separately via Vercel CLI or Dashboard (not in Settings → Environment Variables).

### Root Cause
- Added `GITHUB_TOKEN` in Settings → Environment Variables without creating the Secret `github_token`, so the `@github_token` reference failed
- If vars aren't set for the environment, `os.getenv()` returns `None` at runtime

### Solution
1. **Add environment variables in Vercel project settings**:
   - Go to Project → Settings → Environment Variables
   - Add key-value pairs (e.g., `DATABASE_URL`)
   - Select environments: Production, Preview, Development

2. Remove any `env` field from `vercel.json`.

---

## 3. Python Version and Dependency Issues

### Issue Description
- Deployment errors like "No module named 'xxx'" (missing dependencies)
- Python version mismatches causing install or runtime failures

### Root Cause
- `requirements.txt` missing runtime packages
- Vercel's default Python version differs from local dev
- Some packages incompatible with certain Python versions

### Solution
1. **Ensure complete `requirements.txt`**:
   ```txt
   Flask>=3.0.0
   Flask-CORS>=4.0.0
   Flask-SQLAlchemy>=3.1.0
   psycopg2-binary>=2.9.0
   openai>=1.0.0
   # ... other dependencies
   ```

2. **Specify Python version in `vercel.json` or `runtime.txt`**:
   ```json
   {
     "functions": {
       "api/index.py": {
         "runtime": "python3.9"
       }
     }
   }
   ```

**Key Takeaways**:
- Serverless is stateless; dependencies reinstall on each cold start
- Use stable version ranges (e.g., `>=3.0.0` not `==3.0.1`)
- Avoid unnecessary large packages in `requirements.txt` (slows deployment and cold starts)

---

## 4. Flask `@before_first_request` Decorator Deprecation

### Issue Description
In Flask 3.0+, using `@app.before_first_request` caused runtime warnings or errors:
```
DeprecationWarning: 'before_first_request' is deprecated and will be removed in Flask 3.1
```

### Root Cause
- Flask 3.0 deprecated `@before_first_request`; use app context or run init on startup instead
- "First request" doesn't apply well in serverless (each instance may cold-start independently)

### Solution

**Run on module import** (fits serverless):
```python
# In src/main.py, after app instantiation
try:
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
except Exception as e:
    print(f"Warning: db.create_all() failed: {e}")
    traceback.print_exc()
```

**Key Takeaways**:
- In serverless, init app context on module import (not first request)
- Wrap init logic in try/except to avoid import failures from DB issues

---

## 5. Switching Database from Local SQLite to Remote PostgreSQL

### Issue Description
- Local dev used SQLite file (`database/notes.db`)
- Vercel deployment errored: `OSError: [Errno 30] Read-only file system: '/var/task/database'`
- Serverless file system is read-only; can't create/write SQLite files

### Root Cause
- Vercel runs in temp containers with read-only code dir (`/var/task`)
- SQLite needs file I/O, unsuitable for serverless
- Requests may run in different containers; local files aren't shared

### Solution
1. **Use remote PostgreSQL**:
   - Choose a hosted service: Supabase
   - Get connection string (format: `postgresql://user:password@host:port/dbname`)

2. **Set `DATABASE_URL` in Vercel**:
   - Project Settings → Environment Variables → Add `DATABASE_URL`
   - Value: the connection string

3. **Update app config** (`src/main.py`):
   ```python
   import os

   # Prefer env var for DB URL
   database_url = os.getenv("DATABASE_URL")
   if database_url:
       # Compat with old Heroku format
       if database_url.startswith("postgres://"):
           database_url = database_url.replace("postgres://", "postgresql://", 1)
       app.config["SQLALCHEMY_DATABASE_URI"] = database_url
       print(f"Using remote database: {database_url[:30]}...")  # Prefix only, no password leak
   else:
       # Fallback to in-memory (testing only, no persistence)
       print("Warning: DATABASE_URL not set; using in-memory SQLite.")
       app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
   ```

**Key Takeaways**:
- SQLite unfit for serverless prod (no persistence, poor concurrency)
- Hosted DBs offer backups, scalability, pooling
- Inject connection strings via env vars; never hardcode

---

## 6. Evolution of the `api/index.py` Entry File

### Issue Description
During deployment, `api/index.py` went through several iterations, hitting errors like:
- `TypeError: issubclass() arg 1 must be a class`
- `501 Unsupported method ('GET')`
- Static assets and API requests not routing correctly

### Root Cause Analysis
1. **`issubclass` Error**:
   - Vercel's Python runtime (`vc__handler__python.py`) checks exported symbols
   - Exporting a `handler` var that's not a class (or incompatible) fails the `issubclass()` check

2. **501 Error**:
   - Runtime instantiates a `BaseHTTPRequestHandler` subclass, but if it lacks `do_GET`/`do_POST` etc., stdlib returns 501
   - Early `api/index.py` exported a placeholder `handler` class (just `pass`), failing on requests

3. **Routing Confusion**:
   - Duplicate Flask app instances or routes in `api/index.py`
   - Conflicts with `src/main.py` app definition

### Solution Evolution Process

#### Phase 1: Initial Attempt (Failed)
```python
# Issue: Exported handler class without HTTP methods
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    pass  # ❌ Leads to 501

# Runtime instantiates handler → GET request → 501
```

#### Phase 2: Implement Proxy Class (Partial Success)
```python
# Tried implementing do_GET etc. to forward to Flask
class VercelRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Build WSGI environ and call app.wsgi_app
        # Complex and error-prone
        pass
```
Issue: Proxy logic was tricky—easy to mess up env vars, headers, etc.

#### Phase 3: Final Solution (Success)
**Remove `handler` export entirely; keep only WSGI callable**:

### Key Takeaways
- **Avoid exporting `handler` classes**: Unless fully implementing HTTP methods and runtime compat
- **Prefer WSGI callables**: `wsgi_handler(environ, start_response)` or Flask `app` directly
- **Keep `api/index.py` lean**: Adapter only; business logic in `src/main.py`
- **Add debug logs**: Print key info on import and request handling for Vercel log tracking
---

**Document Version**: 1.0  
**Last Updated**: 2025-10-16  
**Maintainer**: MA Jiyuan  
**Project Repo**: [note-taking-app-celvelzel](https://github.com/celvelzel/note-taking-app-celvelzel)