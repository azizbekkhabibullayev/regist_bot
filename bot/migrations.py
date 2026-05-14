"""
Database schema migration to add language support.
This file contains SQL statements for adding language preferences to users.
"""

# Migration script to add language support to the database
MIGRATION_SQL = """
-- Add language column to users table if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'uz';

-- Add language column to registrations table if it doesn't exist  
ALTER TABLE registrations ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'uz';
"""

# SQL to create the language_preferences table
CREATE_LANGUAGE_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS language_preferences (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'uz' CHECK(language IN ('ru', 'en', 'uz')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
