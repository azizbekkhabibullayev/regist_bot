# Kursga Ro'yxatdan O'tish Telegram Boti

Bu loyiha `Python + aiogram + SQLite` asosida yozilgan Telegram bot bo'lib, kurslarga ro'yxatdan o'tishni avtomatlashtiradi.

## Imkoniyatlar

- Admin kurs yo'nalishlarini qo'shadi
- Admin kurslarni o'chira oladi
- Admin har bir kurs bo'yicha kelgan arizalarni ko'radi
- Admin har bir kursga alohida xabar yubora oladi
- Admin `Teacher haqida` bo'limidagi ma'lumotlarni yangilaydi
- Foydalanuvchi kursni tanlab ro'yxatdan o'tadi
- Ro'yxatdan o'tishda `ism`, `familya`, `telefon`, `manzil` saqlanadi
- `/start` da kurslarga taklif matni va mavjud kurslar ro'yxati chiqadi
- Foydalanuvchi `Teacher haqida` tugmasi orqali ustoz va aloqa ma'lumotlarini ko'radi
- Yangi ariza kelganda adminlarga xabar yuboriladi

## O'rnatish

1. Virtual muhit yarating:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Kutubxonalarni o'rnating:

```powershell
pip install -r requirements.txt
```

3. `.env.example` faylidan nusxa olib `.env` yarating va quyidagilarni to'ldiring:

```env
BOT_TOKEN=BotFather dan olingan token
ADMIN_IDS=123456789,987654321
DATABASE_PATH=data/bot.db
```

`ADMIN_IDS` ga admin Telegram `user_id` lari vergul bilan yoziladi.

4. Botni ishga tushiring:

```powershell
python main.py
```

## Foydalanish

- Oddiy foydalanuvchi `/start` bosadi
- `Kurslar` tugmasini bosib kurs tanlaydi
- `ism`, `familya`, `telefon`, `manzil` kiritadi
- Bot arizani bazaga saqlaydi

Admin uchun:

- `/start` yoki `/admin` dan `Admin panel` ga kiradi
- `Kurs qo'shish` orqali yangi kurs yaratadi
- `Kursni o'chirish` orqali kursni o'chiradi
- `Arizalarni ko'rish` orqali kurs bo'yicha kelgan arizalarni ko'radi
- `Kursga xabar yuborish` orqali faqat tanlangan kursga yozilgan userlarga xabar yuboradi
- `Teacher ma'lumotini sozlash` orqali ism-familya, telefon, ijtimoiy tarmoqlar va qisqacha ma'lumotni yangilaydi

## Asosiy fayllar

- `main.py` - botning asosiy ishga tushirish fayli
- `bot/database.py` - SQLite bilan ishlash
- `bot/keyboards.py` - tugmalar
- `bot/states.py` - formalar holati
- `bot/config.py` - `.env` konfiguratsiyasi

## Railway ga Deploy

Loyihada [railway.json](./railway.json) qo'shilgan. U Railway uchun `python main.py` start command'ini belgilaydi.

### 1. GitHub ga yuklang

Loyihani GitHub repository'ga push qiling.

### 2. Railway project yarating

- Railway ichida `New Project` bosing
- `Deploy from GitHub repo` ni tanlang
- Shu repository'ni ulang

### 3. Environment variables qo'shing

Railway service ichida `Variables` bo'limiga quyidagilarni kiriting:

```env
BOT_TOKEN=BotFather dan olingan token
ADMIN_IDS=123456789,987654321
DATABASE_PATH=data/bot.db
```

### 4. SQLite uchun Volume ulang

Bu bot `SQLite` ishlatadi. Agar volume ulamasangiz, deploy yoki restartdan keyin baza yo'qolishi mumkin.

Railway'da volume yarating va service'ga ulang:

- `Volume` yarating
- Mount path ni `/app/data` qilib bering

Shunda botdagi `data/bot.db` fayli saqlanib qoladi.

Xohlasangiz `DATABASE_PATH=/app/data/bot.db` ham ishlatishingiz mumkin.

### 5. Deploy qiling

Railway build tugagach service avtomatik ishga tushadi.

- `Deployments` loglarida `python main.py` ishga tushganini tekshiring
- Bot polling rejimida ishlaydi, shu sabab odatda public domain kerak bo'lmaydi

### 6. Birinchi sozlash

Deploy bo'lgach:

- Telegram'da botga `/start` yuboring
- Admin account bilan `Admin panel` ga kiring
- `Teacher ma'lumotini sozlash` ni to'ldiring
- Kurslarni qo'shing

### Eslatma

- `requirements.txt` Railway tomonidan build vaqtida avtomatik o'qiladi
- `main.py` mavjud bo'lgani uchun Railway ko'pincha start command'ni o'zi ham topadi, lekin `railway.json` bilan uni aniq belgilab qo'ydik
