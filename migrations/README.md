# Database Migrations

This directory contains database migration scripts for the NoteTaker application.

## Available Migrations

### 2025-10-16: Add Translation and Quiz Fields

**Files:**
- `add_translation_quiz_fields.sql` - Raw SQL migration script
- `migrate_add_fields.py` - Python migration script with transaction support

**Changes:**
Adds the following fields to the `note` table:
- `translations` (TEXT) - JSON object storing translations by language
- `translation_updated_at` (TIMESTAMP) - Last translation update time
- `quiz_question` (TEXT) - AI-generated quiz question
- `quiz_options` (TEXT) - JSON array of quiz options
- `quiz_answer` (VARCHAR(50)) - Correct answer label
- `quiz_explanation` (TEXT) - Answer explanation
- `quiz_generated_at` (TIMESTAMP) - Quiz generation time

## How to Apply Migrations

### Option 1: Using Python Script (Recommended)

1. Set your DATABASE_URL environment variable:
   ```powershell
   $env:DATABASE_URL = "postgresql://user:password@host:port/database"
   ```

2. Run the migration script:
   ```powershell
   python migrations/migrate_add_fields.py
   ```

### Option 2: Using SQL Directly

If you have direct database access (e.g., psql, pgAdmin):

```bash
psql $DATABASE_URL -f migrations/add_translation_quiz_fields.sql
```

### Option 3: For Vercel Postgres

1. Go to your Vercel project dashboard
2. Navigate to Storage → Your Postgres Database
3. Click on "Query" or "Data" tab
4. Copy and paste the contents of `add_translation_quiz_fields.sql`
5. Execute the query

Alternatively, use Vercel CLI:
```bash
vercel env pull .env.local
# Set DATABASE_URL from .env.local
python migrations/migrate_add_fields.py
```

## Verifying Migration

After running the migration, verify the new columns exist:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'note' 
AND column_name IN ('translations', 'translation_updated_at', 'quiz_question', 'quiz_options', 'quiz_answer', 'quiz_explanation', 'quiz_generated_at');
```

## Rollback (if needed)

To remove the added fields:

```sql
ALTER TABLE note DROP COLUMN IF EXISTS translations;
ALTER TABLE note DROP COLUMN IF EXISTS translation_updated_at;
ALTER TABLE note DROP COLUMN IF EXISTS quiz_question;
ALTER TABLE note DROP COLUMN IF EXISTS quiz_options;
ALTER TABLE note DROP COLUMN IF EXISTS quiz_answer;
ALTER TABLE note DROP COLUMN IF EXISTS quiz_explanation;
ALTER TABLE note DROP COLUMN IF EXISTS quiz_generated_at;
```

## Notes

- All migrations use `ADD COLUMN IF NOT EXISTS` to be idempotent (safe to run multiple times)
- The Python script includes transaction support for rollback on errors
- Existing data is preserved during migration
- New fields are nullable by default
