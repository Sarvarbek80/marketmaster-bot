from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Kurs haqida", callback_data="course_info")],
        [InlineKeyboardButton(text="💰 Narxlar", callback_data="prices")],
        [InlineKeyboardButton(text="❓ Savol-javob", callback_data="faq")],
    ])


def course_info_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Narxlarni ko'rish", callback_data="prices")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


def prices_kb(p_standart, p_optimal, p_vip, slots_optimal, slots_vip):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🥉 Standart — {int(p_standart):,} so'm".replace(",", " "),
            callback_data="tarif_standart"
        )],
        [InlineKeyboardButton(
            text=f"🥈 Optimal — {int(p_optimal):,} so'm ⚠️ {slots_optimal} joy".replace(",", " "),
            callback_data="tarif_optimal"
        )],
        [InlineKeyboardButton(
            text=f"👑 VIP — {int(p_vip):,} so'm ⚠️ {slots_vip} joy".replace(",", " "),
            callback_data="tarif_vip"
        )],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


def tarif_detail_kb(tarif):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Shu tarifni tanlash", callback_data=f"select_{tarif}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="prices")],
    ])


def payment_methods_kb(card, click_url, payme_url):
    buttons = []
    if click_url:
        buttons.append([InlineKeyboardButton(text="💳 Click orqali to'lash", url=click_url)])
    if payme_url:
        buttons.append([InlineKeyboardButton(text="💳 Payme orqali to'lash", url=payme_url)])
    if card:
        buttons.append([InlineKeyboardButton(text=f"🏦 Karta raqami: {card}", callback_data="show_card")])
    buttons.append([InlineKeyboardButton(text="✅ To'lovni amalga oshirdim", callback_data="payment_done")])
    buttons.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


def faq_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Narxlarni ko'rish", callback_data="prices")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


def upsell_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Ha, VIP ga o'tmoqchiman!", callback_data="upsell_yes")],
        [InlineKeyboardButton(text="❌ Yo'q, rahmat", callback_data="upsell_no")],
    ])


def reminder_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Narxlarni ko'rish", callback_data="prices")],
        [InlineKeyboardButton(text="❓ Savol-javob", callback_data="faq")],
    ])


# ── Admin keyboards ────────────────────────────────────────
def admin_order_kb(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}"),
        ]
    ])


def admin_orders_filter_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Bugun", callback_data="orders_today"),
            InlineKeyboardButton(text="📆 Hafta", callback_data="orders_week"),
            InlineKeyboardButton(text="🗓 Oy", callback_data="orders_month"),
        ],
        [InlineKeyboardButton(text="📋 Hammasi", callback_data="orders_all")],
        [InlineKeyboardButton(text="📊 Excel eksport", callback_data="orders_excel")],
    ])


def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📦 Zakazlar", callback_data="adm_orders")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_users")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="adm_settings")],
    ])


def admin_settings_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Narxlar", callback_data="adm_set_prices")],
        [InlineKeyboardButton(text="🔢 Joylar soni", callback_data="adm_set_slots")],
        [InlineKeyboardButton(text="📅 Cohort sanasi", callback_data="adm_set_date")],
        [InlineKeyboardButton(text="🏦 Karta raqami", callback_data="adm_set_card")],
        [InlineKeyboardButton(text="🔗 Guruh linklari", callback_data="adm_set_groups")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_back")],
    ])
