from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(slots=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    database_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        if not bot_token:
            raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan.")

        admin_ids_raw = os.getenv("ADMIN_IDS", "")
        admin_ids = {
            int(chunk.strip())
            for chunk in admin_ids_raw.split(",")
            if chunk.strip()
        }

        database_path = BASE_DIR / os.getenv("DATABASE_PATH", "data/bot.db")
        database_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(
            bot_token=bot_token,
            admin_ids=admin_ids,
            database_path=database_path,
        )
