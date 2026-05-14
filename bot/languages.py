"""
Multi-language support for the bot.
Supported languages: Russian (ru), English (en), Uzbek (uz)
"""

LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "uz": "Ўзбек"
}

TEXTS = {
    "ru": {
        # Menu buttons
        "menu_courses": "🎓 Курсы",
        "menu_teacher": "👨‍🏫 О преподавателе",
        "menu_admin": "⚙️ Админ панель",
        "menu_back": "⬅️ Назад",
        "menu_cancel": "❌ Отмена",
        "menu_language": "🌐 Язык",
        
        # Admin menu
        "admin_add_course": "➕ Добавить курс",
        "admin_delete_course": "🗑️ Удалить курс",
        "admin_edit_teacher": "✏️ Редактировать информацию",
        "admin_view_applications": "📋 Просмотреть заявки",
        "admin_send_message": "📢 Отправить сообщение",
        
        # Start messages
        "greeting": "Привет!",
        "start_text": "Начните обучение профессии сегодня.",
        "select_course": "Выберите один из следующих курсов и зарегистрируйтесь за несколько минут.",
        "available_courses": "Доступные курсы:",
        "no_courses": "Курсы еще не добавлены.",
        "courses_coming": "Вскоре будут добавлены новые курсы.",
        "choose_course": "Выберите нужный курс и оставьте заявку. Мы скоро свяжемся с вами.",
        "teacher_info_button": "Нажмите кнопку <b>О преподавателе</b> для информации.",
        "admin_access": "Вы можете управлять курсами и информацией о преподавателе как администратор.",
        
        # Registration
        "enter_first_name": "Введите ваше имя:",
        "invalid_name_example": "Введите имя правильно. Например: Ахмад",
        "enter_last_name": "Введите вашу фамилию:",
        "invalid_last_name": "Введите фамилию правильно. Например: Иванов",
        "enter_phone": "Отправьте номер телефона или введите вручную.\nНапример: +998901234567",
        "invalid_phone": "Неверный номер телефона. Например: +998901234567",
        "enter_address": "Введите ваш адрес:",
        "address_too_short": "Введите полный адрес.",
        "already_registered": "Вы уже зарегистрированы на этот курс.",
        "registration_success": "Вы успешно зарегистрировались на курс {course_name}.",
        "registration_duplicate": "Вы уже регистрировались на этот курс ранее.",
        
        # Course info
        "course_selected": "Курс {course_name} выбран.",
        "course_description": "Описание: {description}",
        "course_not_found": "Курс не найден.",
        "course_added": "Курс {course_name} добавлен.",
        "course_deleted": "Курс {course_name} удален.",
        "course_deleted_error": "Не удалось удалить курс.",
        "course_exists": "Курс с таким названием уже существует.",
        "no_courses_to_delete": "Нет курсов для удаления.",
        
        # Course management
        "enter_course_name": "Введите название нового курса:",
        "course_name_short": "Введите название курса минимум из 3 символов.",
        "course_name_long": "Введите название курса короче 120 символов.",
        "enter_course_description": "Введите описание курса.\nЕсли не нужно, отправьте `-`",
        "description_required": "Введите описание или отправьте `-`",
        "description_long": "Введите описание короче 600 символов.",
        "choose_course_to_delete": "Выберите курс для удаления:",
        "choose_course_for_message": "Какому курсу отправить сообщение?",
        "choose_course_for_apps": "Какие заявки курса вы хотите просмотреть?",
        
        # Teacher profile
        "teacher_about": "О преподавателе",
        "teacher_no_info": "Информация о преподавателе еще не добавлена.",
        "teacher_name_label": "ФИ:",
        "teacher_phone_label": "Телефон:",
        "teacher_social_label": "Социальные сети:",
        "teacher_bio_label": "Информация:",
        "enter_teacher_name": "Введите ФИ преподавателя:",
        "invalid_teacher_name": "Введите ФИ правильно. Например: Ахмад Иванов",
        "enter_teacher_phone": "Введите телефон преподавателя.\nНапример: +998901234567",
        "enter_teacher_social": "Отправьте адреса социальных сетей.\nКаждый на новой строке.\nЕсли нет, отправьте `-`",
        "invalid_teacher_social": "Отправьте адреса социальных сетей или `-`",
        "enter_teacher_bio": "Введите информацию о преподавателе.\nНапример: опыт, направления, достижения.\nЕсли нет, отправьте `-`",
        "teacher_bio_short": "Введите информацию минимум из 10 символов или `-`",
        "teacher_updated": "Информация о преподавателе успешно обновлена.",
        
        # Admin panel
        "admin_welcome": "Добро пожаловать в админ панель. Здесь вы можете управлять курсами, заявками и информацией о преподавателе.",
        "admin_no_access": "У вас нет доступа к админ панели.",
        "no_permission": "У вас нет прав на это действие.",
        
        # Notifications
        "new_application": "Новая заявка.\n\nКурс: {course_name}\nИмя: {first_name}\nФамилия: {last_name}\nТелефон: {phone}\nАдрес: {address}\nTelegram: {telegram}",
        "applications_header": "Заявки по курсу {course_name}:",
        "no_applications": "Нет заявок на курс {course_name}.",
        "application_info": "{index}. {first_name} {last_name}\nТелефон: {phone}\nАдрес: {address}\nTelegram: {telegram}\nДата: {created_at}",
        
        # Broadcast
        "recipients_count": "Получатели: {count}",
        "enter_message": "Введите текст сообщения для отправки:",
        "message_too_short": "Введите более длинное сообщение.",
        "broadcast_sent": "Сообщение отправлено по курсу {course_name}.",
        "broadcast_sent_count": "Отправлено: {sent}",
        "broadcast_failed_count": "Не отправлено: {failed}",
        "no_recipients": "Нет зарегистрированных пользователей на этот курс.",
        "course_broadcast_header": "{course_name} курс сообщение:",
        
        # Pages
        "page_info": "Страница: {current}/{total}",
        "select_to_delete": "Выберите курс для удаления:",
        "select_course_apps": "Выберите курс для просмотра заявок:",
        "select_course_broadcast": "Выберите курс для отправки сообщения:",
        
        # Errors
        "use_buttons": "Пожалуйста, используйте кнопки меню: курсы, о преподавателе или /start.",
        "operation_cancelled": "Операция отменена.",
        "error": "Произошла ошибка.",
        
        # Language selection
        "select_language": "Выберите язык:",
        "language_changed": "Язык изменен на Русский.",
    },
    
    "en": {
        # Menu buttons
        "menu_courses": "🎓 Courses",
        "menu_teacher": "👨‍🏫 About Teacher",
        "menu_admin": "⚙️ Admin Panel",
        "menu_back": "⬅️ Back",
        "menu_cancel": "❌ Cancel",
        "menu_language": "🌐 Language",
        
        # Admin menu
        "admin_add_course": "➕ Add Course",
        "admin_delete_course": "🗑️ Delete Course",
        "admin_edit_teacher": "✏️ Edit Info",
        "admin_view_applications": "📋 View Applications",
        "admin_send_message": "📢 Send Message",
        
        # Start messages
        "greeting": "Hello!",
        "start_text": "Start learning a profession today.",
        "select_course": "Choose one of the courses below and register in a few minutes.",
        "available_courses": "Available courses:",
        "no_courses": "Courses have not been added yet.",
        "courses_coming": "New courses will be added soon.",
        "choose_course": "Select the right course and submit an application. We will contact you soon.",
        "teacher_info_button": "Press the <b>About Teacher</b> button for information.",
        "admin_access": "You can manage courses and teacher information as an administrator.",
        
        # Registration
        "enter_first_name": "Enter your first name:",
        "invalid_name_example": "Enter the name correctly. For example: Ahmed",
        "enter_last_name": "Enter your last name:",
        "invalid_last_name": "Enter the last name correctly. For example: Smith",
        "enter_phone": "Send your phone number or enter manually.\nFor example: +998901234567",
        "invalid_phone": "Invalid phone number. For example: +998901234567",
        "enter_address": "Enter your address:",
        "address_too_short": "Enter a complete address.",
        "already_registered": "You are already registered for this course.",
        "registration_success": "You have successfully registered for the {course_name} course.",
        "registration_duplicate": "You have already registered for this course before.",
        
        # Course info
        "course_selected": "Course {course_name} selected.",
        "course_description": "Description: {description}",
        "course_not_found": "Course not found.",
        "course_added": "Course {course_name} added.",
        "course_deleted": "Course {course_name} deleted.",
        "course_deleted_error": "Failed to delete the course.",
        "course_exists": "A course with this name already exists.",
        "no_courses_to_delete": "No courses to delete.",
        
        # Course management
        "enter_course_name": "Enter the name of the new course:",
        "course_name_short": "Enter a course name of at least 3 characters.",
        "course_name_long": "Enter a course name shorter than 120 characters.",
        "enter_course_description": "Enter the course description.\nIf not needed, send `-`",
        "description_required": "Enter a description or send `-`",
        "description_long": "Enter a description shorter than 600 characters.",
        "choose_course_to_delete": "Select a course to delete:",
        "choose_course_for_message": "Which course to send a message to?",
        "choose_course_for_apps": "Which course applications do you want to view?",
        
        # Teacher profile
        "teacher_about": "About Teacher",
        "teacher_no_info": "Teacher information has not been added yet.",
        "teacher_name_label": "Full Name:",
        "teacher_phone_label": "Phone:",
        "teacher_social_label": "Social Networks:",
        "teacher_bio_label": "Information:",
        "enter_teacher_name": "Enter teacher's full name:",
        "invalid_teacher_name": "Enter the name correctly. For example: Ahmed Smith",
        "enter_teacher_phone": "Enter teacher's phone.\nFor example: +998901234567",
        "enter_teacher_social": "Send social network addresses.\nEach on a new line.\nIf none, send `-`",
        "invalid_teacher_social": "Send social network addresses or `-`",
        "enter_teacher_bio": "Enter teacher information.\nFor example: experience, subjects, achievements.\nIf none, send `-`",
        "teacher_bio_short": "Enter information with at least 10 characters or `-`",
        "teacher_updated": "Teacher information has been successfully updated.",
        
        # Admin panel
        "admin_welcome": "Welcome to the admin panel. You can manage courses, applications, and teacher information here.",
        "admin_no_access": "You do not have access to the admin panel.",
        "no_permission": "You do not have permission for this action.",
        
        # Notifications
        "new_application": "New application.\n\nCourse: {course_name}\nName: {first_name}\nLast Name: {last_name}\nPhone: {phone}\nAddress: {address}\nTelegram: {telegram}",
        "applications_header": "Applications for {course_name} course:",
        "no_applications": "No applications for {course_name} course.",
        "application_info": "{index}. {first_name} {last_name}\nPhone: {phone}\nAddress: {address}\nTelegram: {telegram}\nDate: {created_at}",
        
        # Broadcast
        "recipients_count": "Recipients: {count}",
        "enter_message": "Enter the message text to send:",
        "message_too_short": "Enter a longer message.",
        "broadcast_sent": "Message sent for {course_name} course.",
        "broadcast_sent_count": "Sent: {sent}",
        "broadcast_failed_count": "Failed: {failed}",
        "no_recipients": "No users registered for this course.",
        "course_broadcast_header": "{course_name} course message:",
        
        # Pages
        "page_info": "Page: {current}/{total}",
        "select_to_delete": "Select a course to delete:",
        "select_course_apps": "Select a course to view applications:",
        "select_course_broadcast": "Select a course to send a message:",
        
        # Errors
        "use_buttons": "Please use the menu buttons: courses, about teacher, or /start.",
        "operation_cancelled": "Operation cancelled.",
        "error": "An error occurred.",
        
        # Language selection
        "select_language": "Select language:",
        "language_changed": "Language changed to English.",
    },
    
    "uz": {
        # Menu buttons
        "menu_courses": "🎓 Kurslar",
        "menu_teacher": "👨‍🏫 Ustoz haqida",
        "menu_admin": "⚙️ Admin paneli",
        "menu_back": "⬅️ Orqaga",
        "menu_cancel": "❌ Bekor qilish",
        "menu_language": "🌐 Til",
        
        # Admin menu
        "admin_add_course": "➕ Kurs qo'shish",
        "admin_delete_course": "🗑️ Kurs o'chirish",
        "admin_edit_teacher": "✏️ Ma'lumotni tahrirlash",
        "admin_view_applications": "📋 Arizalarni ko'rish",
        "admin_send_message": "📢 Xabar yuborish",
        
        # Start messages
        "greeting": "Assalomu alaykum!",
        "start_text": "Kasb o'rganishni bugundan boshlang.",
        "select_course": "Quyidagi kurslardan birini tanlang va bir necha daqiqada ro'yxatdan o'ting.",
        "available_courses": "Mavjud kurslar:",
        "no_courses": "Hozircha kurslar qo'shilmagan.",
        "courses_coming": "Yaqinda yangi kurslar qo'shiladi.",
        "choose_course": "Mos kursni tanlab, ariza qoldiring. Siz bilan tez orada bog'laniladi.",
        "teacher_info_button": "Ustoz haqida bilish uchun <b>Ustoz haqida</b> tugmasini bosing.",
        "admin_access": "Siz admin sifatida kurslar va ustoz ma'lumotlarini ham boshqarishingiz mumkin.",
        
        # Registration
        "enter_first_name": "Ismingizni kiriting:",
        "invalid_name_example": "Ismni to'g'ri kiriting. Masalan: Ali",
        "enter_last_name": "Familyangizni kiriting:",
        "invalid_last_name": "Familyani to'g'ri kiriting. Masalan: Karimov",
        "enter_phone": "Telefon raqamingizni yuboring yoki qo'lda kiriting.\nMasalan: +998901234567",
        "invalid_phone": "Telefon raqam noto'g'ri. Masalan: +998901234567",
        "enter_address": "Manzilingizni kiriting:",
        "address_too_short": "Manzilni to'liqroq kiriting.",
        "already_registered": "Siz ushbu kursga allaqachon ro'yxatdan o'tgansiz.",
        "registration_success": "Siz {course_name} kursiga muvaffaqiyatli ro'yxatdan o'tdingiz.",
        "registration_duplicate": "Siz bu kursga oldin ro'yxatdan o'tgansiz.",
        
        # Course info
        "course_selected": "{course_name} kursi tanlandi.",
        "course_description": "Tavsif: {description}",
        "course_not_found": "Kurs topilmadi.",
        "course_added": "{course_name} kursi qo'shildi.",
        "course_deleted": "{course_name} kursi o'chirildi.",
        "course_deleted_error": "Kursni o'chirib bo'lmadi.",
        "course_exists": "Bunday nomdagi kurs allaqachon mavjud.",
        "no_courses_to_delete": "O'chirish uchun kurs topilmadi.",
        
        # Course management
        "enter_course_name": "Yangi kurs nomini kiriting:",
        "course_name_short": "Kurs nomini kamida 3 ta belgida kiriting.",
        "course_name_long": "Kurs nomini 120 ta belgidan qisqaroq kiriting.",
        "enter_course_description": "Kurs tavsifini kiriting.\nAgar kerak bo'lmasa `-` yuboring",
        "description_required": "Tavsif kiriting yoki `-` yuboring.",
        "description_long": "Tavsifni 600 ta belgidan qisqaroq kiriting.",
        "choose_course_to_delete": "O'chiriladigan kursni tanlang:",
        "choose_course_for_message": "Qaysi kursga xabar yubormoqchisiz?",
        "choose_course_for_apps": "Qaysi kurs arizalarini ko'rmoqchisiz?",
        
        # Teacher profile
        "teacher_about": "Ustoz haqida",
        "teacher_no_info": "Hozircha ustoz haqida ma'lumot kiritilmagan.",
        "teacher_name_label": "Ism-familya:",
        "teacher_phone_label": "Telefon:",
        "teacher_social_label": "Ijtimoiy tarmoqlar:",
        "teacher_bio_label": "Ma'lumot:",
        "enter_teacher_name": "Teacher ism-familyasini kiriting:",
        "invalid_teacher_name": "Ism-familyani to'g'ri kiriting. Masalan: Habib Karimov",
        "enter_teacher_phone": "Teacher telefon raqamini kiriting.\nMasalan: +998901234567",
        "enter_teacher_social": "Ijtimoiy tarmoqlar manzillarini yuboring.\nHar birini yangi qatordan yozing.\nAgar hozircha bo'lmasa `-` yuboring.",
        "invalid_teacher_social": "Ijtimoiy tarmoq manzillarini yuboring yoki `-` yozing.",
        "enter_teacher_bio": "Teacher haqida qisqacha ma'lumot kiriting.\nMasalan: tajribasi, dars yo'nalishi, yutuqlari.\nAgar hozircha bo'lmasa `-` yuboring.",
        "teacher_bio_short": "Teacher haqida kamida 10 ta belgi bilan yozing yoki `-` yuboring.",
        "teacher_updated": "Teacher ma'lumotlari muvaffaqiyatli yangilandi.",
        
        # Admin panel
        "admin_welcome": "Admin panelga xush kelibsiz. Bu yerda kurslar, arizalar va ustoz ma'lumotlarini boshqarasiz.",
        "admin_no_access": "Sizda admin panelga kirish huquqi yo'q.",
        "no_permission": "Sizda bu amal uchun huquq yo'q.",
        
        # Notifications
        "new_application": "Yangi ariza keldi.\n\nKurs: {course_name}\nIsm: {first_name}\nFamilya: {last_name}\nTelefon: {phone}\nManzil: {address}\nTelegram: {telegram}",
        "applications_header": "{course_name} kursi bo'yicha arizalar:",
        "no_applications": "{course_name} kursi uchun hali arizalar yo'q.",
        "application_info": "{index}. {first_name} {last_name}\nTelefon: {phone}\nManzil: {address}\nTelegram: {telegram}\nSana: {created_at}",
        
        # Broadcast
        "recipients_count": "Qabul qiluvchilar soni: {count}",
        "enter_message": "Endi yuboriladigan xabar matnini kiriting:",
        "message_too_short": "Xabar matnini to'liqroq kiriting.",
        "broadcast_sent": "{course_name} kursi uchun xabar yuborildi.",
        "broadcast_sent_count": "Yuborildi: {sent}",
        "broadcast_failed_count": "Yuborilmadi: {failed}",
        "no_recipients": "Bu kurs uchun ro'yxatdan o'tgan userlar topilmadi.",
        "course_broadcast_header": "{course_name} kursi bo'yicha xabar:",
        
        # Pages
        "page_info": "Sahifa: {current}/{total}",
        "select_to_delete": "O'chiriladigan kursni tanlang:",
        "select_course_apps": "Qaysi kurs arizalarini ko'rmoqchisiz?",
        "select_course_broadcast": "Qaysi kursga xabar yubormoqchisiz?",
        
        # Errors
        "use_buttons": "Iltimos, menyudagi tugmalardan foydalaning: kurslar, ustoz haqida yoki /start.",
        "operation_cancelled": "Amal bekor qilindi.",
        "error": "Xatolik yuz berdi.",
        
        # Language selection
        "select_language": "Tilni tanlang:",
        "language_changed": "Til Ўзбекча tilga o'zgartirildi.",
    }
}

def get_text(language: str, key: str, **kwargs) -> str:
    """Get translated text for a key in a specific language."""
    if language not in TEXTS:
        language = "uz"  # Default to Uzbek
    
    text = TEXTS[language].get(key, f"[{key}]")
    
    # Replace placeholders
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text
