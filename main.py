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
    MENU_TEACHER,
    admin_menu,
    cancel_keyboard,
    contact_keyboard,
    courses_inline_keyboard,
    main_menu,
)
from bot.states import AddCourseState, CourseBroadcastState, RegistrationState, TeacherProfileState


settings = Settings.from_env()
database = Database(settings.database_path)
router = Router()
TELEGRAM_TEXT_LIMIT = 3500


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


def format_registrations(course_name: str, registrations: list[Any]) -> str:
    if not registrations:
        return f"{course_name} kursi uchun hali arizalar yo'q."

    lines = [f"{course_name} kursi bo'yicha arizalar:", ""]
    for index, registration in enumerate(registrations, start=1):
        telegram_name = (
            f"@{registration['username']}"
            if registration["username"]
            else f"ID: {registration['user_id']}"
        )
        lines.extend(
            [
                f"{index}. {registration['first_name']} {registration['last_name']}",
                f"Telefon: {registration['phone']}",
                f"Manzil: {registration['address']}",
                f"Telegram: {telegram_name}",
                f"Sana: {registration['created_at']}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def format_teacher_profile(profile: Any) -> str:
    full_name = str(profile["full_name"]).strip()
    phone = str(profile["phone"]).strip()
    social_links = str(profile["social_links"]).strip()
    bio = str(profile["bio"]).strip()

    if not any([full_name, phone, social_links, bio]):
        return (
            "<b>Teacher haqida</b>\n\n"
            "Hozircha ustoz haqida ma'lumot kiritilmagan."
        )

    lines = ["<b>Teacher haqida</b>", ""]
    if full_name:
        lines.append(f"<b>Ism-familya:</b> {escape(full_name)}")
    if phone:
        lines.append(f"<b>Telefon:</b> {escape(phone)}")
    if social_links:
        lines.append("<b>Ijtimoiy tarmoqlar:</b>")
        for link in social_links.splitlines():
            clean_link = link.strip()
            if clean_link:
                lines.append(f"- {escape(clean_link)}")
    if bio:
        lines.extend(["", "<b>Qisqacha ma'lumot:</b>"])
        for line in bio.splitlines():
            clean_line = line.strip()
            if clean_line:
                lines.append(escape(clean_line))
    return "\n".join(lines)


def build_start_text(courses: list[Any], is_admin: bool) -> str:
    lines = [
        "<b>Assalomu alaykum!</b>",
        "Kasb o'rganishni bugundan boshlang.",
        "Quyidagi kurslardan birini tanlang va bir necha daqiqada ro'yxatdan o'ting.",
        "",
    ]

    if courses:
        lines.append("<b>Hozir mavjud kurslar:</b>")
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
                "Mos kursni tanlab, ariza qoldiring. Siz bilan tez orada bog'laniladi.",
            ]
        )
    else:
        lines.extend(
            [
                "Hozircha kurslar ro'yxati shakllantirilmoqda.",
                "Yaqinda yangi kurslar qo'shiladi.",
            ]
        )

    lines.append("")
    lines.append("Ustoz haqida bilish uchun <b>Teacher haqida</b> tugmasini bosing.")
    if is_admin:
        lines.append("Siz admin sifatida kurslar va teacher ma'lumotlarini ham boshqarishingiz mumkin.")
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
    text = (
        "Yangi ariza keldi.\n\n"
        f"Kurs: {course_name}\n"
        f"Ism: {registration_data['first_name']}\n"
        f"Familya: {registration_data['last_name']}\n"
        f"Telefon: {registration_data['phone']}\n"
        f"Manzil: {registration_data['address']}\n"
        f"Telegram: {telegram_name}"
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
    await message.answer(
        "Kerakli bo'limni tanlang: kurslar yoki teacher haqida ma'lumot ochishingiz mumkin.",
        reply_markup=main_menu(is_admin_user(message.from_user.id if message.from_user else None)),
    )


async def send_courses_catalog(message: Message, intro_text: str | None = None) -> None:
    courses = database.list_courses()
    if not courses:
        await message.answer("Hozircha kurslar qo'shilmagan.")
        return

    text = "\n".join(
        [
        intro_text or "Quyidagi kurslardan birini tanlang:",
        "",
            format_courses_for_user(
                courses,
                numbered=True,
                include_descriptions=False,
                name_limit=60,
            ),
        ]
    )

    chunks = split_text(text, limit=TELEGRAM_TEXT_LIMIT)
    for chunk in chunks[:-1]:
        await message.answer(chunk)
    await message.answer(
        chunks[-1],
        reply_markup=courses_inline_keyboard(courses, "course"),
    )


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    is_admin = is_admin_user(message.from_user.id if message.from_user else None)
    courses = database.list_courses()
    start_chunks = split_text(build_start_text(courses, is_admin), limit=TELEGRAM_TEXT_LIMIT)
    for index, chunk in enumerate(start_chunks):
        await message.answer(
            chunk,
            reply_markup=main_menu(is_admin) if index == 0 else None,
            parse_mode=ParseMode.HTML,
        )
    if courses:
        await message.answer(
            "Ro'yxatdan o'tish uchun pastdagi kurslardan birini tanlang:",
            reply_markup=courses_inline_keyboard(courses, "course"),
        )


@router.message(Command("admin"))
@router.message(F.text == MENU_ADMIN)
async def admin_panel_handler(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda admin panelga kirish huquqi yo'q.")
        return

    await state.clear()
    await message.answer(
        "Admin panelga xush kelibsiz. Bu yerda kurslar, arizalar va teacher ma'lumotlarini boshqarasiz.",
        reply_markup=admin_menu(),
    )


@router.message(F.text == MENU_BACK)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_menu(message)


@router.message(F.text == MENU_CANCEL)
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Amal bekor qilindi.",
        reply_markup=main_menu(is_admin_user(message.from_user.id if message.from_user else None)),
    )


@router.message(F.text == MENU_COURSES)
async def courses_handler(message: Message) -> None:
    await send_courses_catalog(
        message,
        intro_text="Ro'yxatdan o'tmoqchi bo'lgan kursingizni tanlang:",
    )


@router.message(F.text == MENU_TEACHER)
async def teacher_info_handler(message: Message) -> None:
    profile = database.get_teacher_profile()
    await message.answer(
        format_teacher_profile(profile),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(is_admin_user(message.from_user.id if message.from_user else None)),
    )


@router.message(F.text == ADMIN_SEND_COURSE_MESSAGE)
async def send_course_message_menu_handler(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await state.clear()
    courses = database.list_courses()
    if not courses:
        await message.answer("Hozircha kurslar mavjud emas.", reply_markup=admin_menu())
        return

    await message.answer(
        "Qaysi kursga xabar yubormoqchisiz?",
        reply_markup=courses_inline_keyboard(courses, "broadcast_course"),
    )


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def choose_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer("Kurs topilmadi.", show_alert=True)
        return

    if database.user_has_registration(callback.from_user.id, course_id):
        await callback.answer(
            "Siz ushbu kursga allaqachon ro'yxatdan o'tgansiz.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(course_id=course_id, course_name=course["name"])
    await state.set_state(RegistrationState.first_name)
    description = (
        f"\nTavsif: {course['description']}"
        if course["description"]
        else ""
    )
    await callback.message.answer(
        f"{course['name']} kursi tanlandi.{description}\n\nIsmingizni kiriting:",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(RegistrationState.first_name)
async def registration_first_name_handler(message: Message, state: FSMContext) -> None:
    if not message.text or not is_valid_name(message.text):
        await message.answer("Ismni to'g'ri kiriting. Masalan: Ali")
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.last_name)
    await message.answer("Familyangizni kiriting:", reply_markup=cancel_keyboard())


@router.message(RegistrationState.last_name)
async def registration_last_name_handler(message: Message, state: FSMContext) -> None:
    if not message.text or not is_valid_name(message.text):
        await message.answer("Familyani to'g'ri kiriting. Masalan: Karimov")
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer(
        "Telefon raqamingizni yuboring yoki qo'lda kiriting.\nMasalan: +998901234567",
        reply_markup=contact_keyboard(),
    )


@router.message(RegistrationState.phone)
async def registration_phone_handler(message: Message, state: FSMContext) -> None:
    phone: str | None = None
    if message.contact:
        if message.contact.user_id and message.contact.user_id != message.from_user.id:
            await message.answer("Iltimos, o'zingizning telefon raqamingizni yuboring.")
            return
        phone = normalize_phone(message.contact.phone_number)
    elif message.text:
        phone = normalize_phone(message.text)

    if phone is None:
        await message.answer(
            "Telefon raqam noto'g'ri. Masalan: +998901234567",
            reply_markup=contact_keyboard(),
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.address)
    await message.answer("Manzilingizni kiriting:", reply_markup=cancel_keyboard())


@router.message(RegistrationState.address)
async def registration_address_handler(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 5:
        await message.answer("Manzilni to'liqroq kiriting.")
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
            "Siz bu kursga oldin ro'yxatdan o'tgansiz.",
            reply_markup=main_menu(is_admin_user(message.from_user.id)),
        )
        return

    await state.clear()
    await message.answer(
        f"Siz {data['course_name']} kursiga muvaffaqiyatli ro'yxatdan o'tdingiz.",
        reply_markup=main_menu(is_admin_user(message.from_user.id)),
    )
    await send_admin_notifications(
        message.bot,
        course_name=data["course_name"],
        registration_data=registration_data,
    )


@router.message(F.text == ADMIN_ADD_COURSE)
async def add_course_start_handler(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await state.clear()
    await state.set_state(AddCourseState.name)
    await message.answer("Yangi kurs nomini kiriting:", reply_markup=cancel_keyboard())


@router.message(AddCourseState.name)
async def add_course_name_handler(message: Message, state: FSMContext) -> None:
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
        reply_markup=cancel_keyboard(),
    )


@router.message(AddCourseState.description)
async def add_course_description_handler(message: Message, state: FSMContext) -> None:
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
        reply_markup=admin_menu(),
    )


@router.message(F.text == ADMIN_EDIT_TEACHER)
async def edit_teacher_start_handler(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    await state.clear()
    profile = database.get_teacher_profile()
    await state.set_state(TeacherProfileState.full_name)
    await message.answer(
        f"{format_teacher_profile(profile)}\n\nTeacher ism-familyasini kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.message(TeacherProfileState.full_name)
async def teacher_full_name_handler(message: Message, state: FSMContext) -> None:
    if not message.text or not is_valid_name(message.text):
        await message.answer("Ism-familyani to'g'ri kiriting. Masalan: Habib Karimov")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(TeacherProfileState.phone)
    await message.answer(
        "Teacher telefon raqamini kiriting.\nMasalan: +998901234567",
        reply_markup=cancel_keyboard(),
    )


@router.message(TeacherProfileState.phone)
async def teacher_phone_handler(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Telefon raqam kiriting.")
        return

    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer("Telefon raqam noto'g'ri. Masalan: +998901234567")
        return

    await state.update_data(phone=phone)
    await state.set_state(TeacherProfileState.social_links)
    await message.answer(
        "Ijtimoiy tarmoqlar manzillarini yuboring.\n"
        "Har birini yangi qatordan yozing.\n"
        "Agar hozircha bo'lmasa `-` yuboring.",
        reply_markup=cancel_keyboard(),
    )


@router.message(TeacherProfileState.social_links)
async def teacher_social_links_handler(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Ijtimoiy tarmoq manzillarini yuboring yoki `-` yozing.")
        return

    social_links = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(social_links=social_links)
    await state.set_state(TeacherProfileState.bio)
    await message.answer(
        "Teacher haqida qisqacha ma'lumot kiriting.\n"
        "Masalan: tajribasi, dars yo'nalishi, yutuqlari.\n"
        "Agar hozircha bo'lmasa `-` yuboring.",
        reply_markup=cancel_keyboard(),
    )


@router.message(TeacherProfileState.bio)
async def teacher_bio_handler(message: Message, state: FSMContext) -> None:
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
        "Teacher ma'lumotlari muvaffaqiyatli yangilandi.",
        reply_markup=admin_menu(),
    )
    await message.answer(
        format_teacher_profile(profile),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("broadcast_course:"))
async def choose_broadcast_course_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    if not is_admin_user(callback.from_user.id):
        await callback.answer("Sizda bu amal uchun huquq yo'q.", show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer("Kurs topilmadi.", show_alert=True)
        return

    recipients = database.get_course_recipients(course_id)
    if not recipients:
        await callback.answer("Bu kurs uchun hali ro'yxatdan o'tganlar yo'q.", show_alert=True)
        return

    await state.clear()
    await state.update_data(
        broadcast_course_id=course_id,
        broadcast_course_name=course["name"],
        broadcast_recipient_count=len(recipients),
    )
    await state.set_state(CourseBroadcastState.message)
    await callback.message.answer(
        f"{course['name']} kursi tanlandi.\n"
        f"Qabul qiluvchilar soni: {len(recipients)}\n\n"
        "Endi yuboriladigan xabar matnini kiriting:",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(CourseBroadcastState.message)
async def course_broadcast_message_handler(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await state.clear()
        await message.answer("Sizda bu amal uchun huquq yo'q.")
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
            "Bu kurs uchun ro'yxatdan o'tgan userlar topilmadi.",
            reply_markup=admin_menu(),
        )
        return

    sent_count, failed_count = await send_course_broadcast(
        message.bot,
        course_name=course_name,
        recipients=recipients,
        message_text=message.text.strip(),
    )
    await state.clear()

    result_lines = [
        f"{course_name} kursi uchun xabar yuborildi.",
        f"Yuborildi: {sent_count}",
    ]
    if failed_count:
        result_lines.append(f"Yuborilmadi: {failed_count}")

    await message.answer(
        "\n".join(result_lines),
        reply_markup=admin_menu(),
    )


@router.message(F.text == ADMIN_DELETE_COURSE)
async def delete_course_menu_handler(message: Message) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    courses = database.list_courses()
    if not courses:
        await message.answer("O'chirish uchun kurs topilmadi.", reply_markup=admin_menu())
        return

    await message.answer(
        "O'chiriladigan kursni tanlang:",
        reply_markup=courses_inline_keyboard(courses, "delete_course"),
    )


@router.callback_query(F.data.startswith("delete_course:"))
async def delete_course_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    if not is_admin_user(callback.from_user.id):
        await callback.answer("Sizda bu amal uchun huquq yo'q.", show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer("Kurs topilmadi.", show_alert=True)
        return

    deleted = database.delete_course(course_id)
    if not deleted:
        await callback.answer("Kursni o'chirib bo'lmadi.", show_alert=True)
        return

    await callback.message.answer(f"{course['name']} kursi o'chirildi.")
    await callback.answer("Kurs o'chirildi.")


@router.message(F.text == ADMIN_VIEW_APPLICATIONS)
async def applications_menu_handler(message: Message) -> None:
    if not is_admin_user(message.from_user.id if message.from_user else None):
        await message.answer("Sizda bu amal uchun huquq yo'q.")
        return

    courses = database.list_courses()
    if not courses:
        await message.answer("Hozircha kurslar mavjud emas.", reply_markup=admin_menu())
        return

    await message.answer(
        "Qaysi kurs arizalarini ko'rmoqchisiz?",
        reply_markup=courses_inline_keyboard(courses, "course_apps"),
    )


@router.callback_query(F.data.startswith("course_apps:"))
async def show_applications_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    if not is_admin_user(callback.from_user.id):
        await callback.answer("Sizda bu amal uchun huquq yo'q.", show_alert=True)
        return

    course_id = int(callback.data.split(":")[1])
    course = database.get_course(course_id)
    if course is None:
        await callback.answer("Kurs topilmadi.", show_alert=True)
        return

    registrations = database.get_registrations_by_course(course_id)
    text = format_registrations(course["name"], registrations)
    for chunk in split_text(text):
        await callback.message.answer(chunk)
    await callback.answer()


@router.message()
async def fallback_handler(message: Message) -> None:
    await message.answer(
        "Iltimos, menyudagi tugmalardan foydalaning: kurslar, teacher haqida yoki /start.",
        reply_markup=main_menu(is_admin_user(message.from_user.id if message.from_user else None)),
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
