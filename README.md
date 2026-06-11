# 🤖 MarketMaster UZ Bot

Uzum Market kursi uchun to'liq savdo boti.

---

## 📁 Fayl tuzilishi

```
marketmaster_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Konfiguratsiya
├── database.py         # SQLite ma'lumotlar bazasi
├── keyboards.py        # Barcha tugmalar
├── texts.py            # Barcha O'zbek matnlar
├── scheduler.py        # Avtomatik xabarlar
├── handlers/
│   ├── user.py         # Foydalanuvchi handlerlari
│   └── admin.py        # Admin handlerlari
├── requirements.txt
├── railway.json
├── Procfile
└── .env.example
```

---

## ⚙️ O'rnatish

### 1. Bot tokenini oling
- @BotFather ga yozing
- `/newbot` buyrug'ini yuboring
- Nom va username bering
- Tokenni saqlang

### 2. Admin ID ni oling
- @userinfobot ga `/start` yuboring
- `Id:` qatoridagi raqamni saqlang

### 3. .env fayl yarating
```
cp .env.example .env
```
`.env` faylni oching va to'ldiring:
```
BOT_TOKEN=1234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ADMIN_ID=123456789
```

### 4. Lokal ishga tushirish
```bash
pip install -r requirements.txt
python bot.py
```

---

## 🚀 Railway Deploy

### 1. GitHub ga yuklash
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### 2. Railway.app da Deploy
1. [railway.app](https://railway.app) ga kiring
2. **New Project** → **Deploy from GitHub repo**
3. Reponi tanlang
4. **Variables** bo'limiga o'ting:
   - `BOT_TOKEN` = bot tokeningiz
   - `ADMIN_ID` = telegram id raqamingiz
5. **Deploy** tugmasini bosing ✅

---

## 🎛️ Admin Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panelni ochish |
| `/stats` | Statistika ko'rish |
| `/orders` | Zakazlar ro'yxati |
| `/users` | Foydalanuvchilar |
| `/report` | Oylik hisobot |
| `/broadcast` | Barchaga xabar |
| `/broadcast_leads` | Faqat leadlarga |
| `/broadcast_students` | Faqat o'quvchilarga |
| `/settings` | Sozlamalar paneli |
| `/cancel` | Amalni bekor qilish |

---

## ⚙️ Admin Sozlamalari (tugmalar orqali)

### Narxlarni o'zgartirish
`/settings` → **💰 Narxlar** → 3 ta narxni ketma-ket kiriting

### Joylar sonini o'zgartirish
`/settings` → **🔢 Joylar soni** → Optimal va VIP uchun kiriting

### Cohort sanasini belgilash
`/settings` → **📅 Cohort sanasi** → Masalan: `15-iyul 2025`

### Karta raqamini qo'shish
`/settings` → **🏦 Karta raqami** → Masalan: `8600 1234 5678 9012`

### Guruh linkini qo'shish
`/settings` → **🔗 Guruh linklari** → 3 ta link ketma-ket kiriting

---

## 💳 To'lov Jarayoni

```
Foydalanuvchi tarif tanlaydi
       ↓
To'lov ma'lumotlari ko'rsatiladi
       ↓
Foydalanuvchi to'lov qiladi
       ↓
"✅ To'lovni amalga oshirdim" bosadi
       ↓
Chek (rasm) yuboradi
       ↓
Admin bildirgi oladi → Tasdiqlash yoki Rad etish
       ↓
Tasdiqlansa: O'quvchi statusiga o'tadi + guruh linki yuboriladi
```

---

## 🔔 Avtomatik Xabarlar

- **30 daqiqa** ichida javob bermagan foydalanuvchilarga eslatma
- **24 soat** ichida to'lov qilmagan foydalanuvchilarga scarcity xabari
- **Optimal** tarif xaridorlariga **1 soat keyin** VIP upsell taklifi

---

## 📊 Database Jadvallar

- `users` — Barcha foydalanuvchilar va holati
- `orders` — To'lov zakazlari
- `settings` — Bot sozlamalari (narx, joylar, linklar)
- `statistics` — Hodisalar logi

---

## ❓ Muammo bo'lsa

1. `BOT_TOKEN` va `ADMIN_ID` to'g'ri ekanligini tekshiring
2. Railway → Logs bo'limida xato xabarini ko'ring
3. Bot bloklanmagan yoki to'xtatilmaganligini tekshiring
