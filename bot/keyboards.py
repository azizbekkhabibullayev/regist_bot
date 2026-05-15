from __future__ import annotations

from collections.abc import Mapping, Sequence

from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def shorten_button_text(value: str, limit: int = 40) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def main_menu(is_admin: bool, lang: str = "uz") -> ReplyKeyboardMarkup:
    from bot.language_manager import LanguageManager
    strings = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
    
    keyboard = [[
        KeyboardButton(text=strings["menu_courses"]),
        KeyboardButton(text=strings["menu_teacher"]),
    ]]
    keyboard.append([KeyboardButton(text=strings["menu_lang"])])
    if is_admin:
        # Admin paneli odatda bir xil tilda qolgani ma'qul, lekin uni ham o'zgartirsa bo'ladi
        keyboard.append([KeyboardButton(text=strings["menu_admin"])])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def admin_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
    from bot.language_manager import LanguageManager
    s = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=s["admin_menu_add"]), KeyboardButton(text=s["admin_menu_del"])],
            [KeyboardButton(text=s["admin_menu_apps"]), KeyboardButton(text=s["admin_menu_send"])],
            [KeyboardButton(text=s["admin_menu_teacher"])],
            [KeyboardButton(text=s["menu_back"])],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    from bot.language_manager import LanguageManager
    s = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s["menu_cancel"])]],
        resize_keyboard=True,
    )


def language_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    from bot.language_manager import LanguageManager
    s = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="O'zbekcha 🇺🇿"), KeyboardButton(text="Русский 🇷🇺")],
            [KeyboardButton(text="English 🇺🇸"), KeyboardButton(text=s["menu_cancel"])],
        ],
        resize_keyboard=True,
    )


def contact_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    from bot.language_manager import LanguageManager
    s = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=s["send_phone_btn"], request_contact=True)],
            [KeyboardButton(text=s["menu_cancel"])],
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
    lang: str = "uz"
):
    from bot.language_manager import LanguageManager
    s = LanguageManager.STRINGS.get(lang, LanguageManager.STRINGS["uz"])
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
                    text=s["prev_btn"],
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
                    text=s["next_btn"],
                    callback_data=f"page:{prefix}:{page + 1}",
                )
            )
        builder.row(*navigation_row)
    return builder.as_markup()
