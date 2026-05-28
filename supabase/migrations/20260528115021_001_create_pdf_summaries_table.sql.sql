/*
  # PDF Summaries Table
  
  Stores AI-generated summaries, key points, and viva questions from PDF documents.
  
  1. New Tables
    - `pdf_summaries` - Stores document summaries with metadata
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `filename` (text) - Original PDF filename
      - `summary` (text) - AI-generated summary
      - `key_points` (text) - Extracted key points
      - `viva_questions` (text) - Generated viva/exam questions
      - `language` (text) - Language code (en, hi, mr)
      - `created_at` (timestamp)
      - `file_size` (integer) - PDF file size in bytes
  
  2. Security
    - Enable RLS on `pdf_summaries` table
    - Users can only access their own summaries
*/


CREATE TABLE IF NOT EXISTS pdf_summaries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  filename text NOT NULL,
  summary text,
  key_points text,
  viva_questions text,
  language text DEFAULT 'en',
  file_size integer,
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE pdf_summaries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own summaries
CREATE POLICY "Users can view own PDF summaries"
  ON pdf_summaries FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own summaries
CREATE POLICY "Users can insert own PDF summaries"
  ON pdf_summaries FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own summaries
CREATE POLICY "Users can update own PDF summaries"
  ON pdf_summaries FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own summaries
CREATE POLICY "Users can delete own PDF summaries"
  ON pdf_summaries FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Create index for faster queries
CREATE INDEX idx_pdf_summaries_user_id ON pdf_summaries(user_id);
CREATE INDEX idx_pdf_summaries_created_at ON pdf_summaries(created_at DESC);
