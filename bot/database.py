from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass(slots=True)
class Database:
    path: Path

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def init(self) -> None:
        with closing(self._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    course_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE(user_id, course_id)
                );

                CREATE TABLE IF NOT EXISTS teacher_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    full_name TEXT NOT NULL DEFAULT '',
                    phone TEXT NOT NULL DEFAULT '',
                    social_links TEXT NOT NULL DEFAULT '',
                    bio TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL
                );
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO teacher_profile (
                    id,
                    full_name,
                    phone,
                    social_links,
                    bio,
                    updated_at
                )
                VALUES (1, '', '', '', '', ?)
                """,
                (now_text(),),
            )
            connection.commit()

    def add_course(self, name: str, description: str | None = None) -> int:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO courses (name, description, created_at)
                VALUES (?, ?, ?)
                """,
                (name, description, now_text()),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_courses(self) -> list[sqlite3.Row]:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.description,
                    c.created_at,
                    COUNT(r.id) AS registration_count
                FROM courses c
                LEFT JOIN registrations r ON r.course_id = c.id
                GROUP BY c.id
                ORDER BY c.name COLLATE NOCASE
                """
            )
            return list(cursor.fetchall())

    def get_course(self, course_id: int) -> sqlite3.Row | None:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT id, name, description, created_at
                FROM courses
                WHERE id = ?
                """,
                (course_id,),
            )
            return cursor.fetchone()

    def delete_course(self, course_id: int) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                "DELETE FROM courses WHERE id = ?",
                (course_id,),
            )
            connection.commit()
            return cursor.rowcount > 0

    def user_has_registration(self, user_id: int, course_id: int) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT 1
                FROM registrations
                WHERE user_id = ? AND course_id = ?
                LIMIT 1
                """,
                (user_id, course_id),
            )
            return cursor.fetchone() is not None

    def add_registration(
        self,
        *,
        user_id: int,
        username: str | None,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        course_id: int,
    ) -> int:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO registrations (
                    user_id,
                    username,
                    first_name,
                    last_name,
                    phone,
                    address,
                    course_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    first_name,
                    last_name,
                    phone,
                    address,
                    course_id,
                    now_text(),
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def get_registrations_by_course(self, course_id: int) -> list[sqlite3.Row]:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT
                    r.id,
                    r.user_id,
                    r.username,
                    r.first_name,
                    r.last_name,
                    r.phone,
                    r.address,
                    r.created_at,
                    c.name AS course_name
                FROM registrations r
                INNER JOIN courses c ON c.id = r.course_id
                WHERE r.course_id = ?
                ORDER BY r.created_at DESC
                """,
                (course_id,),
            )
            return list(cursor.fetchall())

    def get_course_recipients(self, course_id: int) -> list[sqlite3.Row]:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT
                    user_id,
                    username,
                    first_name,
                    last_name
                FROM registrations
                WHERE course_id = ?
                ORDER BY created_at DESC
                """,
                (course_id,),
            )
            return list(cursor.fetchall())

    def get_teacher_profile(self) -> sqlite3.Row:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT id, full_name, phone, social_links, bio, updated_at
                FROM teacher_profile
                WHERE id = 1
                """
            )
            profile = cursor.fetchone()
            if profile is None:
                raise RuntimeError("Teacher profile topilmadi.")
            return profile

    def update_teacher_profile(
        self,
        *,
        full_name: str,
        phone: str,
        social_links: str,
        bio: str,
    ) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                UPDATE teacher_profile
                SET
                    full_name = ?,
                    phone = ?,
                    social_links = ?,
                    bio = ?,
                    updated_at = ?
                WHERE id = 1
                """,
                (full_name, phone, social_links, bio, now_text()),
            )
            connection.commit()
