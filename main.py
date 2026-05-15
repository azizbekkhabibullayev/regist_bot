from __future__ import annotations

import asyncio
import logging
import sqlite3
from html import escape
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.database import Database
from bot.language_manager import LanguageManager, LANGUAGE_CODES
from bot.keyboards import (
    admin_menu,
    cancel_keyboard,
    contact_keyboard,
    courses_inline_keyboard,
    language_keyboard,
    main_menu,
)
from bot.states import AddCourseState, CourseBroadcastState, RegistrationState, TeacherProfileState, LanguageState


settings = Settings.from_env()
database = Database(settings.database_path)
lang_manager = LanguageManager(database)
router = Router()
TELEGRAM_TEXT_LIMIT = 3500
COURSES_PER_PAGE = 8


def is_admin_user(user_id: int | None) -> bool:
    return user_id is not None and user_id in settings.admin_ids


def normalize_phone(value: str) -> str | None:
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("00"):
        cleaned = f"+{cleaned[2:]}"
    if cleaned and cleaned[0] != "+" and cleaned.isdigit():
        cleaned = f"+{cleaned}"
    digits_only = cleaned[1:] if cleaned.startswith("+") else cleaned
    if not digits_only.isdigit():
        return None
    if not 9 <= len(digits_only) <= 15:
        return None
    return cleaned


def is_valid_name(value: str) -> bool:
    text = value.strip()
    return len(text) >= 2 and not any(char.isdigit() for char in text)


def split_text(text: str, limit: int = 3500) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    chunk: list[str] = []
    current_length = 0

    for line in text.splitlines():
        if len(line) > limit:
            if chunk:
                parts.append("\n".join(chunk))
                chunk = []
                current_length = 0

            start_index = 0
            while start_index < len(line):
                parts.append(line[start_index : start_index + limit])
                start_index += limit
            continue

        next_length = current_length + len(line) + 1
        if chunk and next_length > limit:
            parts.append("\n".join(chunk))
            chunk = [line]
            current_length = len(line) + 1
        else:
            chunk.append(line)
            current_length = next_length

    if chunk:
        parts.append("\n".join(chunk))
    return parts


def shorten_text(value: str, limit: int = 90) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def format_courses_for_user(
    courses: list[Any],
    *,
    numbered: bool = False,
    html_safe: bool = False,
    include_descriptions: bool = True,
    name_limit: int = 70,
    description_limit: int = 90,
) -> str:
    lines: list[str] = []
    for index, course in enumerate(courses, start=1):
        name = shorten_text(str(course["name"]), name_limit)
        description = str(course["description"]).strip() if course["description"] else ""
        if description:
            description = shorten_text(description, description_limit)
        if html_safe:
            name = escape(name)
            description = escape(description)

        prefix = f"{index}." if numbered else "-"
        line = f"{prefix} {name}"
        if include_descriptions and description:
            line = f"{line}: {description}"
        lines.append(line)
    return "\n".join(lines)


def format_registrations(course_name: str, registrations: list[Any], lang: str) -> str:
    if not registrations:
        return lang_manager.get_text_by_lang(lang, "admin_apps_empty", course=course_name)

    lines = [lang_manager.get_text_by_lang(lang, "admin_apps_title", course=course_name), ""]
    for index, registration in enumerate(registrations, start=1):
        telegram_name = (
            f"@{registration['username']}"
            if registration["username"]
            else f"ID: {registration['user_id']}"
        )
        lines.extend(
            [
                f"{index}. {registration['first_name']} {registration['last_name']}",
                f"{lang_manager.get_text_by_lang(lang, 'field_phone')} {registration['phone']}",
                f"{lang_manager.get_text_by_lang(lang, 'enter_address')} {registration['address']}",
                f"Telegram: {telegram_name}",
                f"Sana: {registration['created_at']}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def format_teacher_profile(profile: Any, lang: str) -> str:
    full_name = str(profile["full_name"]).strip()
    phone = str(profile["phone"]).strip()
    social_links = str(profile["social_links"]).strip()
    bio = str(profile["bio"]).strip()

    if not any([full_name, phone, social_links, bio]):
        return lang_manager.get_text_by_lang(lang, "teacher_not_set")

    lines = [lang_manager.get_text_by_lang(lang, "teacher_profile_title"), ""]
    if full_name:
        lines.append(f"{lang_manager.get_text_by_lang(lang, 'field_full_name')} {escape(full_name)}")
    if phone:
        lines.append(f"{lang_manager.get_text_by_lang(lang, 'field_phone')} {escape(phone)}")
    if social_links:
        lines.append(lang_manager.get_text_by_lang(lang, "field_social"))
        for link in social_links.splitlines():
            clean_link = link.strip()
            if clean_link:
                lines.append(f"- {escape(clean_link)}")
    if bio:
        lines.extend(["", lang_manager.get_text_by_lang(lang, "field_bio")])
        for line in bio.splitlines():
            clean_line = line.strip()
            if clean_line:
                lines.append(escape(clean_line))
    return "\n".join(lines)


def build_start_text(courses: list[Any], is_admin: bool, lang: str) -> str:
    lines = [lang_manager.get_text_by_lang(lang, "welcome"), ""]

    if courses:
        lines.append(lang_manager.get_text_by_lang(lang, "start_available"))
        lines.append(
            format_courses_for_user(
                courses,
                numbered=True,
                html_safe=True,
                include_descriptions=False,
                name_limit=60,
            )
        )
    else:
        lines.append(lang_manager.get_text_by_lang(lang, "start_empty"))

    lines.append("")
    lines.append(lang_manager.get_text_by_lang(lang, "start_teacher"))
    if is_admin:
        lines.append(lang_manager.get_text_by_lang(lang, "start_admin"))
    return "\n".join(lines)


async def send_admin_notifications(
    bot: Bot,
    *,
    course_name: str,
    registration_data: dict[str, Any],
) -> None:
    if not settings.admin_ids:
        return

    username = registration_data.get("username")
    telegram_name = f"@{username}" if username else f"ID: {registration_data['user_id']}"
    for admin_id in settings.admin_ids:
        admin_lang = lang_manager.get_user_language(admin_id)
        text = lang_manager.get_text_by_lang(
            admin_lang, "admin_new_reg_notif",
            course=course_name,
            first=registration_data['first_name'],
            last=registration_data['last_name'],
            phone=registration_data['phone'],
            addr=registration_data['address'],
            tg=telegram_name
        )
        try:
            await bot.send_message(admin_id, text)
        except (TelegramForbiddenError, TelegramBadRequest):
            continue


async def send_course_broadcast(
    bot: Bot,
    *,
    course_name: str,
    recipients: list[Any],
    message_text: str,
) -> tuple[int, int]:
    sent_count = 0
    failed_count = 0
    text = f"{course_name} kursi bo'yicha xabar:\n\n{message_text}"

    for recipient in recipients:
        try:
            await bot.send_message(recipient["user_id"], text)
            sent_count += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed_count += 1

    return sent_count, failed_count


async def show_main_menu(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    is_admin = is_admin_user(message.from_user.id if message.from_user else None)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "welcome"),
        reply_markup=main_menu(is_admin, lang=user_lang),
        parse_mode=ParseMode.HTML
    )


@router.message(F.text.in_(lang_manager.get_all_translations("menu_lang")))
async def change_language_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    await state.set_state(LanguageState.choosing_language)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "choose_lang"),
        reply_markup=language_keyboard(user_lang),
    )


@router.message(LanguageState.choosing_language)
async def process_language_choice(message: Message, state: FSMContext) -> None:
    code = LANGUAGE_CODES.get(message.text or "")
    if message.text in lang_manager.get_all_translations("menu_cancel"):
        await state.clear()
        await show_main_menu(message)
        return

    if not code:
        await message.answer("Select language / Tilni tanlang / Выберите язык")
        return

    lang_manager.set_user_language(message.from_user.id, code)
    await state.clear()
    
    success_text = lang_manager.get_text_by_lang(code, "lang_changed")
    await message.answer(success_text, reply_markup=main_menu(is_admin_user(message.from_user.id), lang=code))


async def send_courses_catalog(message: Message, intro_text: str | None = None) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    courses = database.list_courses()
    if not courses:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "no_courses"))
        return

    total_pages = max(1, (len(courses) + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE)
    text = f"{intro_text or lang_manager.get_text_by_lang(user_lang, 'select_course')}\n\nSahifa: 1/{total_pages}"
    await message.answer(
        text,
        reply_markup=courses_inline_keyboard(
            courses,
            "course",
            page=0,
            per_page=COURSES_PER_PAGE,
            lang=user_lang
        ),
    )


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_lang = lang_manager.get_user_language(user_id)
    is_admin = is_admin_user(message.from_user.id if message.from_user else None)
    courses = database.list_courses()
    start_chunks = split_text(build_start_text(courses, is_admin, user_lang), limit=TELEGRAM_TEXT_LIMIT)
    for index, chunk in enumerate(start_chunks):
        await message.answer(
            chunk,
            reply_markup=main_menu(is_admin, lang=user_lang) if index == 0 else None,
            parse_mode=ParseMode.HTML,
        )


@router.message(Command("admin"))
@router.message(F.text.in_(lang_manager.get_all_translations("menu_admin")))
async def admin_panel_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    await state.clear()
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_welcome"),
        reply_markup=admin_menu(user_lang),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("menu_back")))
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_menu(message)


@router.message(F.text.in_(lang_manager.get_all_translations("menu_cancel")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    await state.clear()
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "action_cancelled"),
        reply_markup=main_menu(is_admin_user(message.from_user.id), lang=user_lang),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("menu_courses")))
async def courses_handler(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    await send_courses_catalog(
        message,
        intro_text=lang_manager.get_text_by_lang(user_lang, "select_course"),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("menu_teacher")))
async def teacher_info_handler(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    profile = database.get_teacher_profile()
    await message.answer(
        format_teacher_profile(profile, user_lang),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(is_admin_user(message.from_user.id), lang=user_lang),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("admin_menu_send")))
async def send_course_message_menu_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    await state.clear()
    courses = database.list_courses()
    if not courses:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_courses"), reply_markup=admin_menu(user_lang))
        return

    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_broadcast_select"),
        reply_markup=courses_inline_keyboard(
            courses,
            "broadcast_course",
            page=0,
            per_page=COURSES_PER_PAGE,
            lang=user_lang
        ),
    )


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("page:"))
async def course_pagination_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return

    prefix = parts[1]
    page = int(parts[2])
    courses = database.list_courses()
    user_lang = lang_manager.get_user_language(callback.from_user.id)
    if not courses:
        await callback.answer("Hozircha kurslar yo'q.", show_alert=True)
        return

    total_pages = max(1, (len(courses) + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    if prefix == "course":
        text = f"{lang_manager.get_text_by_lang(user_lang, 'select_course')}\n\nSahifa: {page + 1}/{total_pages}"
    elif prefix == "delete_course":
        if not is_admin_user(callback.from_user.id):
            await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
            return
        text = f"{lang_manager.get_text_by_lang(user_lang, 'admin_course_del_select')}\n\nSahifa: {page + 1}/{total_pages}"
    elif prefix == "course_apps":
        if not is_admin_user(callback.from_user.id):
            await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
            return
        text = f"{lang_manager.get_text_by_lang(user_lang, 'admin_apps_select')}\n\nSahifa: {page + 1}/{total_pages}"
    elif prefix == "broadcast_course":
        if not is_admin_user(callback.from_user.id):
            await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
            return
        text = f"{lang_manager.get_text_by_lang(user_lang, 'admin_broadcast_select')}\n\nSahifa: {page + 1}/{total_pages}"
    else:
        await callback.answer()
        return

    await callback.message.edit_text(
        text,
        reply_markup=courses_inline_keyboard(
            courses,
            prefix,
            page=page,
            per_page=COURSES_PER_PAGE,
            lang=user_lang
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def choose_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_lang = lang_manager.get_user_language(callback.from_user.id)
    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_not_found"), show_alert=True)
        return

    if database.user_has_registration(callback.from_user.id, course_id):
        await callback.answer(
            lang_manager.get_text_by_lang(user_lang, "already_registered"),
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(course_id=course_id, course_name=course["name"])
    await state.set_state(RegistrationState.first_name)
    
    course_text = lang_manager.get_text_by_lang(user_lang, "course_selected", course_name=course["name"])
    if course["description"]:
        course_text += lang_manager.get_text_by_lang(user_lang, "course_desc", description=course["description"])
    
    await callback.message.answer(
        f"{course_text}\n\n{lang_manager.get_text_by_lang(user_lang, 'enter_first_name')}",
        reply_markup=cancel_keyboard(user_lang),
    )
    await callback.answer()


@router.message(RegistrationState.first_name)
async def registration_first_name_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text or not is_valid_name(message.text):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "invalid_name"))
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.last_name)
    await message.answer(lang_manager.get_text_by_lang(user_lang, "enter_last_name"), reply_markup=cancel_keyboard(user_lang))


@router.message(RegistrationState.last_name)
async def registration_last_name_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text or not is_valid_name(message.text):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "invalid_name"))
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "enter_phone"),
        reply_markup=contact_keyboard(user_lang),
    )


@router.message(RegistrationState.phone)
async def registration_phone_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    phone: str | None = None
    if message.contact:
        if message.contact.user_id and message.contact.user_id != message.from_user.id:
            await message.answer(lang_manager.get_text_by_lang(user_lang, "invalid_phone"))
            return
        phone = normalize_phone(message.contact.phone_number)
    elif message.text:
        phone = normalize_phone(message.text)

    if phone is None:
        await message.answer(
            lang_manager.get_text_by_lang(user_lang, "invalid_phone"),
            reply_markup=contact_keyboard(user_lang),
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.address)
    await message.answer(lang_manager.get_text_by_lang(user_lang, "enter_address"), reply_markup=cancel_keyboard(user_lang))


@router.message(RegistrationState.address)
async def registration_address_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text or len(message.text.strip()) < 5:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "invalid_address"))
        return

    data = await state.get_data()
    registration_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "phone": data["phone"],
        "address": message.text.strip(),
        "course_id": data["course_id"],
    }

    try:
        database.add_registration(**registration_data)
    except sqlite3.IntegrityError:
        await state.clear()
        await message.answer(
            lang_manager.get_text_by_lang(user_lang, "already_registered"),
            reply_markup=main_menu(is_admin_user(message.from_user.id), lang=user_lang),
        )
        return

    await state.clear()
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "reg_success", course_name=data["course_name"]),
        reply_markup=main_menu(is_admin_user(message.from_user.id), lang=user_lang),
    )
    await send_admin_notifications(
        message.bot,
        course_name=data["course_name"],
        registration_data=registration_data,
    )


@router.message(F.text.in_(lang_manager.get_all_translations("admin_menu_add")))
async def add_course_start_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await state.clear()
    await state.set_state(AddCourseState.name)
    await message.answer("Yangi kurs nomini kiriting:", reply_markup=cancel_keyboard(user_lang))


@router.message(AddCourseState.name)
async def add_course_name_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Kurs nomini kamida 3 ta belgida kiriting.")
        return
    if len(message.text.strip()) > 120:
        await message.answer("Kurs nomini 120 ta belgidan qisqaroq kiriting.")
        return

    await state.update_data(name=message.text.strip())
    await state.set_state(AddCourseState.description)
    await message.answer(
        "Kurs tavsifini kiriting.\nAgar kerak bo'lmasa `-` yuboring.",
        reply_markup=cancel_keyboard(user_lang),
    )


@router.message(AddCourseState.description)
async def add_course_description_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text:
        await message.answer("Tavsif kiriting yoki `-` yuboring.")
        return
    if message.text.strip() != "-" and len(message.text.strip()) > 600:
        await message.answer("Tavsifni 600 ta belgidan qisqaroq kiriting.")
        return

    data = await state.get_data()
    description = None if message.text.strip() == "-" else message.text.strip()

    try:
        database.add_course(data["name"], description)
    except sqlite3.IntegrityError:
        await message.answer("Bunday nomdagi kurs allaqachon mavjud.")
        return

    await state.clear()
    await message.answer(
        f"{data['name']} kursi qo'shildi.",
        reply_markup=admin_menu(user_lang),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("admin_menu_teacher")))
async def edit_teacher_start_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    await state.clear()
    profile = database.get_teacher_profile()
    await state.set_state(TeacherProfileState.full_name)
    await message.answer(
        f"{format_teacher_profile(profile, user_lang)}\n\n{lang_manager.get_text_by_lang(user_lang, 'admin_teacher_edit_name')}",
        reply_markup=cancel_keyboard(user_lang),
        parse_mode=ParseMode.HTML,
    )


@router.message(TeacherProfileState.full_name)
async def teacher_full_name_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text or not is_valid_name(message.text):
        await message.answer("Ism-familyani to'g'ri kiriting. Masalan: Habib Karimov")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(TeacherProfileState.phone)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_teacher_edit_phone"),
        reply_markup=cancel_keyboard(user_lang),
    )


@router.message(TeacherProfileState.phone)
async def teacher_phone_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    phone = normalize_phone(message.text or "")
    if phone is None:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "invalid_phone"))
        return

    await state.update_data(phone=phone)
    await state.set_state(TeacherProfileState.social_links)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_teacher_edit_social"),
        reply_markup=cancel_keyboard(user_lang),
    )


@router.message(TeacherProfileState.social_links)
async def teacher_social_links_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text:
        await message.answer("Ijtimoiy tarmoq manzillarini yuboring yoki `-` yozing.")
        return

    social_links = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(social_links=social_links)
    await state.set_state(TeacherProfileState.bio)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_teacher_edit_bio"),
        reply_markup=cancel_keyboard(user_lang),
    )


@router.message(TeacherProfileState.bio)
async def teacher_bio_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not message.text:
        await message.answer("Qisqacha ma'lumot kiriting yoki `-` yozing.")
        return

    bio_text = "" if message.text.strip() == "-" else message.text.strip()
    if bio_text and len(bio_text) < 10:
        await message.answer("Teacher haqida kamida 10 ta belgi bilan yozing yoki `-` yuboring.")
        return

    data = await state.get_data()
    database.update_teacher_profile(
        full_name=data["full_name"],
        phone=data["phone"],
        social_links=data["social_links"],
        bio=bio_text,
    )
    await state.clear()
    profile = database.get_teacher_profile()
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_teacher_updated"),
        reply_markup=admin_menu(user_lang),
    )
    await message.answer(
        format_teacher_profile(profile, user_lang),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("broadcast_course:"))
async def choose_broadcast_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_lang = lang_manager.get_user_language(callback.from_user.id)
    if not is_admin_user(callback.from_user.id):
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_not_found"), show_alert=True)
        return

    recipients = database.get_course_recipients(course_id)
    if not recipients:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_broadcast_no_users"), show_alert=True)
        return

    await state.clear()
    await state.update_data(
        broadcast_course_id=course_id,
        broadcast_course_name=course["name"],
        broadcast_recipient_count=len(recipients),
    )
    await state.set_state(CourseBroadcastState.message)
    await callback.message.answer(
        lang_manager.get_text_by_lang(user_lang, "course_selected", course_name=course['name']) + 
        f"\n\n{lang_manager.get_text_by_lang(user_lang, 'admin_broadcast_prompt')}",
        reply_markup=cancel_keyboard(user_lang),
    )
    await callback.answer()


@router.message(CourseBroadcastState.message)
async def course_broadcast_message_handler(message: Message, state: FSMContext) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await state.clear()
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Xabar matnini to'liqroq kiriting.")
        return

    data = await state.get_data()
    course_id = data["broadcast_course_id"]
    course_name = data["broadcast_course_name"]
    recipients = database.get_course_recipients(course_id)

    if not recipients:
        await state.clear()
        await message.answer(
            lang_manager.get_text_by_lang(user_lang, "admin_broadcast_no_users"),
            reply_markup=admin_menu(user_lang),
        )
        return

    sent_count, failed_count = await send_course_broadcast(
        message.bot,
        course_name=course_name,
        recipients=recipients,
        message_text=message.text.strip(),
    )
    await state.clear()

    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_broadcast_status", name=course_name, sent=sent_count, failed=failed_count),
        reply_markup=admin_menu(user_lang),
    )


@router.message(F.text.in_(lang_manager.get_all_translations("admin_menu_del")))
async def delete_course_menu_handler(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    courses = database.list_courses()
    if not courses:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_courses"), reply_markup=admin_menu(user_lang))
        return

    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_course_del_select"),
        reply_markup=courses_inline_keyboard(
            courses,
            "delete_course",
            page=0,
            per_page=COURSES_PER_PAGE,
        ),
    )


@router.callback_query(F.data.startswith("delete_course:"))
async def delete_course_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_lang = lang_manager.get_user_language(callback.from_user.id)
    if not is_admin_user(callback.from_user.id):
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_not_found"), show_alert=True)
        return

    deleted = database.delete_course(course_id)
    if not deleted:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_del_fail"), show_alert=True)
        return

    await callback.message.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_del_success", name=course['name']))
    await callback.answer("Kurs o'chirildi.")


@router.message(F.text.in_(lang_manager.get_all_translations("admin_menu_apps")))
async def applications_menu_handler(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"))
        return

    courses = database.list_courses()
    if not courses:
        await message.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_courses"), reply_markup=admin_menu(user_lang))
        return

    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "admin_apps_select"),
        reply_markup=courses_inline_keyboard(
            courses,
            "course_apps",
            page=0,
            per_page=COURSES_PER_PAGE,
        ),
    )


@router.callback_query(F.data.startswith("course_apps:"))
async def show_applications_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_lang = lang_manager.get_user_language(callback.from_user.id)
    if not is_admin_user(callback.from_user.id):
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_no_permission"), show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(lang_manager.get_text_by_lang(user_lang, "admin_course_not_found"), show_alert=True)
        return

    registrations = database.get_registrations_by_course(course_id)
    text = format_registrations(course["name"], registrations, user_lang)
    for chunk in split_text(text):
        await callback.message.answer(chunk)
    await callback.answer()


@router.message()
async def fallback_handler(message: Message) -> None:
    user_lang = lang_manager.get_user_language(message.from_user.id)
    await message.answer(
        lang_manager.get_text_by_lang(user_lang, "fallback"),
        reply_markup=main_menu(is_admin_user(message.from_user.id), lang=user_lang),
    )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    database.init()
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    bot = Bot(token=settings.bot_token)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
