"""
User language preference management module.
Handles getting, setting, and storing user language preferences.
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from bot.database import Database


class LanguageManager:
    """Manages user language preferences."""
    
    def __init__(self, database: Database):
        self.database = database
        self.db_path = database.db_path
    
    def get_user_language(self, user_id: int) -> str:
        """Get the language preference for a user. Defaults to 'uz' if not set."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT language FROM language_preferences WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            return row["language"] if row else "uz"
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            # Table might not exist yet, return default
            return "uz"
    
    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set the language preference for a user."""
        if language not in ("ru", "en", "uz"):
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try to insert, if it fails (user already exists), update
            cursor.execute(
                """INSERT OR REPLACE INTO language_preferences (user_id, language) 
                   VALUES (?, ?)""",
                (user_id, language)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.DatabaseError:
            return False
    
    def create_preferences_table(self) -> None:
        """Create the language_preferences table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS language_preferences (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'uz' CHECK(language IN ('ru', 'en', 'uz')),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except sqlite3.DatabaseError as e:
            print(f"Error creating language_preferences table: {e}")


# Language code mapping for button text recognition
LANGUAGE_CODES = {
    "Ўзбек": "uz",
    "Русский": "ru",
    "English": "en",
}

# Reverse mapping
LANGUAGE_NAMES = {
    "uz": "Ўзбек",
    "ru": "Русский",
    "en": "English",
}


def get_language_from_button(button_text: str) -> Optional[str]:
    """Extract language code from language selection button text."""
    for text, code in LANGUAGE_CODES.items():
        if text in button_text:
            return code
    return None
