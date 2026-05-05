from __future__ import annotations

from collections.abc import Mapping, Sequence

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
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
):
    builder = InlineKeyboardBuilder()
    for course in courses:
        builder.button(
            text=str(course["name"]),
            callback_data=f"{prefix}:{int(course['id'])}",
        )
    builder.adjust(1)
    return builder.as_markup()
