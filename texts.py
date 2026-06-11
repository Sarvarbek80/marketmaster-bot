# Barcha bot matni — O'zbek tilida

WELCOME = """👋 Assalomu alaykum, {name}!

Uzum Market kursiga xush kelibsiz! 🎉

Bu kurs orqali siz:
🎁 Uzum marketda 0 dan ishlash
🎁 Xitoy bozorlari bilan ishlash bonusi 
🎁 Kurator yordami
🎁 Jonli efirlar 

Quyidagilardan birini tanlang 👇"""

COURSE_INFO = """📚 <b>UZUM MARKET KURSI</b>

Kurs 5 ta moduldan iborat — har bir modulda amaliy darslar va bonuslar mavjud!

<b>📌 Modul 1 — Boshlash</b>
• YATT ochish
• Ro'yxatdan o'tish
• Kabinet sozlash

<b>📌 Modul 2 — Tovar</b>
• Tovar kartochkasi yaratish
• SKU va kategoriya
• Unit ekonomika hisoblash

<b>📌 Modul 3 — Dizayn</b>
• Canva bilan ishlash
• AI infografika yaratish

<b>📌 Modul 4 — Logistika</b>
• FBO sxemasi
• Qadoqlash va yetkazish
• Qaytarish boshqaruvi

<b>📌 Modul 5 — Savdo</b>
• Reklama qo'yish
• FBS va DBS
• Uzum Bot ishlatish

🎁 <b>BONUS: Xitoy kursi</b>
• 1688 dan mahsulot topish
• Pinduoduo ishlash

<b>Format:</b> Online • Video darslar • Umrbod kirish
<b>Qo'shimcha:</b> Kurator + Jonli efir + Mentorlik"""

FAQ_TEXT = """❓ <b>KO'P SO'RALADIGAN SAVOLLAR</b>

<b>🌍 Viloyatdan bo'lsa bo'ladimi?</b>
Ha, kurs to'liq online — O'zbekistonning istalgan joyidan!

<b>⏰ Darslar qancha vaqt ochiq bo'ladi?</b>
Umrbod kirish huquqi beriladi.

<b>💳 Bo'lib to'lash bormi?</b>
afsuski hozirda mavjud emas.

<b>🏆 Natija kafolati bormi?</b>
Amaliyot qilinsa natija bo'ladi. O'quvchilarimiz oyiga 3-10 mln so'm daromad olmoqda.

<b>🚀 Kurs qachon boshlanadi?</b>
guruhga qo'shilishingiz bilan. Ro'yxatdan o'ting — xabar beramiz!"""

TARIF_STANDART = """🥉 <b>STANDART TARIF</b>
💰 <b>{price} so'm</b>

✅ 0 dan video darslar
✅ Umrbod kirish
✅ Telegram guruh

⏰ Narx {date} dan oshishi mumkin!

Bu tarif Uzum Marketni o'rganib, mustaqil boshlashni xohlaganlar uchun."""

TARIF_OPTIMAL = """🥈 <b>OPTIMAL TARIF</b>
💰 <b>{price} so'm</b>

✅ 0 dan video dars
✅ Xitoy bozorlari bilan ishlash bonusi
✅ Umrbod kirish
✅ Telegram guruh
✅ Kurator yordami (30 kun)
✅ Jonli efirlar

⚠️ Atigi <b>{slots} ta joy</b> qoldi!
⏰ Narx {date} dan oshishi mumkin!

Bu tarif tez natija olishni va savol-javob bo'lishini xohlaganlar uchun."""

TARIF_VIP = """👑 <b>VIP TARIF</b>
💰 <b>{price} so'm</b>

✅ 0 dan video darslar
✅ Xitoy bozorlari bilan ishlash bonusi
✅ Umrbod kirish
✅ Telegram guruh
✅ Kurator yordami (90 kun)
✅ Jonli efirlar
✅ Shaxsiy mentorlik (2 marta)
✅ Do'kon auditi
✅ Konsultatsiya

⚠️ Atigi <b>{slots} ta joy</b> qoldi!
⏰ Narx {date} dan oshishi mumkin!

Bu tarif eng tez va kafolatlangan natija olishni xohlaganlar uchun."""

PAYMENT_INFO = """💳 <b>TO'LOV AMALGA OSHIRISH</b>

Tarif: <b>{tarif}</b>
Summa: <b>{price} so'm</b>

To'lov usullari:
{methods}

To'lovni amalga oshirgach, <b>"✅ To'lovni amalga oshirdim"</b> tugmasini bosing."""

SEND_CHECK = """📸 Iltimos, to'lov chekini yuboring.

(Skrinshot yoki rasm shaklida)"""

CHECK_RECEIVED = """✅ Chekingiz qabul qilindi!

⏳ 30 daqiqa ichida tekshiriladi va sizga guruh linki yuboriladi.

Savolingiz bo'lsa: @marketmaster_uzb"""

PAYMENT_APPROVED = """🎉 <b>Tabriklaymiz!</b>

To'lovingiz tasdiqlandi! Siz endi rasmiy o'quvchisiz! 🚀

Quyidagi havoladan guruhga qo'shiling:
👇"""

PAYMENT_REJECTED = """❌ Afsuski, to'lov tasdiqlanmadi.

Iltimos, chekni qayta yuboring yoki qo'llab-quvvatlash bilan bog'laning."""

REMINDER_30MIN = """💬 Savolingiz bormi? 😊

Istalgan savolga javob berishga tayyorman!
Narxlar yoki kurs haqida ko'proq bilmoqchimisiz?"""

REMINDER_24H = """⚠️ Joylar tez tugamoqda!

Siz hali kursga yozilmagansiz. Joyni band qilib qo'yaylikmi?

Hozir ro'yxatdan o'tgan o'quvchilar allaqachon dars boshlashga tayyorlanmoqda! 🚀"""

UPSELL_MSG = """🎉 Tabriklaymiz, siz Optimal tarifni oldingiz!

💡 Lekin... VIP tarifga o'tib, <b>shaxsiy mentorlik</b> va <b>do'kon auditi</b> ham olishni xohlaysizmi?

👑 <b>VIP ga o'tish uchun qo'shimcha: 550 000 so'm</b>

✅ Shaxsiy mentorlik (2 marta)
✅ Do'kon auditi
✅ Konsultatsiya

Bu imkoniyat faqat yangi o'quvchilar uchun! ⏰"""

UPSELL_YES = """🔥 Zo'r! VIP ga o'tish uchun quyidagicha to'lov qiling:

Qo'shimcha summa: <b>550 000 so'm</b>

To'lovni amalga oshirib, chekni yuboring. Admin tekshiradi va VIP guruhga qo'shadi!"""

UPSELL_NO = """✅ Tushunarli! Optimal tarifdan mamnun bo'lishingizni tilaymiz! 🎓

Savolingiz bo'lsa doim yozib qolinavering."""

CARD_TEXT = """🏦 Karta raqami: 123413412515143132

<code>{card}</code>

Yuqoridagi raqamga {price} so'm o'tkazing va chekni yuboring."""
