from __future__ import annotations

import os
import sqlite3
import unittest
from pathlib import Path

from bot.database import Database


class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.database_path = Path(__file__).resolve().parent / "test_runtime.db"
        if self.database_path.exists():
            os.remove(self.database_path)
        self.database = Database(self.database_path)
        self.database.init()

    def tearDown(self) -> None:
        if self.database_path.exists():
            os.remove(self.database_path)

    def test_course_and_registration_flow(self) -> None:
        course_id = self.database.add_course("Frontend", "React kursi")

        courses = self.database.list_courses()
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]["name"], "Frontend")

        registration_id = self.database.add_registration(
            user_id=1001,
            username="student",
            first_name="Ali",
            last_name="Valiyev",
            phone="+998901234567",
            address="Toshkent, Chilonzor",
            course_id=course_id,
        )
        self.assertGreater(registration_id, 0)
        self.assertTrue(self.database.user_has_registration(1001, course_id))

        registrations = self.database.get_registrations_by_course(course_id)
        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0]["first_name"], "Ali")

    def test_duplicate_registration_is_rejected(self) -> None:
        course_id = self.database.add_course("Backend", "Python kursi")

        self.database.add_registration(
            user_id=2002,
            username=None,
            first_name="Vali",
            last_name="Karimov",
            phone="+998901112233",
            address="Samarqand",
            course_id=course_id,
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.database.add_registration(
                user_id=2002,
                username=None,
                first_name="Vali",
                last_name="Karimov",
                phone="+998901112233",
                address="Samarqand",
                course_id=course_id,
            )

    def test_teacher_profile_is_stored(self) -> None:
        profile = self.database.get_teacher_profile()
        self.assertEqual(profile["id"], 1)

        self.database.update_teacher_profile(
            full_name="Habib Karimov",
            phone="+998901234567",
            social_links="Telegram: https://t.me/habib\nInstagram: https://instagram.com/habib",
            bio="5 yillik tajribaga ega mentor.",
        )

        updated_profile = self.database.get_teacher_profile()
        self.assertEqual(updated_profile["full_name"], "Habib Karimov")
        self.assertEqual(updated_profile["phone"], "+998901234567")
        self.assertIn("https://t.me/habib", updated_profile["social_links"])
        self.assertEqual(updated_profile["bio"], "5 yillik tajribaga ega mentor.")

    def test_course_recipients_are_separated_by_course(self) -> None:
        frontend_id = self.database.add_course("Frontend", "UI kursi")
        backend_id = self.database.add_course("Backend", "API kursi")

        self.database.add_registration(
            user_id=10,
            username="frontend_user",
            first_name="Ali",
            last_name="Frontendov",
            phone="+998901000010",
            address="Toshkent",
            course_id=frontend_id,
        )
        self.database.add_registration(
            user_id=20,
            username="backend_user",
            first_name="Vali",
            last_name="Backendov",
            phone="+998901000020",
            address="Samarqand",
            course_id=backend_id,
        )

        frontend_recipients = self.database.get_course_recipients(frontend_id)
        backend_recipients = self.database.get_course_recipients(backend_id)

        self.assertEqual(len(frontend_recipients), 1)
        self.assertEqual(frontend_recipients[0]["user_id"], 10)
        self.assertEqual(len(backend_recipients), 1)
        self.assertEqual(backend_recipients[0]["user_id"], 20)


if __name__ == "__main__":
    unittest.main()
