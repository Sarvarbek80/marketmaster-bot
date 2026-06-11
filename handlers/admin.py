from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import io

import database as db
import keyboards as kb
from config import ADMIN_ID

router = Router()


def is_admin(tg_id):
    return tg_id == ADMIN_ID


class AdminState(StatesGroup):
    broadcast_text = State()
    set_price_standart = State()
    set_price_optimal = State()
    set_price_vip = State()
    set_slots_optimal = State()
    set_slots_vip = State()
    set_date = State()
    set_card = State()
    set_group_standart = State()
    set_group_optimal = State()
    set_group_vip = State()


# ── /admin ─────────────────────────────────────────────────
@router.message(Command("admin"))
async def admin_panel(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    await msg.answer("⚙️ <b>Admin panel</b>", reply_markup=kb.admin_main_kb(), parse_mode="HTML")


@router.callback_query(F.data == "adm_back")
async def adm_back(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.clear()
    await call.message.edit_text("⚙️ <b>Admin panel</b>", reply_markup=kb.admin_main_kb(), parse_mode="HTML")


# ── Stats ──────────────────────────────────────────────────
@router.message(Command("stats"))
@router.callback_query(F.data == "adm_stats")
async def stats(update, state: FSMContext = None):
    msg = update if isinstance(update, Message) else update.message
    if not is_admin(msg.chat.id if isinstance(update, Message) else update.from_user.id):
        return
    s = db.get_stats()
    text = (
        "📊 <b>STATISTIKA</b>\n\n"
        f"🚀 Bugungi startlar: <b>{s['today_starts']}</b>\n"
        f"👥 Jami foydalanuvchilar: <b>{s['total_users']}</b>\n"
        f"💡 Leadlar: <b>{s['total_leads']}</b>\n"
        f"💳 To'lovlar: <b>{s['total_payments']}</b>\n"
        f"🎓 O'quvchilar: <b>{s['total_students']}</b>\n"
        f"📈 Konversiya: <b>{s['conversion']}%</b>\n"
        f"🏆 Eng mashhur tarif: <b>{s['popular_tarif']}</b>"
    )
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, parse_mode="HTML", reply_markup=kb.admin_main_kb())
    else:
        await msg.answer(text, parse_mode="HTML")


# ── Orders ─────────────────────────────────────────────────
@router.message(Command("orders"))
@router.callback_query(F.data == "adm_orders")
async def orders_menu(update, state: FSMContext = None):
    msg = update if isinstance(update, Message) else update.message
    if not is_admin(msg.chat.id if isinstance(update, Message) else update.from_user.id):
        return
    text = "📦 <b>ZAKAZLAR</b>\nFiltrni tanlang:"
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, parse_mode="HTML", reply_markup=kb.admin_orders_filter_kb())
    else:
        await msg.answer(text, parse_mode="HTML", reply_markup=kb.admin_orders_filter_kb())


@router.callback_query(F.data.startswith("orders_"))
async def orders_filtered(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    period = call.data.replace("orders_", "")

    if period == "excel":
        await export_excel(call)
        return

    orders = db.get_orders_filtered(period)
    if not orders:
        await call.answer("Hech qanday zakaz topilmadi.", show_alert=True)
        return

    status_map = {"pending": "⏳", "check_sent": "📤", "approved": "✅", "rejected": "❌"}
    tarif_map = {"standart": "🥉 Standart", "optimal": "🥈 Optimal", "vip": "👑 VIP"}

    lines = [f"📦 <b>ZAKAZLAR</b> ({period})\n"]
    for o in orders[:20]:
        st = status_map.get(o["status"], "❓")
        tr = tarif_map.get(o["tarif"], o["tarif"])
        uname = f"@{o['username']}" if o.get("username") else o.get("full_name", "—")
        lines.append(f"{st} #{o['id']} | {tr} | {uname} | {o['created_at'][:10]}")

    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=kb.admin_orders_filter_kb())


async def export_excel(call: CallbackQuery):
    import openpyxl
    orders = db.get_orders_filtered("all")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Zakazlar"
    ws.append(["ID", "TG_ID", "Username", "To'liq ism", "Tarif", "Status", "Sana"])
    for o in orders:
        ws.append([
            o["id"], o["tg_id"],
            o.get("username", ""), o.get("full_name", ""),
            o["tarif"], o["status"], o["created_at"]
        ])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    await call.message.answer_document(
        BufferedInputFile(buf.read(), filename="zakazlar.xlsx"),
        caption="📊 Zakazlar Excel fayli"
    )


# ── Approve / Reject ───────────────────────────────────────
@router.callback_query(F.data.startswith("approve_"))
async def approve_order(call: CallbackQuery, bot):
    if not is_admin(call.from_user.id):
        return
    order_id = int(call.data.replace("approve_", ""))
    order = db.get_order_by_id(order_id)
    if not order:
        await call.answer("Zakaz topilmadi!", show_alert=True)
        return

    db.approve_order(order_id)
    db.update_user_status(order["tg_id"], "student")

    tarif = order["tarif"]
    group_link = db.get_setting(f"group_{tarif}")

    if group_link:
        await bot.send_message(
            order["tg_id"],
            tx_approved(group_link),
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            order["tg_id"],
            "🎉 To'lovingiz tasdiqlandi! Guruh linki tez orada yuboriladi.",
        )

    await call.message.edit_caption(
        call.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode="HTML"
    )
    await call.answer("✅ Tasdiqlandi!")

    # Upsell for optimal
    if tarif == "optimal":
        import asyncio
        asyncio.create_task(_send_upsell_later(bot, order["tg_id"]))


async def _send_upsell_later(bot, tg_id):
    import asyncio
    from texts import UPSELL_MSG
    import keyboards as kb
    await asyncio.sleep(3600)
    user = db.get_user(tg_id)
    if user and user.get("status") == "student":
        try:
            await bot.send_message(tg_id, UPSELL_MSG, reply_markup=kb.upsell_kb(), parse_mode="HTML")
        except Exception:
            pass


def tx_approved(group_link):
    from texts import PAYMENT_APPROVED
    return PAYMENT_APPROVED + f"\n{group_link}"


@router.callback_query(F.data.startswith("reject_"))
async def reject_order(call: CallbackQuery, bot):
    if not is_admin(call.from_user.id):
        return
    order_id = int(call.data.replace("reject_", ""))
    order = db.get_order_by_id(order_id)
    if not order:
        await call.answer("Zakaz topilmadi!", show_alert=True)
        return

    db.reject_order(order_id)
    from texts import PAYMENT_REJECTED
    await bot.send_message(order["tg_id"], PAYMENT_REJECTED)
    await call.message.edit_caption(
        call.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await call.answer("❌ Rad etildi!")


# ── Users ──────────────────────────────────────────────────
@router.message(Command("users"))
@router.callback_query(F.data == "adm_users")
async def users_list(update, state: FSMContext = None):
    msg = update if isinstance(update, Message) else update.message
    if not is_admin(msg.chat.id if isinstance(update, Message) else update.from_user.id):
        return

    all_users = db.get_all_users()
    students = [u for u in all_users if u["status"] == "student"]
    interested = [u for u in all_users if u["status"] in ("interested", "selected_tarif", "check_sent")]

    text = (
        f"👥 <b>FOYDALANUVCHILAR</b>\n\n"
        f"📊 Jami: <b>{len(all_users)}</b>\n"
        f"💡 Qiziqdi: <b>{len(interested)}</b>\n"
        f"🎓 O'quvchilar: <b>{len(students)}</b>\n\n"
        f"<b>Oxirgi 10 ta foydalanuvchi:</b>\n"
    )
    for u in all_users[-10:]:
        uname = f"@{u['username']}" if u.get("username") else u.get("full_name", "—")
        text += f"• {uname} | {u['status']} | {u.get('last_active', '')[:10]}\n"

    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, parse_mode="HTML", reply_markup=kb.admin_main_kb())
    else:
        await msg.answer(text, parse_mode="HTML")


# ── Broadcast ──────────────────────────────────────────────
@router.message(Command("broadcast"))
async def broadcast_cmd(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.set_state(AdminState.broadcast_text)
    await msg.answer(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
        "(Bekor qilish: /cancel)"
    )


@router.message(Command("broadcast_leads"))
async def broadcast_leads_cmd(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.set_state(AdminState.broadcast_text)
    await state.update_data(broadcast_target="leads")
    await msg.answer("📢 Leadlarga yuboriladigan xabarni yozing:\n\n(Bekor qilish: /cancel)")


@router.message(Command("broadcast_students"))
async def broadcast_students_cmd(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.set_state(AdminState.broadcast_text)
    await state.update_data(broadcast_target="students")
    await msg.answer("📢 O'quvchilarga yuboriladigan xabarni yozing:\n\n(Bekor qilish: /cancel)")


@router.message(AdminState.broadcast_text)
async def do_broadcast(msg: Message, state: FSMContext, bot):
    data = await state.get_data()
    target = data.get("broadcast_target", "all")
    await state.clear()

    if target == "leads":
        users = db.get_users_by_status("interested") + db.get_users_by_status("selected_tarif")
    elif target == "students":
        users = db.get_users_by_status("student")
    else:
        users = db.get_all_users()

    sent = 0
    failed = 0
    for u in users:
        try:
            await bot.send_message(u["tg_id"], msg.text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

    await msg.answer(f"✅ Broadcast yakunlandi!\n\n📤 Yuborildi: {sent}\n❌ Xato: {failed}")


# ── Settings ───────────────────────────────────────────────
@router.message(Command("settings"))
@router.callback_query(F.data == "adm_settings")
async def settings_menu(update, state: FSMContext = None):
    msg = update if isinstance(update, Message) else update.message
    if not is_admin(msg.chat.id if isinstance(update, Message) else update.from_user.id):
        return

    p_s = db.get_setting("price_standart")
    p_o = db.get_setting("price_optimal")
    p_v = db.get_setting("price_vip")
    s_o = db.get_setting("slots_optimal")
    s_v = db.get_setting("slots_vip")
    date = db.get_setting("cohort_date")
    card = db.get_setting("card_number") or "—"
    g_s = db.get_setting("group_standart") or "—"
    g_o = db.get_setting("group_optimal") or "—"
    g_v = db.get_setting("group_vip") or "—"

    text = (
        "⚙️ <b>SOZLAMALAR</b>\n\n"
        f"💰 Narxlar:\n  🥉 Standart: {int(p_s):,} so'm\n  🥈 Optimal: {int(p_o):,} so'm\n  👑 VIP: {int(p_v):,} so'm\n\n"
        f"🔢 Joylar: Optimal={s_o}, VIP={s_v}\n"
        f"📅 Cohort: {date}\n"
        f"🏦 Karta: {card}\n\n"
        f"🔗 Guruhlar:\n  🥉 {g_s}\n  🥈 {g_o}\n  👑 {g_v}"
    ).replace(",", " ")

    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, parse_mode="HTML", reply_markup=kb.admin_settings_kb())
    else:
        await msg.answer(text, parse_mode="HTML", reply_markup=kb.admin_settings_kb())


# Settings callbacks
@router.callback_query(F.data == "adm_set_prices")
async def set_prices_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.set_price_standart)
    await call.message.edit_text(
        "💰 Standart tarif narxini kiriting (so'mda):\nMasalan: 299000",
        reply_markup=kb.back_to_menu_kb()
    )


@router.message(AdminState.set_price_standart)
async def set_price_standart(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        val = int(msg.text.strip().replace(" ", ""))
        db.set_setting("price_standart", str(val))
        await state.set_state(AdminState.set_price_optimal)
        await msg.answer(f"✅ Standart: {val:,} so'm\n\n💰 Optimal narxini kiriting:".replace(",", " "))
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting. Qayta urinib ko'ring:")


@router.message(AdminState.set_price_optimal)
async def set_price_optimal(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        val = int(msg.text.strip().replace(" ", ""))
        db.set_setting("price_optimal", str(val))
        await state.set_state(AdminState.set_price_vip)
        await msg.answer(f"✅ Optimal: {val:,} so'm\n\n💰 VIP narxini kiriting:".replace(",", " "))
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting:")


@router.message(AdminState.set_price_vip)
async def set_price_vip(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        val = int(msg.text.strip().replace(" ", ""))
        db.set_setting("price_vip", str(val))
        await state.clear()
        await msg.answer(
            f"✅ Barcha narxlar yangilandi!\n\n"
            f"🥉 Standart: {int(db.get_setting('price_standart')):,} so'm\n"
            f"🥈 Optimal: {int(db.get_setting('price_optimal')):,} so'm\n"
            f"👑 VIP: {val:,} so'm".replace(",", " "),
            reply_markup=kb.admin_settings_kb()
        )
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting:")


@router.callback_query(F.data == "adm_set_slots")
async def set_slots_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.set_slots_optimal)
    await call.message.edit_text(
        "🔢 Optimal tarifda nechta joy? (raqam kiriting):",
        reply_markup=kb.back_to_menu_kb()
    )


@router.message(AdminState.set_slots_optimal)
async def set_slots_optimal(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        val = int(msg.text.strip())
        db.set_setting("slots_optimal", str(val))
        await state.set_state(AdminState.set_slots_vip)
        await msg.answer(f"✅ Optimal joylar: {val}\n\n🔢 VIP tarifda nechta joy?")
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting:")


@router.message(AdminState.set_slots_vip)
async def set_slots_vip(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        val = int(msg.text.strip())
        db.set_setting("slots_vip", str(val))
        await state.clear()
        await msg.answer(
            f"✅ Joylar yangilandi!\n\n"
            f"🥈 Optimal: {db.get_setting('slots_optimal')} joy\n"
            f"👑 VIP: {val} joy",
            reply_markup=kb.admin_settings_kb()
        )
    except ValueError:
        await msg.answer("❌ Faqat raqam kiriting:")


@router.callback_query(F.data == "adm_set_date")
async def set_date_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.set_date)
    await call.message.edit_text(
        "📅 Cohort sanasini kiriting:\nMasalan: 15-iyul 2025 yoki 2025-07-15",
        reply_markup=kb.back_to_menu_kb()
    )


@router.message(AdminState.set_date)
async def set_date(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    db.set_setting("cohort_date", msg.text.strip())
    await state.clear()
    await msg.answer(f"✅ Cohort sanasi: {msg.text.strip()}", reply_markup=kb.admin_settings_kb())


@router.callback_query(F.data == "adm_set_card")
async def set_card_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.set_card)
    await call.message.edit_text(
        "🏦 Karta raqamini kiriting:\nMasalan: 8600 1234 5678 9012",
        reply_markup=kb.back_to_menu_kb()
    )


@router.message(AdminState.set_card)
async def set_card(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    db.set_setting("card_number", msg.text.strip())
    await state.clear()
    await msg.answer(f"✅ Karta raqami saqlandi: {msg.text.strip()}", reply_markup=kb.admin_settings_kb())


@router.callback_query(F.data == "adm_set_groups")
async def set_groups_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.set_group_standart)
    await call.message.edit_text(
        "🔗 Standart tarif guruh linkini kiriting:\nMasalan: https://t.me/+xxxxxxxxxxxx",
        reply_markup=kb.back_to_menu_kb()
    )


@router.message(AdminState.set_group_standart)
async def set_group_standart(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    db.set_setting("group_standart", msg.text.strip())
    await state.set_state(AdminState.set_group_optimal)
    await msg.answer("✅ Standart guruh saqlandi!\n\n🔗 Optimal tarif guruh linkini kiriting:")


@router.message(AdminState.set_group_optimal)
async def set_group_optimal(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    db.set_setting("group_optimal", msg.text.strip())
    await state.set_state(AdminState.set_group_vip)
    await msg.answer("✅ Optimal guruh saqlandi!\n\n🔗 VIP tarif guruh linkini kiriting:")


@router.message(AdminState.set_group_vip)
async def set_group_vip(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    db.set_setting("group_vip", msg.text.strip())
    await state.clear()
    await msg.answer(
        "✅ Barcha guruh linklarni saqlandi!\n\n"
        f"🥉 Standart: {db.get_setting('group_standart')}\n"
        f"🥈 Optimal: {db.get_setting('group_optimal')}\n"
        f"👑 VIP: {db.get_setting('group_vip')}",
        reply_markup=kb.admin_settings_kb()
    )


# ── /cancel ────────────────────────────────────────────────
@router.message(Command("cancel"))
async def cancel_cmd(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=kb.admin_main_kb())


# ── /report ────────────────────────────────────────────────
@router.message(Command("report"))
async def monthly_report(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    s = db.get_stats()
    orders = db.get_orders_filtered("month")
    approved = [o for o in orders if o["status"] == "approved"]
    total_income = sum(
        int(db.get_setting(f"price_{o['tarif']}") or 0)
        for o in approved
    )
    text = (
        "📋 <b>OYLIK HISOBOT</b>\n\n"
        f"👥 Jami foydalanuvchilar: {s['total_users']}\n"
        f"💡 Leadlar: {s['total_leads']}\n"
        f"💳 Tasdiqlangan to'lovlar: {len(approved)}\n"
        f"💰 Taxminiy daromad: {total_income:,} so'm\n"
        f"📈 Konversiya: {s['conversion']}%\n"
        f"🏆 Mashhur tarif: {s['popular_tarif']}"
    ).replace(",", " ")
    await msg.answer(text, parse_mode="HTML")
