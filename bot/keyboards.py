from __future__ import annotations

from collections.abc import Mapping, Sequence

from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.languages import get_text, LANGUAGES


def shorten_button_text(value: str, limit: int = 40) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def main_menu(is_admin: bool, language: str = "uz") -> ReplyKeyboardMarkup:
    """Main menu keyboard with language support."""
    keyboard = [[
        KeyboardButton(text=get_text(language, "menu_courses")),
        KeyboardButton(text=get_text(language, "menu_teacher")),
    ]]
    if is_admin:
        keyboard.append([KeyboardButton(text=get_text(language, "menu_admin"))])
    keyboard.append([KeyboardButton(text=get_text(language, "menu_language"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def admin_menu(language: str = "uz") -> ReplyKeyboardMarkup:
    """Admin panel menu keyboard with language support."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(language, "admin_add_course"))],
            [KeyboardButton(text=get_text(language, "admin_delete_course"))],
            [KeyboardButton(text=get_text(language, "admin_view_applications"))],
            [KeyboardButton(text=get_text(language, "admin_send_message"))],
            [KeyboardButton(text=get_text(language, "admin_edit_teacher"))],
            [KeyboardButton(text=get_text(language, "menu_back"))],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard(language: str = "uz") -> ReplyKeyboardMarkup:
    """Cancel button keyboard with language support."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text(language, "menu_cancel"))]],
        resize_keyboard=True,
    )


def contact_keyboard(language: str = "uz") -> ReplyKeyboardMarkup:
    """Contact sharing keyboard with language support."""
    contact_button_text = {
        "ru": "Отправить номер телефона",
        "en": "Send phone number",
        "uz": "Telefon raqamni yuborish",
    }.get(language, "Telefon raqamni yuborish")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=contact_button_text, request_contact=True)],
            [KeyboardButton(text=get_text(language, "menu_cancel"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def language_selection_keyboard() -> ReplyKeyboardMarkup:
    """Language selection keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"🇺🇿 {LANGUAGES['uz']}")],
            [KeyboardButton(text=f"🇷🇺 {LANGUAGES['ru']}")],
            [KeyboardButton(text=f"🇬🇧 {LANGUAGES['en']}")],
        ],
        resize_keyboard=True,
    )


def courses_inline_keyboard(
    courses: Sequence[Mapping[str, object]],
    prefix: str,
    *,
    language: str = "uz",
    page: int = 0,
    per_page: int = 8,
):
    """Courses pagination keyboard with language support."""
    builder = InlineKeyboardBuilder()

    total_courses = len(courses)
    start_index = page * per_page
    end_index = start_index + per_page
    page_courses = courses[start_index:end_index]

    for course in page_courses:
        builder.button(
            text=shorten_button_text(str(course["name"])),
            callback_data=f"{prefix}:{int(course['id'])}",
        )

    builder.adjust(1)

    total_pages = max(1, (total_courses + per_page - 1) // per_page)
    if total_pages > 1:
        navigation_row: list[InlineKeyboardButton] = []
        if page > 0:
            navigation_row.append(
                InlineKeyboardButton(
                    text="◀️ " + ("Oldingi" if language == "uz" else "Назад" if language == "ru" else "Previous"),
                    callback_data=f"page:{prefix}:{page - 1}",
                )
            )
        navigation_row.append(
            InlineKeyboardButton(
                text=f"{page + 1}/{total_pages}",
                callback_data="noop",
            )
        )
        if page < total_pages - 1:
            navigation_row.append(
                InlineKeyboardButton(
                    text=("Keyingi" if language == "uz" else "Далее" if language == "ru" else "Next") + " ▶️",
                    callback_data=f"page:{prefix}:{page + 1}",
                )
            )
        builder.row(*navigation_row)
    return builder.as_markup()


# Legacy constants for backwards compatibility
MENU_COURSES = "Kurslar"
MENU_TEACHER = "Teacher haqida"
MENU_ADMIN = "Admin panel"
MENU_BACK = "Bosh menyu"
MENU_CANCEL = "Bekor qilish"
MENU_LANGUAGE = "Til"

ADMIN_ADD_COURSE = "Kurs qo'shish"
ADMIN_DELETE_COURSE = "Kursni o'chirish"
ADMIN_VIEW_APPLICATIONS = "Arizalarni ko'rish"
ADMIN_EDIT_TEACHER = "Teacher ma'lumotini sozlash"
ADMIN_SEND_COURSE_MESSAGE = "Kursga xabar yuborish"
