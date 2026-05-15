"""
User language preference management module.
Handles getting, setting, and storing user language preferences.
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime
from typing import Any, Optional

from bot.database import Database


class LanguageManager:
    """Manages user language preferences."""
    
    STRINGS = {
        "uz": {
            "menu_courses": "Kurslar 📚",
            "menu_teacher": "Teacher haqida 👨‍🏫",
            "menu_admin": "Admin panel 🛠",
            "menu_lang": "Tilni o'zgartirish 🌐",
            "menu_back": "Bosh menyu ⬅️",
            "menu_cancel": "Bekor qilish ❌",
            "welcome": "<b>Assalomu alaykum!</b>\nKasb o'rganishni bugundan boshlang.\nQuyidagi kurslardan birini tanlang va bir necha daqiqada ro'yxatdan o'ting.",
            "start_available": "<b>Hozir mavjud kurslar:</b>",
            "start_empty": "Hozircha kurslar ro'yxati shakllantirilmoqda.\nYaqinda yangi kurslar qo'shiladi.",
            "start_teacher": "Ustoz haqida bilish uchun <b>Teacher haqida</b> tugmasini bosing.",
            "start_admin": "Siz admin sifatida kurslar va teacher ma'lumotlarini ham boshqarishingiz mumkin.",
            "choose_lang": "Tilni tanlang:",
            "lang_changed": "Til o'zgartirildi: O'zbekcha 🇺🇿",
            "no_courses": "Hozircha kurslar qo'shilmagan.",
            "select_course": "Ro'yxatdan o'tmoqchi bo'lgan kursingizni tanlang:",
            "prev_btn": "◀️ Oldingi",
            "next_btn": "Keyingi ▶️",
            "teacher_profile_title": "<b>Teacher haqida</b>",
            "teacher_not_set": "Hozircha ustoz haqida ma'lumot kiritilmagan.",
            "field_full_name": "<b>Ism-familya:</b>",
            "field_phone": "<b>Telefon:</b>",
            "field_social": "<b>Ijtimoiy tarmoqlar:</b>",
            "field_bio": "<b>Qisqacha ma'lumot:</b>",
            "enter_first_name": "Ismingizni kiriting:",
            "enter_last_name": "Familyangizni kiriting:",
            "enter_phone": "Telefon raqamingizni yuboring yoki qo'lda kiriting.\nMasalan: +998901234567",
            "enter_address": "Manzilingizni kiriting:",
            "send_phone_btn": "Telefon raqamni yuboring",
            "reg_success": "Siz {course_name} kursiga muvaffaqiyatli ro'yxatdan o'tdingiz.",
            "already_registered": "Siz ushbu kursga allaqachon ro'yxatdan o'tgansiz.",
            "invalid_name": "Ismni to'g'ri kiriting (kamida 2 ta harf).",
            "invalid_phone": "Telefon raqam noto'g'ri. Masalan: +998901234567",
            "invalid_address": "Manzilni to'liqroq kiriting.",
            "fallback": "Iltimos, menyudagi tugmalardan foydalaning.",
            "action_cancelled": "Amal bekor qilindi.",
            "course_selected": "{course_name} kursi tanlandi.",
            "course_desc": "\nTavsif: {description}",
            "admin_welcome": "Admin panelga xush kelibsiz. Bu yerda kurslar, arizalar va teacher ma'lumotlarini boshqarasiz.",
            "admin_menu_add": "Kurs qo'shish",
            "admin_menu_del": "Kursni o'chirish",
            "admin_menu_apps": "Arizalarni ko'rish",
            "admin_menu_send": "Kursga xabar yuborish",
            "admin_menu_teacher": "Teacher ma'lumotini sozlash",
            "admin_no_permission": "Sizda bu amal uchun huquq yo'q.",
            "admin_course_add_name": "Yangi kurs nomini kiriting:",
            "admin_course_add_desc": "Kurs tavsifini kiriting.\nAgar kerak bo'lmasa `-` yuboring.",
            "admin_course_added": "{name} kursi qo'shildi.",
            "admin_course_exists": "Bunday nomdagi kurs allaqachon mavjud.",
            "admin_course_del_select": "O'chiriladigan kursni tanlang:",
            "admin_course_del_success": "{name} kursi o'chirildi.",
            "admin_course_del_fail": "Kursni o'chirib bo'lmadi.",
            "admin_course_not_found": "Kurs topilmadi.",
            "admin_no_courses": "Hozircha kurslar mavjud emas.",
            "admin_apps_select": "Qaysi kurs arizalarini ko'rmoqchisiz?",
            "admin_broadcast_select": "Qaysi kursga xabar yubormoqchisiz?",
            "admin_broadcast_prompt": "Endi yuboriladigan xabar matnini kiriting:",
            "admin_broadcast_status": "{name} kursi uchun xabar yuborildi.\nYuborildi: {sent}\nYuborilmadi: {failed}",
            "admin_broadcast_no_users": "Bu kurs uchun ro'yxatdan o'tgan userlar topilmadi.",
            "admin_teacher_edit_name": "Teacher ism-familyasini kiriting:",
            "admin_teacher_edit_phone": "Teacher telefon raqamini kiriting.\nMasalan: +998901234567",
            "admin_teacher_edit_social": "Ijtimoiy tarmoqlar manzillarini yuboring.\nHar birini yangi qatordan yozing.\nAgar hozircha bo'lmasa `-` yuboring.",
            "admin_teacher_edit_bio": "Teacher haqida qisqacha ma'lumot kiriting.\nAgar hozircha bo'lmasa `-` yuboring.",
            "admin_teacher_updated": "Teacher ma'lumotlari muvaffaqiyatli yangilandi.",
            "admin_new_reg_notif": "Yangi ariza keldi.\n\nKurs: {course}\nIsm: {first}\nFamilya: {last}\nTelefon: {phone}\nManzil: {addr}\nTelegram: {tg}",
            "admin_apps_empty": "{course} kursi uchun hali arizalar yo'q.",
            "admin_apps_title": "{course} kursi bo'yicha arizalar:",
        },
        "ru": {
            "menu_courses": "Курсы 📚",
            "menu_teacher": "О учителе 👨‍🏫",
            "menu_admin": "Админ панель 🛠",
            "menu_lang": "Изменить язык 🌐",
            "menu_back": "Главное меню ⬅️",
            "menu_cancel": "Отмена ❌",
            "welcome": "<b>Здравствуйте!</b>\nНачните обучение профессии сегодня.\nВыберите один из курсов ниже и зарегистрируйтесь за несколько минут.",
            "start_available": "<b>Доступные курсы:</b>",
            "start_empty": "Список курсов в данный момент формируется.\nНовые курсы будут добавлены в ближайшее время.",
            "start_teacher": "Нажмите <b>О учителе</b>, чтобы узнать больше.",
            "start_admin": "Вы можете управлять курсами и информацией как администратор.",
            "choose_lang": "Выберите язык:",
            "lang_changed": "Язык изменен: Русский 🇷🇺",
            "no_courses": "Курсы пока не добавлены.",
            "select_course": "Выберите курс для регистрации:",
            "prev_btn": "◀️ Назад",
            "next_btn": "Вперед ▶️",
            "teacher_profile_title": "<b>О учителе</b>",
            "teacher_not_set": "Информация об учителе еще не введена.",
            "field_full_name": "<b>Имя и фамилия:</b>",
            "field_phone": "<b>Телефон:</b>",
            "field_social": "<b>Социальные сети:</b>",
            "field_bio": "<b>Краткая информация:</b>",
            "enter_first_name": "Введите ваше имя:",
            "enter_last_name": "Введите вашу фамилию:",
            "enter_phone": "Отправьте свой номер телефона или введите его вручную.\nНапример: +998901234567",
            "enter_address": "Введите ваш адрес:",
            "send_phone_btn": "Отправить номер телефона",
            "reg_success": "Вы успешно зарегистрировались на курс {course_name}.",
            "already_registered": "Вы уже зарегистрированы на этот курс.",
            "invalid_name": "Введите имя правильно (минимум 2 буквы).",
            "invalid_phone": "Неверный номер телефона. Например: +998901234567",
            "invalid_address": "Введите адрес более подробно.",
            "fallback": "Пожалуйста, используйте кнопки меню.",
            "action_cancelled": "Действие отменено.",
            "course_selected": "Выбран курс {course_name}.",
            "course_desc": "\nОписание: {description}",
            "admin_welcome": "Добро пожаловать в админ-панель. Здесь вы управляете курсами, заявками и информацией об учителе.",
            "admin_menu_add": "Добавить курс",
            "admin_menu_del": "Удалить курс",
            "admin_menu_apps": "Просмотр заявок",
            "admin_menu_send": "Отправить сообщение курсу",
            "admin_menu_teacher": "Настройка профиля учителя",
            "admin_no_permission": "У вас нет прав для этого действия.",
            "admin_course_add_name": "Введите название нового курса:",
            "admin_course_add_desc": "Введите описание курса.\nЕсли не нужно, отправьте `-`.",
            "admin_course_added": "Курс {name} добавлен.",
            "admin_course_exists": "Курс с таким названием уже существует.",
            "admin_course_del_select": "Выберите курс для удаления:",
            "admin_course_del_success": "Курс {name} удален.",
            "admin_course_del_fail": "Не удалось удалить курс.",
            "admin_course_not_found": "Курс не найден.",
            "admin_no_courses": "Курсы пока не созданы.",
            "admin_apps_select": "Заявки какого курса вы хотите посмотреть?",
            "admin_broadcast_select": "Какому курсу вы хотите отправить сообщение?",
            "admin_broadcast_prompt": "Теперь введите текст сообщения для рассылки:",
            "admin_broadcast_status": "Сообщение для курса {name} отправлено.\nОтправлено: {sent}\nНе удалось: {failed}",
            "admin_broadcast_no_users": "Для этого курса не найдено зарегистрированных пользователей.",
            "admin_teacher_edit_name": "Введите имя и фамилию учителя:",
            "admin_teacher_edit_phone": "Введите номер телефона учителя.\nНапример: +998901234567",
            "admin_teacher_edit_social": "Отправьте ссылки на социальные сети.\nПишите каждую с новой строки.\nЕсли пока нет, отправьте `-`.",
            "admin_teacher_edit_bio": "Введите краткую информацию об учителе.\nЕсли пока нет, отправьте `-`.",
            "admin_teacher_updated": "Информация об учителе успешно обновлена.",
            "admin_new_reg_notif": "Поступила новая заявка.\n\nКурс: {course}\nИмя: {first}\nФамилия: {last}\nТелефон: {phone}\nАдрес: {addr}\nTelegram: {tg}",
            "admin_apps_empty": "Для курса {course} пока нет заявок.",
            "admin_apps_title": "Заявки по курсу {course}:",
        },
        "en": {
            "menu_courses": "Courses 📚",
            "menu_teacher": "About Teacher 👨‍🏫",
            "menu_admin": "Admin Panel 🛠",
            "menu_lang": "Change Language 🌐",
            "menu_back": "Main Menu ⬅️",
            "menu_cancel": "Cancel ❌",
            "welcome": "<b>Welcome!</b>\nStart learning a profession today.\nChoose one of the courses below and register in a few minutes.",
            "start_available": "<b>Available courses:</b>",
            "start_empty": "The list of courses is currently being formed.\nNew courses will be added soon.",
            "start_teacher": "Click <b>About Teacher</b> to learn more.",
            "start_admin": "You can manage courses and information as an administrator.",
            "choose_lang": "Choose language:",
            "lang_changed": "Language changed: English 🇺🇸",
            "no_courses": "No courses added yet.",
            "select_course": "Select a course to register:",
            "prev_btn": "◀️ Previous",
            "next_btn": "Next ▶️",
            "teacher_profile_title": "<b>About Teacher</b>",
            "teacher_not_set": "Teacher information not entered yet.",
            "field_full_name": "<b>Full name:</b>",
            "field_phone": "<b>Phone:</b>",
            "field_social": "<b>Social links:</b>",
            "field_bio": "<b>Bio:</b>",
            "enter_first_name": "Enter your first name:",
            "enter_last_name": "Enter your last name:",
            "enter_phone": "Send your phone number or enter it manually.\nFor example: +998901234567",
            "enter_address": "Enter your address:",
            "send_phone_btn": "Send phone number",
            "reg_success": "You have successfully registered for the {course_name} course.",
            "already_registered": "You are already registered for this course.",
            "invalid_name": "Enter name correctly (at least 2 letters).",
            "invalid_phone": "Invalid phone number. Example: +998901234567",
            "invalid_address": "Enter address in more detail.",
            "fallback": "Please use the menu buttons.",
            "action_cancelled": "Action cancelled.",
            "course_selected": "Course {course_name} selected.",
            "course_desc": "\nDescription: {description}",
            "admin_welcome": "Welcome to the admin panel. Here you manage courses, applications, and teacher info.",
            "admin_menu_add": "Add Course",
            "admin_menu_del": "Delete Course",
            "admin_menu_apps": "View Applications",
            "admin_menu_send": "Send Message to Course",
            "admin_menu_teacher": "Teacher Profile Settings",
            "admin_no_permission": "You do not have permission for this action.",
            "admin_course_add_name": "Enter the new course name:",
            "admin_course_add_desc": "Enter the course description.\nIf not needed, send `-`.",
            "admin_course_added": "Course {name} added.",
            "admin_course_exists": "A course with this name already exists.",
            "admin_course_del_select": "Select a course to delete:",
            "admin_course_del_success": "Course {name} deleted.",
            "admin_course_del_fail": "Could not delete the course.",
            "admin_course_not_found": "Course not found.",
            "admin_no_courses": "No courses available yet.",
            "admin_apps_select": "Which course applications do you want to see?",
            "admin_broadcast_select": "Which course do you want to send a message to?",
            "admin_broadcast_prompt": "Now enter the message text to send:",
            "admin_broadcast_status": "Message sent for {name} course.\nSent: {sent}\nFailed: {failed}",
            "admin_broadcast_no_users": "No registered users found for this course.",
            "admin_teacher_edit_name": "Enter teacher's full name:",
            "admin_teacher_edit_phone": "Enter teacher's phone number.\nExample: +998901234567",
            "admin_teacher_edit_social": "Send social media links.\nWrite each on a new line.\nIf not available yet, send `-`.",
            "admin_teacher_edit_bio": "Enter brief info about the teacher.\nIf not available yet, send `-`.",
            "admin_teacher_updated": "Teacher profile updated successfully.",
            "admin_new_reg_notif": "New application received.\n\nCourse: {course}\nFirst name: {first}\nLast name: {last}\nPhone: {phone}\nAddress: {addr}\nTelegram: {tg}",
            "admin_apps_empty": "No applications for {course} course yet.",
            "admin_apps_title": "Applications for {course} course:",
        }
    }

    def __init__(self, database: Database):
        self.database = database
    
    def get_user_language(self, user_id: int) -> str:
        """Get the language preference for a user. Defaults to 'uz' if not set."""
        with closing(self.database._connect()) as conn:
            row = conn.execute(
                "SELECT language FROM language_preferences WHERE user_id = ?", (user_id,)
            ).fetchone()
            return row["language"] if row else "uz"
    
    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set the language preference for a user."""
        if language not in ("ru", "en", "uz"):
            return False
        with closing(self.database._connect()) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """INSERT OR REPLACE INTO language_preferences (user_id, language, updated_at) 
                   VALUES (?, ?, ?)""",
                (user_id, language, now)
            )
            conn.commit()
            return True
            
    def get_text(self, user_id: int, key: str, **kwargs: Any) -> str:
        lang = self.get_user_language(user_id)
        return self.get_text_by_lang(lang, key, **kwargs)

    def get_text_by_lang(self, lang: str, key: str, **kwargs: Any) -> str:
        text = self.STRINGS.get(lang, self.STRINGS["uz"]).get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_all_translations(self, key: str) -> list[str]:
        return [s[key] for s in self.STRINGS.values() if key in s]


# Language code mapping for button text recognition
LANGUAGE_CODES = {
    "O'zbekcha 🇺🇿": "uz",
    "Русский 🇷🇺": "ru",
    "English 🇺🇸": "en",
}

# Reverse mapping
LANGUAGE_NAMES = {
    "uz": "O'zbekcha 🇺🇿",
    "ru": "Русский 🇷🇺",
    "en": "English 🇺🇸",
}


def get_language_from_button(button_text: str) -> Optional[str]:
    """Extract language code from language selection button text."""
    for text, code in LANGUAGE_CODES.items():
        if text in button_text:
            return code
    return None