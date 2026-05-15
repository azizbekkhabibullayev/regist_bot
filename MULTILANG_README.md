# Registration Bot - Multi-Language Support

Ushbu bot **3 ta tilda** ishlaydi: **Ўзбек**, **Русский** va **English**

---

## 📋 Xususiyatlar (Features)

### Tilda Qo'llab-Quvvatlash (Language Support)
- 🇺🇿 **Ўзбек тили** (Uzbek)
- 🇷🇺 **Русский язык** (Russian)
- 🇬🇧 **English**

Bot har bir foydalanuvchi uchun uning tanlagan tilida xizmat ko'rsatadi.

---

## 🚀 Boshlash (Getting Started)

### O'rnatish (Installation)

```bash
# Kerakli kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### Bot Ishga Tushirish (Running the Bot)

```bash
python main.py
```

---

## 🌐 Tilda O'zgartiRISH (Changing Language)

1. Asosiy menyudan **"🌐 Til"** tugmasini bosing
2. Kerakli tilda tugmasini tanlang:
   - 🇺🇿 Ўзбек
   - 🇷🇺 Русский
   - 🇬🇧 English
3. Bot siz bilan shu tildan gaplashishni boshlaydi

Sizning tanlash bot bazasida saqlanadi va keyingi suhbatlarda eslab qoladi.

---

## 📁 Fayl Strukturasi (File Structure)

```
regist_bot/
├── main.py                          # Botning asosiy faylı
├── bot/
│   ├── config.py                   # Konfiguratsiya
│   ├── database.py                 # Ma'lumotlar bazasi
│   ├── keyboards.py                # Tugmalar (tilga mos)
│   ├── states.py                   # FSM davlatlar
│   ├── languages.py                # Tildagi matnlar
│   ├── language_manager.py         # Til boshqaruvi
│   └── migrations.py               # Bazani migratsiya
├── requirements.txt
└── README.md
```

---

## 🎯 Tilga Mos Xususiyatlar (Language-Specific Features)

### Foydalanuvchi Interfeysı (User Interface)
Barcha matnlar, tugmalar va xabarlar foydalanuvchining tanlagan tilida ko'rsatiladi:
- Asosiy menyu
- Ro'yxatdan o'tish formasi
- Xato xabarlar
- Muvaffaqiyat xabarlar

### Admin Paneli (Admin Panel)
Admin panelining barcha xabarlari ham tilga mos:
- Arizalarni ko'rish
- Kurs boshqaruvi
- Xabar yuborish
- Ustoz ma'lumotlarini tahrirlash

---

## 💾 Ma'lumotlar Bazasi (Database)

Tilda qo'llab-quvvatlash uchun quyidagi jadvallar yaratiladi:

```sql
-- Foydalanuvchining til qo'llanmasi
CREATE TABLE language_preferences (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'uz' CHECK(language IN ('ru', 'en', 'uz')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📝 Tillar va Kodlar (Languages and Codes)

| Til (Language) | Kod (Code) | Tugma (Button) |
|---|---|---|
| Ўзбек | `uz` | 🇺🇿 Ўзбек |
| Русский | `ru` | 🇷🇺 Русский |
| English | `en` | 🇬🇧 English |

---

## 🔧 Til Qo'shish (Adding a New Language)

Yangi til qo'shish uchun:

### 1. `bot/languages.py` ga matnlar qo'shish

```python
TEXTS = {
    "new_lang": {
        "menu_courses": "Your text here",
        "menu_teacher": "Your text here",
        # ... boshqa barcha matnlar
    }
}

LANGUAGES = {
    "new_lang": "Language Name",
}
```

### 2. `bot/keyboards.py` ga tugmalarni qo'shish

```python
def language_selection_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 Ўзбек")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇬🇧 English")],
            [KeyboardButton(text="🆕 Your Language")],  # Yangi til
        ],
        resize_keyboard=True,
    )
```

### 3. `bot/language_manager.py` ga kod qo'shish

```python
LANGUAGE_CODES = {
    "Ўзбек": "uz",
    "Русский": "ru",
    "English": "en",
    "Your Language": "new_lang",  # Yangi kod
}
```

---

## 🔄 Imkon-Funksiyalar (Features)

### ✅ Amalga Oshirilgan
- [x] 3 tilda toliq qo'llab-quvvatlash
- [x] Foydalanuvchining til qo'lanmasi saqlanishi
- [x] Admin paneli tilga mos
- [x] Ro'yxatdan o'tish tilga mos
- [x] Kurs boshqaruvi tilga mos
- [x] Xato xabarlar tilga mos

### 📋 Kelasi Ishlar (Future Enhancements)
- [ ] Yangi tillar qo'shish
- [ ] Tilni avtomatik aniqlash
- [ ] RTL (Ўzbekcha, Arabcha) qo'llab-quvvatlash
- [ ] Til fayllarini lokalizatsiya qilish

---

## 🐛 Xatolikni Tuzatish (Troubleshooting)

### Til o'zgarmadi
**Sabab:** Language preferences jadvali yaratilmagan
**Yechim:** Botni qayta ishga tushiring
```bash
python main.py
```

### Matn ko'rsatilmadi
**Sabab:** `languages.py` da matn yo'q
**Yechim:** `languages.py` faylida barcha matnlarni tekshiring

### Tugma ko'rsatilmadi
**Sabab:** `language_manager.py` da kod ro'yxatiga qo'shilmagan
**Yechim:** `LANGUAGE_CODES` ga yangi kodni qo'shing

---

## 📞 Yordam (Support)

Muammolar yoki taklif uchun GitHub issues yarating:
https://github.com/azizbekkhabibullayev/regist_bot/issues

---

## 📄 Litsenziya (License)

Bu loyiha MIT litsenziyasi ostida.

---

## 👨‍💻 Muallif (Author)

**Aziz Bekkhabibullayev**
- GitHub: [@azizbekkhabibullayev](https://github.com/azizbekkhabibullayev)

---

## 🎉 Rahmat Qo'llashgan Uchun!

Ushbu multi-language bot-ni foydalanganingiz uchun raxmat! 🚀

Agar bot foydali bo'lsa, ⭐ bering!
