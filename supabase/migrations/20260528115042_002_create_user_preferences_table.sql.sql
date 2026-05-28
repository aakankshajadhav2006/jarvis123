/*
  # User Language Preferences Table
  
  Stores user preferences for multilingual voice assistance.
  
  1. New Tables
    - `user_preferences` - Stores user settings and preferences
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users, unique)
      - `preferred_language` (text) - Language code (en, hi, mr)
      - `voice_mode_enabled` (boolean) - Voice mode toggle
      - `updated_at` (timestamp)
  
  2. Security
    - Enable RLS on `user_preferences` table
    - Users can only access their own preferences
*/


CREATE TABLE IF NOT EXISTS user_preferences (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  preferred_language text DEFAULT 'en',
  voice_mode_enabled boolean DEFAULT false,
  updated_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own preferences
CREATE POLICY "Users can view own preferences"
  ON user_preferences FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own preferences
CREATE POLICY "Users can insert own preferences"
  ON user_preferences FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own preferences
CREATE POLICY "Users can update own preferences"
  ON user_preferences FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own preferences
CREATE POLICY "Users can delete own preferences"
  ON user_preferences FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Create index for faster queries
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
