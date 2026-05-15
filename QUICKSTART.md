# 🚀 Tezkor Boshlash Qo'llanmasi (Quick Start Guide)

## 3 Ta Tildagi Bot (Bot in 3 Languages)

Bu qo'llanma `regist_bot` ning **multi-language** xususiyatidan foydalanishni o'rgatadi.

---

## ⚡ Dastlabki 5 Daqiqa (First 5 Minutes)

### 1. Bot Ishga Tushirish (Start Bot)
```bash
python main.py
```

### 2. Telegram Bot Bilan Bog'lanish (Connect to Telegram)
- Telegram App ochish
- Bot usernamesi qidirish
- `/start` komandasi yuborish

### 3. Tilni Tanlash (Select Language)
- Asosiy menyudan **"🌐 Til"** tugmasini bosish
- Kerakli tilni tanlash:
  - 🇺🇿 Ўзбек
  - 🇷🇺 Русский
  - 🇬🇧 English

**Tayyor!** Bot siz bilan tanlagan tildan gaplashadi.

---

## 🌐 Tillar (Languages)

| Til | Kod | Tugma |
|---|---|---|
| Ўзбек | `uz` | 🇺🇿 |
| Русский | `ru` | 🇷🇺 |
| English | `en` | 🇬🇧 |

---

## 📱 Foydalanuvchi Qo'llanmasi (User Guide)

### Kurs Tanlash (Select Course)
1. **"🎓 Kurslar"** tugmasini bosing
2. Kerakli kursni tanlang
3. Ro'yxatdan o'tish formasi tilida ko'rsatiladi

### Ro'yxatdan O'tish (Register)
1. **Ismingizni** kiriting
2. **Familyangizni** kiriting
3. **Telefon raqamingizni** yuboring
4. **Manzilingizni** kiriting

**Barcha matnlar tanlagan tilida!**

### Ustoz Haqida (About Teacher)
- **"👨‍🏫 Ustoz haqida"** tugmasini bosing
- Ustoz ma'lumotlari tilida ko'rsatiladi

### Tilni O'zgartiRISH (Change Language)
1. **"🌐 Til"** tugmasini bosing
2. Yangi tilni tanlang
3. Bot yangi tilga o'tadi

---

## 👨‍💼 Admin Qo'llanmasi (Admin Guide)

### Admin Panelga Kirish (Enter Admin Panel)
1. **"⚙️ Admin panel"** tugmasini bosing
2. Admin menyusi tilida ko'rsatiladi

### Kurs Qo'shish (Add Course)
```
➕ Kurs qo'shish
├─ Kurs nomini kiriting
└─ Kurs tavsifini kiriting
```

### Arizalarni Ko'rish (View Applications)
```
📋 Arizalarni ko'rish
├─ Kursni tanlang
└─ Arizalar tilida ko'rsatiladi
```

### Ustoz Ma'lumotlarini Tahrirlash (Edit Teacher Info)
```
✏️ Ma'lumotni tahrirlash
├─ Ism-familyasini kiriting
├─ Telefon raqamini kiriting
├─ Ijtimoiy tarmoqlarni kiriting
└─ Qisqacha ma'lumot kiriting
```

### Xabar Yuborish (Send Message)
```
📢 Xabar yuborish
├─ Kursni tanlang
└─ Xabar matnini kiriting
```

**Barcha admin operatsiyalari admin tilida!**

---

## 🔧 Texnik Ma'lumot (Technical Info)

### Til Saqlanish (Language Storage)
```
SQLite Database
└── language_preferences
    ├── user_id (INTEGER)
    ├── language (TEXT: 'uz', 'ru', 'en')
    └── updated_at (TIMESTAMP)
```

### Til Olish (Get Language)
```python
from bot.language_manager import language_manager

user_language = language_manager.get_user_language(user_id)
# Natija: 'uz', 'ru', yoki 'en'
```

### Matn Olish (Get Text)
```python
from bot.languages import get_text

text = get_text('uz', 'greeting')  # "Assalomu alaykum!"
text = get_text('ru', 'greeting')  # "Привет!"
text = get_text('en', 'greeting')  # "Hello!"
```

---

## 📁 Muhim Fayllar (Important Files)

```
regist_bot/
├── main.py                    # Bot logikasi (til qo'llab-quvvatlash bilan)
├── bot/
│   ├── languages.py          # 📝 BARCHA TILLAR VA MATNLAR
│   ├── keyboards.py          # 🎨 TUGMALAR (TIL PARAMETRI BILAN)
│   ├── language_manager.py   # 💾 TIL BOSHQARUVI
│   └── migrations.py         # 🔧 DATABASE MIGRATSIYA
├── MULTILANG_README.md       # 📖 TO'LIQ DOKUMENTATSIYA
└── IMPLEMENTATION_SUMMARY.md # 📋 IMPLEMENTATION HAQIDA
```

---

## ❓ Tez-Tez Savollar (FAQ)

### S: Yangi til qo'shish mumkinmi?
**J:** Ha! `bot/languages.py` ga matnlar qo'shing va `language_manager.py` ga kod qo'shing.

### S: Mening til eslab qolinadimi?
**J:** Ha! Bot til qo'lanmasini SQLite bazasida saqlab turadi. Keyingi sessiyada ayniy til ishlaydi.

### S: Admin xabarlar qaysi tilida yuboriladi?
**J:** Foydalanuvchining tanlagan tilida! Har bir user o'z tilida admin xabarlarini oladi.

### S: Eski tilga qaytish mumkinmi?
**J:** Ha! "🌐 Til" tugmasidan yangi til tanlashingiz mumkin.

### S: Agar til tanlanmasa nima bo'ladi?
**J:** Default til **Ўзбек (uz)** ishlatiladi.

---

## 🎯 Xususiyatlar Ro'yxati (Feature Checklist)

### Barcha Tillar Qo'llab-Quvvatlanadi ✅
- [x] 🇺🇿 Ўзбек (Uzbek)
- [x] 🇷🇺 Русский (Russian)
- [x] 🇬🇧 English (English)

### Barcha Joylar Til Qo'llab-Quvvatlanadi ✅
- [x] Asosiy menyu
- [x] Ro'yxatdan o'tish
- [x] Kurs boshqaruvi
- [x] Admin paneli
- [x] Xato xabarlari
- [x] Muvaffaqiyat xabarlari
- [x] Admin notifikatsiyalari

---

## 🚀 Keyingi Qadamlar (Next Steps)

1. **Bo'lim 1:** Bot konfiguratsiyasi (`bot/config.py`)
2. **Bo'lim 2:** Ma'lumotlar bazasi (`bot/database.py`)
3. **Bo'lim 3:** Til qo'shish (`bot/languages.py`)
4. **Bo'lim 4:** Admin funksiyalari (`main.py`)

---

## 📞 Yordam va Qo'llab-Quvvatlash (Support)

### Muammolar
- GitHub Issues: https://github.com/azizbekkhabibullayev/regist_bot/issues
- Email: [muallif email]

### Dokumentatsiya
- **MULTILANG_README.md** - To'liq qo'llanma
- **IMPLEMENTATION_SUMMARY.md** - Implementation haqida
- **bot/languages.py** - Tillar manbasi

---

## 💡 Maslahatlar (Tips)

1. **Til o'zgartiRISH oson** - Har vaqt "🌐 Til" tugmasini bosing
2. **Matnlarni o'zgartiRISH oson** - `bot/languages.py` ni tahrirlang
3. **Tillar qo'shish oson** - 3 ta faylga qo'shish kerak
4. **Admin xabarlari hamyoniy** - Foydalanuvchining tilida yuboriladi

---

## 🎓 O'quv Resurslari (Learning Resources)

### Boshlangichlar Uchun
- Bot buyruqlari: `/start`, `/admin`
- Tugmalar: Menyuda ko'rsatilgan
- Tillar: Yuqorida ro'yxatdan

### Dasturchilar Uchun
- `bot/languages.py` - Tillar struktura
- `bot/language_manager.py` - API haqida
- `main.py` - Integratsiya misollari

### Admin Uchun
- Admin paneli funksiyalari
- Kurs boshqaruvi
- Xabar yuborish

---

## ✨ Xamchasi (Summary)

**regist_bot** endi 3 tilda to'liq qo'llab-quvvatladi:
- 🇺🇿 Ўзбек
- 🇷🇺 Русский
- 🇬🇧 English

Foydalanuvchilar o'z tillarida to'liq xizmat olishlari mumkin!

---

**Boshlash:** `/start` komandasi yuborish  
**Tilni o'zgartiRISH:** "🌐 Til" tugmasini bosish  
**Admin Panel:** "⚙️ Admin panel" tugmasini bosish  

**Xush kelibsiz! 🚀**

---

*Oxirgi update: 2026-05-15*  
*Muallif: azizbekkhabibullayev*
