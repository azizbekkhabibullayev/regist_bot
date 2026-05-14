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
from bot.keyboards import (
    ADMIN_ADD_COURSE,
    ADMIN_DELETE_COURSE,
    ADMIN_EDIT_TEACHER,
    ADMIN_SEND_COURSE_MESSAGE,
    ADMIN_VIEW_APPLICATIONS,
    MENU_ADMIN,
    MENU_BACK,
    MENU_CANCEL,
    MENU_COURSES,
    MENU_LANGUAGE,
    MENU_TEACHER,
    admin_menu,
    cancel_keyboard,
    contact_keyboard,
    courses_inline_keyboard,
    language_selection_keyboard,
    main_menu,
)
from bot.language_manager import LanguageManager, get_language_from_button
from bot.languages import get_text
from bot.states import AddCourseState, CourseBroadcastState, RegistrationState, TeacherProfileState


settings = Settings.from_env()
database = Database(settings.database_path)
language_manager = LanguageManager(database)
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


def format_registrations(course_name: str, registrations: list[Any], language: str = "uz") -> str:
    if not registrations:
        return get_text(language, "no_applications", course_name=course_name)

    lines = [get_text(language, "applications_header", course_name=course_name), ""]
    for index, registration in enumerate(registrations, start=1):
        telegram_name = (
            f"@{registration['username']}"
            if registration["username"]
            else f"ID: {registration['user_id']}"
        )
        phone_label = {"ru": "Телефон", "en": "Phone", "uz": "Telefon"}.get(language, "Telefon")
        address_label = {"ru": "Адрес", "en": "Address", "uz": "Manzil"}.get(language, "Manzil")
        date_label = {"ru": "Дата", "en": "Date", "uz": "Sana"}.get(language, "Sana")
        
        lines.extend(
            [
                f"{index}. {registration['first_name']} {registration['last_name']}",
                f"{phone_label}: {registration['phone']}",
                f"{address_label}: {registration['address']}",
                f"Telegram: {telegram_name}",
                f"{date_label}: {registration['created_at']}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def format_teacher_profile(profile: Any, language: str = "uz") -> str:
    full_name = str(profile["full_name"]).strip()
    phone = str(profile["phone"]).strip()
    social_links = str(profile["social_links"]).strip()
    bio = str(profile["bio"]).strip()

    if not any([full_name, phone, social_links, bio]):
        return get_text(language, "teacher_no_info")

    lines = [f"<b>{get_text(language, 'teacher_about')}</b>", ""]
    if full_name:
        lines.append(f"<b>{get_text(language, 'teacher_name_label')}</b> {escape(full_name)}")
    if phone:
        lines.append(f"<b>{get_text(language, 'teacher_phone_label')}</b> {escape(phone)}")
    if social_links:
        lines.append(f"<b>{get_text(language, 'teacher_social_label')}</b>")
        for link in social_links.splitlines():
            clean_link = link.strip()
            if clean_link:
                lines.append(f"- {escape(clean_link)}")
    if bio:
        lines.extend(["", f"<b>{get_text(language, 'teacher_bio_label')}</b>"])
        for line in bio.splitlines():
            clean_line = line.strip()
            if clean_line:
                lines.append(escape(clean_line))
    return "\n".join(lines)


def build_start_text(courses: list[Any], is_admin: bool, language: str = "uz") -> str:
    lines = [
        f"<b>{get_text(language, 'greeting')}</b>",
        get_text(language, "start_text"),
        get_text(language, "select_course"),
        "",
    ]

    if courses:
        lines.append(f"<b>{get_text(language, 'available_courses')}</b>")
        lines.append(
            format_courses_for_user(
                courses,
                numbered=True,
                html_safe=True,
                include_descriptions=False,
                name_limit=60,
            )
        )
        lines.extend(
            [
                "",
                get_text(language, "choose_course"),
            ]
        )
    else:
        lines.extend(
            [
                get_text(language, "no_courses"),
                get_text(language, "courses_coming"),
            ]
        )

    lines.append("")
    lines.append(get_text(language, "teacher_info_button"))
    if is_admin:
        lines.append(get_text(language, "admin_access"))
    return "\n".join(lines)


async def send_admin_notifications(
    bot: Bot,
    *,
    course_name: str,
    registration_data: dict[str, Any],
    language: str = "uz",
) -> None:
    if not settings.admin_ids:
        return

    username = registration_data.get("username")
    telegram_name = f"@{username}" if username else f"ID: {registration_data['user_id']}"
    text = get_text(
        language,
        "new_application",
        course_name=course_name,
        first_name=registration_data['first_name'],
        last_name=registration_data['last_name'],
        phone=registration_data['phone'],
        address=registration_data['address'],
        telegram=telegram_name,
    )

    for admin_id in settings.admin_ids:
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
    language: str = "uz",
) -> tuple[int, int]:
    sent_count = 0
    failed_count = 0
    header = get_text(language, "course_broadcast_header", course_name=course_name)
    text = f"{header}\n\n{message_text}"

    for recipient in recipients:
        try:
            await bot.send_message(recipient["user_id"], text)
            sent_count += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed_count += 1

    return sent_count, failed_count


async def show_main_menu(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await state.clear()
    await message.answer(
        get_text(language, "use_buttons"),
        reply_markup=main_menu(is_admin_user(user_id), language),
    )


async def send_courses_catalog(message: Message, intro_text: str | None = None, language: str = "uz") -> None:
    courses = database.list_courses()
    if not courses:
        await message.answer(get_text(language, "no_courses"))
        return

    total_pages = max(1, (len(courses) + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE)
    text = f"{intro_text or get_text(language, 'choose_course')}\n\n{get_text(language, 'page_info', current=1, total=total_pages)}"
    await message.answer(
        text,
        reply_markup=courses_inline_keyboard(
            courses,
            "course",
            language=language,
            page=0,
            per_page=COURSES_PER_PAGE,
        ),
    )


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    
    await state.clear()
    is_admin = is_admin_user(user_id)
    courses = database.list_courses()
    start_chunks = split_text(build_start_text(courses, is_admin, language), limit=TELEGRAM_TEXT_LIMIT)
    for index, chunk in enumerate(start_chunks):
        await message.answer(
            chunk,
            reply_markup=main_menu(is_admin, language) if index == 0 else None,
            parse_mode=ParseMode.HTML,
        )
    if courses:
        select_text = get_text(language, "choose_course")
        await message.answer(
            select_text,
            reply_markup=courses_inline_keyboard(
                courses,
                "course",
                language=language,
                page=0,
                per_page=COURSES_PER_PAGE,
            ),
        )


@router.message(F.text == MENU_LANGUAGE)
async def language_selection_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await message.answer(
        get_text(language, "select_language"),
        reply_markup=language_selection_keyboard(),
    )


@router.message(F.text.contains("🇺🇿") | F.text.contains("🇷🇺") | F.text.contains("🇬🇧"))
async def language_change_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    new_language = get_language_from_button(message.text)
    
    if new_language and user_id:
        language_manager.set_user_language(user_id, new_language)
        await state.clear()
        await message.answer(
            get_text(new_language, "language_changed"),
            reply_markup=main_menu(is_admin_user(user_id), new_language),
        )
    else:
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await show_main_menu(message, state)


@router.message(Command("admin"))
@router.message(F.text == MENU_ADMIN)
async def admin_panel_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "admin_no_access"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await state.clear()
    await message.answer(
        get_text(language, "admin_welcome"),
        reply_markup=admin_menu(language),
    )


@router.message(F.text == MENU_BACK)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await show_main_menu(message, state)


@router.message(F.text == MENU_CANCEL)
async def cancel_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    
    await state.clear()
    await message.answer(
        get_text(language, "operation_cancelled"),
        reply_markup=main_menu(is_admin_user(user_id), language),
    )


@router.message(F.text == MENU_COURSES)
async def courses_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await send_courses_catalog(message, language=language)


@router.message(F.text == MENU_TEACHER)
async def teacher_info_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    
    profile = database.get_teacher_profile()
    await message.answer(
        format_teacher_profile(profile, language),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(is_admin_user(user_id), language),
    )


@router.message(F.text == ADMIN_SEND_COURSE_MESSAGE)
async def send_course_message_menu_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await state.clear()
    courses = database.list_courses()
    if not courses:
        await message.answer(get_text(language, "no_courses"), reply_markup=admin_menu(language))
        return

    await message.answer(
        get_text(language, "choose_course_for_message"),
        reply_markup=courses_inline_keyboard(
            courses,
            "broadcast_course",
            language=language,
            page=0,
            per_page=COURSES_PER_PAGE,
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

    user_id = callback.from_user.id
    language = language_manager.get_user_language(user_id)
    
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return

    prefix = parts[1]
    page = int(parts[2])
    courses = database.list_courses()
    if not courses:
        await callback.answer(get_text(language, "no_courses"), show_alert=True)
        return

    total_pages = max(1, (len(courses) + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    if prefix == "course":
        text = f"{get_text(language, 'choose_course')}\n\n{get_text(language, 'page_info', current=page + 1, total=total_pages)}"
    elif prefix == "delete_course":
        if not is_admin_user(user_id):
            await callback.answer(get_text(language, "no_permission"), show_alert=True)
            return
        text = f"{get_text(language, 'select_to_delete')}\n\n{get_text(language, 'page_info', current=page + 1, total=total_pages)}"
    elif prefix == "course_apps":
        if not is_admin_user(user_id):
            await callback.answer(get_text(language, "no_permission"), show_alert=True)
            return
        text = f"{get_text(language, 'select_course_apps')}\n\n{get_text(language, 'page_info', current=page + 1, total=total_pages)}"
    elif prefix == "broadcast_course":
        if not is_admin_user(user_id):
            await callback.answer(get_text(language, "no_permission"), show_alert=True)
            return
        text = f"{get_text(language, 'select_course_broadcast')}\n\n{get_text(language, 'page_info', current=page + 1, total=total_pages)}"
    else:
        await callback.answer()
        return

    await callback.message.edit_text(
        text,
        reply_markup=courses_inline_keyboard(
            courses,
            prefix,
            language=language,
            page=page,
            per_page=COURSES_PER_PAGE,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def choose_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = language_manager.get_user_language(user_id)
    
    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(get_text(language, "course_not_found"), show_alert=True)
        return

    if database.user_has_registration(user_id, course_id):
        await callback.answer(
            get_text(language, "already_registered"),
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(course_id=course_id, course_name=course["name"], language=language)
    await state.set_state(RegistrationState.first_name)
    description = (
        f"\n{get_text(language, 'course_description', description=course['description'])}"
        if course["description"]
        else ""
    )
    await callback.message.answer(
        f"{get_text(language, 'course_selected', course_name=course['name'])}{description}\n\n{get_text(language, 'enter_first_name')}",
        reply_markup=cancel_keyboard(language),
    )
    await callback.answer()


@router.message(RegistrationState.first_name)
async def registration_first_name_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or not is_valid_name(message.text):
        await message.answer(get_text(language, "invalid_name_example"))
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.last_name)
    await message.answer(get_text(language, "enter_last_name"), reply_markup=cancel_keyboard(language))


@router.message(RegistrationState.last_name)
async def registration_last_name_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or not is_valid_name(message.text):
        await message.answer(get_text(language, "invalid_last_name"))
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer(
        get_text(language, "enter_phone"),
        reply_markup=contact_keyboard(language),
    )


@router.message(RegistrationState.phone)
async def registration_phone_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    phone: str | None = None
    if message.contact:
        if message.contact.user_id and message.contact.user_id != message.from_user.id:
            await message.answer(get_text(language, "enter_phone"))
            return
        phone = normalize_phone(message.contact.phone_number)
    elif message.text:
        phone = normalize_phone(message.text)

    if phone is None:
        await message.answer(
            get_text(language, "invalid_phone"),
            reply_markup=contact_keyboard(language),
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.address)
    await message.answer(get_text(language, "enter_address"), reply_markup=cancel_keyboard(language))


@router.message(RegistrationState.address)
async def registration_address_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or len(message.text.strip()) < 5:
        await message.answer(get_text(language, "address_too_short"))
        return

    user_id = message.from_user.id
    registration_data = {
        "user_id": user_id,
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
            get_text(language, "registration_duplicate"),
            reply_markup=main_menu(is_admin_user(user_id), language),
        )
        return

    await state.clear()
    await message.answer(
        get_text(language, "registration_success", course_name=data['course_name']),
        reply_markup=main_menu(is_admin_user(user_id), language),
    )
    await send_admin_notifications(
        message.bot,
        course_name=data["course_name"],
        registration_data=registration_data,
        language=language,
    )


@router.message(F.text == ADMIN_ADD_COURSE)
async def add_course_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await state.clear()
    await state.set_state(AddCourseState.name)
    await state.update_data(language=language)
    await message.answer(get_text(language, "enter_course_name"), reply_markup=cancel_keyboard(language))


@router.message(AddCourseState.name)
async def add_course_name_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or len(message.text.strip()) < 3:
        await message.answer(get_text(language, "course_name_short"))
        return
    if len(message.text.strip()) > 120:
        await message.answer(get_text(language, "course_name_long"))
        return

    await state.update_data(name=message.text.strip())
    await state.set_state(AddCourseState.description)
    await message.answer(
        get_text(language, "enter_course_description"),
        reply_markup=cancel_keyboard(language),
    )


@router.message(AddCourseState.description)
async def add_course_description_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text:
        await message.answer(get_text(language, "description_required"))
        return
    if message.text.strip() != "-" and len(message.text.strip()) > 600:
        await message.answer(get_text(language, "description_long"))
        return

    description = None if message.text.strip() == "-" else message.text.strip()

    try:
        database.add_course(data["name"], description)
    except sqlite3.IntegrityError:
        await message.answer(get_text(language, "course_exists"))
        return

    await state.clear()
    await message.answer(
        get_text(language, "course_added", course_name=data['name']),
        reply_markup=admin_menu(language),
    )


@router.message(F.text == ADMIN_EDIT_TEACHER)
async def edit_teacher_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    await state.clear()
    profile = database.get_teacher_profile()
    await state.set_state(TeacherProfileState.full_name)
    await state.update_data(language=language)
    await message.answer(
        f"{format_teacher_profile(profile, language)}\n\n{get_text(language, 'enter_teacher_name')}",
        reply_markup=cancel_keyboard(language),
        parse_mode=ParseMode.HTML,
    )


@router.message(TeacherProfileState.full_name)
async def teacher_full_name_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or not is_valid_name(message.text):
        await message.answer(get_text(language, "invalid_teacher_name"))
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(TeacherProfileState.phone)
    await message.answer(
        get_text(language, "enter_teacher_phone"),
        reply_markup=cancel_keyboard(language),
    )


@router.message(TeacherProfileState.phone)
async def teacher_phone_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text:
        await message.answer(get_text(language, "invalid_phone"))
        return

    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(get_text(language, "invalid_phone"))
        return

    await state.update_data(phone=phone)
    await state.set_state(TeacherProfileState.social_links)
    await message.answer(
        get_text(language, "enter_teacher_social"),
        reply_markup=cancel_keyboard(language),
    )


@router.message(TeacherProfileState.social_links)
async def teacher_social_links_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text:
        await message.answer(get_text(language, "invalid_teacher_social"))
        return

    social_links = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(social_links=social_links)
    await state.set_state(TeacherProfileState.bio)
    await message.answer(
        get_text(language, "enter_teacher_bio"),
        reply_markup=cancel_keyboard(language),
    )


@router.message(TeacherProfileState.bio)
async def teacher_bio_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text:
        await message.answer(get_text(language, "teacher_bio_short"))
        return

    bio_text = "" if message.text.strip() == "-" else message.text.strip()
    if bio_text and len(bio_text) < 10:
        await message.answer(get_text(language, "teacher_bio_short"))
        return

    database.update_teacher_profile(
        full_name=data["full_name"],
        phone=data["phone"],
        social_links=data["social_links"],
        bio=bio_text,
    )
    await state.clear()

    profile = database.get_teacher_profile()
    await message.answer(
        get_text(language, "teacher_updated"),
        reply_markup=admin_menu(language),
    )
    await message.answer(
        format_teacher_profile(profile, language),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("broadcast_course:"))
async def choose_broadcast_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id)
        await callback.answer(get_text(language, "no_permission"), show_alert=True)
        return

    language = language_manager.get_user_language(user_id)
    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(get_text(language, "course_not_found"), show_alert=True)
        return

    recipients = database.get_course_recipients(course_id)
    if not recipients:
        await callback.answer(get_text(language, "no_recipients"), show_alert=True)
        return

    await state.clear()
    await state.update_data(
        broadcast_course_id=course_id,
        broadcast_course_name=course["name"],
        broadcast_recipient_count=len(recipients),
        language=language,
    )
    await state.set_state(CourseBroadcastState.message)
    await callback.message.answer(
        f"{get_text(language, 'course_selected', course_name=course['name'])}\n"
        f"{get_text(language, 'recipients_count', count=len(recipients))}\n\n"
        f"{get_text(language, 'enter_message')}",
        reply_markup=cancel_keyboard(language),
    )
    await callback.answer()


@router.message(CourseBroadcastState.message)
async def course_broadcast_message_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        await state.clear()
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    data = await state.get_data()
    language = data.get("language", "uz")
    
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(get_text(language, "message_too_short"))
        return

    course_id = data["broadcast_course_id"]
    course_name = data["broadcast_course_name"]
    recipients = database.get_course_recipients(course_id)

    if not recipients:
        await state.clear()
        await message.answer(
            get_text(language, "no_recipients"),
            reply_markup=admin_menu(language),
        )
        return

    sent_count, failed_count = await send_course_broadcast(
        message.bot,
        course_name=course_name,
        recipients=recipients,
        message_text=message.text.strip(),
        language=language,
    )
    await state.clear()

    result_lines = [
        get_text(language, "broadcast_sent", course_name=course_name),
        get_text(language, "broadcast_sent_count", sent=sent_count),
    ]
    if failed_count:
        result_lines.append(get_text(language, "broadcast_failed_count", failed=failed_count))

    await message.answer(
        "\n".join(result_lines),
        reply_markup=admin_menu(language),
    )


@router.message(F.text == ADMIN_DELETE_COURSE)
async def delete_course_menu_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    courses = database.list_courses()
    if not courses:
        await message.answer(get_text(language, "no_courses_to_delete"), reply_markup=admin_menu(language))
        return

    await message.answer(
        get_text(language, "select_to_delete"),
        reply_markup=courses_inline_keyboard(
            courses,
            "delete_course",
            language=language,
            page=0,
            per_page=COURSES_PER_PAGE,
        ),
    )


@router.callback_query(F.data.startswith("delete_course:"))
async def delete_course_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = language_manager.get_user_language(user_id)
    
    if not is_admin_user(user_id):
        await callback.answer(get_text(language, "no_permission"), show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(get_text(language, "course_not_found"), show_alert=True)
        return

    deleted = database.delete_course(course_id)
    if not deleted:
        await callback.answer(get_text(language, "course_deleted_error"), show_alert=True)
        return

    await callback.message.answer(get_text(language, "course_deleted", course_name=course['name']))
    await callback.answer(get_text(language, "course_deleted", course_name=course['name']))


@router.message(F.text == ADMIN_VIEW_APPLICATIONS)
async def applications_menu_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    
    if not is_admin_user(user_id):
        language = language_manager.get_user_language(user_id) if user_id else "uz"
        await message.answer(get_text(language, "no_permission"))
        return

    language = language_manager.get_user_language(user_id) if user_id else "uz"
    courses = database.list_courses()
    if not courses:
        await message.answer(get_text(language, "no_courses"), reply_markup=admin_menu(language))
        return

    await message.answer(
        get_text(language, "select_course_apps"),
        reply_markup=courses_inline_keyboard(
            courses,
            "course_apps",
            language=language,
            page=0,
            per_page=COURSES_PER_PAGE,
        ),
    )


@router.callback_query(F.data.startswith("course_apps:"))
async def show_applications_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = language_manager.get_user_language(user_id)
    
    if not is_admin_user(user_id):
        await callback.answer(get_text(language, "no_permission"), show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer(get_text(language, "course_not_found"), show_alert=True)
        return

    registrations = database.get_registrations_by_course(course_id)
    text = format_registrations(course["name"], registrations, language)
    for chunk in split_text(text):
        await callback.message.answer(chunk)
    await callback.answer()


@router.message()
async def fallback_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    language = language_manager.get_user_language(user_id) if user_id else "uz"
    
    await message.answer(
        get_text(language, "use_buttons"),
        reply_markup=main_menu(is_admin_user(user_id), language),
    )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    database.init()
    # Initialize language preferences table
    language_manager.create_preferences_table()
    
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    bot = Bot(token=settings.bot_token)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
