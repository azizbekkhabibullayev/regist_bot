from __future__ import annotations

from collections.abc import Mapping, Sequence

from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


MENU_COURSES = "Kurslar"
MENU_TEACHER = "Teacher haqida"
MENU_ADMIN = "Admin panel"
MENU_BACK = "Bosh menyu"
MENU_CANCEL = "Bekor qilish"

ADMIN_ADD_COURSE = "Kurs qo'shish"
ADMIN_DELETE_COURSE = "Kursni o'chirish"
ADMIN_VIEW_APPLICATIONS = "Arizalarni ko'rish"
ADMIN_EDIT_TEACHER = "Teacher ma'lumotini sozlash"
ADMIN_SEND_COURSE_MESSAGE = "Kursga xabar yuborish"


def shorten_button_text(value: str, limit: int = 40) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def main_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    keyboard = [[
        KeyboardButton(text=MENU_COURSES),
        KeyboardButton(text=MENU_TEACHER),
    ]]
    if is_admin:
        keyboard.append([KeyboardButton(text=MENU_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADMIN_ADD_COURSE)],
            [KeyboardButton(text=ADMIN_DELETE_COURSE)],
            [KeyboardButton(text=ADMIN_VIEW_APPLICATIONS)],
            [KeyboardButton(text=ADMIN_SEND_COURSE_MESSAGE)],
            [KeyboardButton(text=ADMIN_EDIT_TEACHER)],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=MENU_CANCEL)]],
        resize_keyboard=True,
    )


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)],
            [KeyboardButton(text=MENU_CANCEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def courses_inline_keyboard(
    courses: Sequence[Mapping[str, object]],
    prefix: str,
    *,
    page: int = 0,
    per_page: int = 8,
):
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
                    text="◀️ Oldingi",
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
                    text="Keyingi ▶️",
                    callback_data=f"page:{prefix}:{page + 1}",
                )
            )
        builder.row(*navigation_row)
    return builder.as_markup()
