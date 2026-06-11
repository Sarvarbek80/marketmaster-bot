from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
import texts as tx
from config import ADMIN_ID

router = Router()


class PaymentState(StatesGroup):
    waiting_check = State()


def fmt_price(p):
    return f"{int(p):,}".replace(",", " ")


# ── /start ─────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    db.upsert_user(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    db.log_event("start", msg.from_user.id)
    db.update_user_status(msg.from_user.id, "visited")
    await msg.answer(
        tx.WELCOME.format(name=msg.from_user.first_name),
        reply_markup=kb.main_menu_kb()
    )


# ── Main menu ──────────────────────────────────────────────
@router.callback_query(F.data == "main_menu")
async def main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        tx.WELCOME.format(name=call.from_user.first_name),
        reply_markup=kb.main_menu_kb()
    )


# ── Course info ────────────────────────────────────────────
@router.callback_query(F.data == "course_info")
async def course_info(call: CallbackQuery):
    db.update_user_status(call.from_user.id, "interested")
    await call.message.edit_text(tx.COURSE_INFO, reply_markup=kb.course_info_kb(), parse_mode="HTML")


# ── Prices ─────────────────────────────────────────────────
@router.callback_query(F.data == "prices")
async def show_prices(call: CallbackQuery):
    db.update_user_status(call.from_user.id, "interested")
    p_s = db.get_setting("price_standart")
    p_o = db.get_setting("price_optimal")
    p_v = db.get_setting("price_vip")
    s_o = db.get_setting("slots_optimal")
    s_v = db.get_setting("slots_vip")

    text = (
        "💰 <b>TARIFLAR</b>\n\n"
        f"🥉 Standart — <b>{fmt_price(p_s)} so'm</b>\n"
        f"🥈 Optimal — <b>{fmt_price(p_o)} so'm</b> (⚠️ {s_o} joy)\n"
        f"👑 VIP — <b>{fmt_price(p_v)} so'm</b> (⚠️ {s_v} joy)\n\n"
        "Batafsil ma'lumot uchun tarifni tanlang 👇"
    )
    await call.message.edit_text(
        text,
        reply_markup=kb.prices_kb(p_s, p_o, p_v, s_o, s_v),
        parse_mode="HTML"
    )


# ── Tarif detail ───────────────────────────────────────────
@router.callback_query(F.data.startswith("tarif_"))
async def tarif_detail(call: CallbackQuery):
    tarif = call.data.replace("tarif_", "")
    date = db.get_setting("cohort_date")

    if tarif == "standart":
        price = fmt_price(db.get_setting("price_standart"))
        text = tx.TARIF_STANDART.format(price=price, date=date)
    elif tarif == "optimal":
        price = fmt_price(db.get_setting("price_optimal"))
        slots = db.get_setting("slots_optimal")
        text = tx.TARIF_OPTIMAL.format(price=price, slots=slots, date=date)
    else:
        price = fmt_price(db.get_setting("price_vip"))
        slots = db.get_setting("slots_vip")
        text = tx.TARIF_VIP.format(price=price, slots=slots, date=date)

    await call.message.edit_text(text, reply_markup=kb.tarif_detail_kb(tarif), parse_mode="HTML")


# ── Select tarif ───────────────────────────────────────────
@router.callback_query(F.data.startswith("select_"))
async def select_tarif(call: CallbackQuery):
    tarif = call.data.replace("select_", "")
    db.update_user_tarif(call.from_user.id, tarif)
    db.update_user_status(call.from_user.id, "selected_tarif")
    db.create_order(call.from_user.id, tarif)
    db.log_event("tarif_selected", call.from_user.id, tarif)

    tarif_names = {"standart": "Standart", "optimal": "Optimal", "vip": "VIP"}
    prices = {
        "standart": db.get_setting("price_standart"),
        "optimal": db.get_setting("price_optimal"),
        "vip": db.get_setting("price_vip"),
    }
    card = db.get_setting("card_number")
    click_url = db.get_setting("click_url")
    payme_url = db.get_setting("payme_url")

    methods = ""
    if card:
        methods += f"🏦 Karta: <code>{card}</code>\n"
    if click_url:
        methods += f"💳 Click: {click_url}\n"
    if payme_url:
        methods += f"💳 Payme: {payme_url}\n"
    if not methods:
        methods = "ℹ️ To'lov ma'lumotlari tez orada qo'shiladi."

    text = tx.PAYMENT_INFO.format(
        tarif=tarif_names.get(tarif, tarif),
        price=fmt_price(prices[tarif]),
        methods=methods
    )
    await call.message.edit_text(
        text,
        reply_markup=kb.payment_methods_kb(card, click_url, payme_url),
        parse_mode="HTML"
    )


# ── Show card ──────────────────────────────────────────────
@router.callback_query(F.data == "show_card")
async def show_card(call: CallbackQuery):
    card = db.get_setting("card_number")
    user = db.get_user(call.from_user.id)
    tarif = user.get("selected_tarif", "standart") if user else "standart"
    prices = {
        "standart": db.get_setting("price_standart"),
        "optimal": db.get_setting("price_optimal"),
        "vip": db.get_setting("price_vip"),
    }
    await call.answer(f"Karta: {card}", show_alert=True)


# ── Payment done ───────────────────────────────────────────
@router.callback_query(F.data == "payment_done")
async def payment_done(call: CallbackQuery, state: FSMContext):
    await state.set_state(PaymentState.waiting_check)
    await call.message.edit_text(tx.SEND_CHECK, reply_markup=kb.back_to_menu_kb())


# ── Receive check ──────────────────────────────────────────
@router.message(PaymentState.waiting_check, F.photo)
async def receive_check(msg: Message, state: FSMContext, bot):
    file_id = msg.photo[-1].file_id
    db.update_order_check(msg.from_user.id, file_id)
    db.update_user_status(msg.from_user.id, "check_sent")
    await state.clear()

    # Find the order for this user
    user = db.get_user(msg.from_user.id)
    tarif = user.get("selected_tarif", "—") if user else "—"
    tarif_names = {"standart": "Standart", "optimal": "Optimal", "vip": "VIP"}

    # Get order id
    import database as database_module
    conn = database_module.get_conn()
    order = conn.execute(
        "SELECT id FROM orders WHERE tg_id=? AND status='check_sent' ORDER BY id DESC LIMIT 1",
        (msg.from_user.id,)
    ).fetchone()
    conn.close()
    order_id = order["id"] if order else 0

    username = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name

    admin_text = (
        f"🔔 <b>YANGI TO'LOV!</b>\n\n"
        f"👤 Ism: {msg.from_user.full_name}\n"
        f"📱 Username: {username}\n"
        f"💰 Tarif: {tarif_names.get(tarif, tarif)}\n"
        f"🕒 Sana: {msg.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"🆔 Zakaz ID: #{order_id}"
    )

    await bot.send_photo(
        ADMIN_ID,
        photo=file_id,
        caption=admin_text,
        reply_markup=kb.admin_order_kb(order_id),
        parse_mode="HTML"
    )

    await msg.answer(tx.CHECK_RECEIVED)


@router.message(PaymentState.waiting_check)
async def check_not_photo(msg: Message):
    await msg.answer("📸 Iltimos, rasm (screenshot) ko'rinishida yuboring.")


# ── FAQ ────────────────────────────────────────────────────
@router.callback_query(F.data == "faq")
async def faq(call: CallbackQuery):
    await call.message.edit_text(tx.FAQ_TEXT, reply_markup=kb.faq_kb(), parse_mode="HTML")


# ── Upsell ─────────────────────────────────────────────────
@router.callback_query(F.data == "upsell_yes")
async def upsell_yes(call: CallbackQuery):
    await call.message.edit_text(tx.UPSELL_YES, reply_markup=kb.back_to_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "upsell_no")
async def upsell_no(call: CallbackQuery):
    await call.message.edit_text(tx.UPSELL_NO, reply_markup=kb.back_to_menu_kb())
