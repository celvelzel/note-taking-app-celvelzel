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