-- Migration: Add translation and quiz fields to note table
-- Date: 2025-10-16
-- Description: Adds AI translation and quiz generation support to existing notes

-- Add translation fields
ALTER TABLE note ADD COLUMN IF NOT EXISTS translations TEXT;
ALTER TABLE note ADD COLUMN IF NOT EXISTS translation_updated_at TIMESTAMP;

-- Add quiz fields
ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_question TEXT;
ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_options TEXT;
ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_answer VARCHAR(50);
ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_explanation TEXT;
ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_generated_at TIMESTAMP;

-- Add comments for documentation
COMMENT ON COLUMN note.translations IS 'JSON object mapping language names to translated text';
COMMENT ON COLUMN note.translation_updated_at IS 'Timestamp of last translation update';
COMMENT ON COLUMN note.quiz_question IS 'AI-generated quiz question text';
COMMENT ON COLUMN note.quiz_options IS 'JSON array of quiz options with label and text';
COMMENT ON COLUMN note.quiz_answer IS 'Correct answer label (e.g., A, B, C, D)';
COMMENT ON COLUMN note.quiz_explanation IS 'Explanation for the correct answer';
COMMENT ON COLUMN note.quiz_generated_at IS 'Timestamp when quiz was generated';
