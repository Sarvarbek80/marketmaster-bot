import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncpg

load_dotenv()

# ════════════════════════════════════════
#   SOZLAMALAR
# ════════════════════════════════════════
BOT_TOKEN   = os.getenv("BOT_TOKEN")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID  = int(os.getenv("CHANNEL_ID", "0"))
GROUP_LINK  = os.getenv("GROUP_LINK", "")
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")
CARD_OWNER  = os.getenv("CARD_OWNER", "Ism Familiya")

KURS_NOMI   = "Uzum Market Kursi"
KURS_NARXI  = 99_000
KURS_TAVSIF = (
    "✅ 0 dan video darslar\n"
    "✅ Umrbod kirish\n"
    "✅ Telegram guruh\n"
    "✅ Kurator yordami"
)
# ════════════════════════════════════════

db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id         SERIAL PRIMARY KEY,
                tg_id      BIGINT,
                username   TEXT,
                full_name  TEXT,
                status     TEXT DEFAULT 'pending',
                file_id    TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

async def new_order(tg_id, username, full_name):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM orders WHERE tg_id=$1 AND status='pending'", tg_id)
        row = await conn.fetchrow(
            "INSERT INTO orders (tg_id, username, full_name) VALUES ($1, $2, $3) RETURNING id",
            tg_id, username, full_name
        )
        return row["id"]

async def save_check(order_id, file_id):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE orders SET file_id=$1, status='check_sent' WHERE id=$2",
            file_id, order_id
        )

async def get_order(order_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM orders WHERE id=$1", order_id)
        return dict(row) if row else None

async def set_status(order_id, status):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE orders SET status=$1 WHERE id=$2", status, order_id)

async def get_stats():
    async with db_pool.acquire() as conn:
        total    = await conn.fetchval("SELECT COUNT(*) FROM orders")
        approved = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE status='approved'")
        pending  = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE status='check_sent'")
        return total, approved, pending


# ─── KEYBOARDS ────────────────────────
def buy_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💳 Sotib olish", callback_data="buy")
    ]])

def paid_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ To'lovni amalga oshirdim", callback_data="paid")
    ]])

def admin_kb(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{order_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"no_{order_id}"),
    ]])

p = f"{KURS_NARXI:,}".replace(",", " ")


# ─── FSM ──────────────────────────────
class S(StatesGroup):
    check = State()


# ─── BOT & DISPATCHER ─────────────────
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp  = Dispatcher(storage=MemoryStorage())


# ─── HANDLERS ─────────────────────────
@dp.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        f"👋 Salom, <b>{msg.from_user.first_name}</b>!\n\n"
        f"📦 <b>{KURS_NOMI}</b>\n"
        f"💰 <b>{p} so'm</b>\n\n"
        f"{KURS_TAVSIF}",
        reply_markup=buy_kb()
    )


@dp.callback_query(F.data == "buy")
async def buy(cq: CallbackQuery, state: FSMContext):
    order_id = await new_order(cq.from_user.id, cq.from_user.username or "", cq.from_user.full_name)
    await state.update_data(order_id=order_id)
    await cq.message.edit_text(
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"Summa: <b>{p} so'm</b>\n\n"
        f"Karta: <code>{CARD_NUMBER}</code>\n"
        f"Egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirgach tugmani bosing 👇",
        reply_markup=paid_kb()
    )


@dp.callback_query(F.data == "paid")
async def paid(cq: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("order_id"):
        return await cq.answer("Avval /start bosing!", show_alert=True)
    await state.set_state(S.check)
    await cq.message.edit_text("📸 To'lov chekini yuboring (skrinshot):")


@dp.message(S.check, F.photo)
async def got_check(msg: Message, state: FSMContext):
    data     = await state.get_data()
    order_id = data["order_id"]
    file_id  = msg.photo[-1].file_id
    await save_check(order_id, file_id)
    await state.clear()

    await msg.answer("✅ Chek qabul qilindi! Tez orada tekshiriladi.")

    caption = (
        f"🆕 <b>Yangi to'lov</b> #{order_id}\n"
        f"👤 {msg.from_user.full_name}"
        + (f" @{msg.from_user.username}" if msg.from_user.username else "") + "\n"
        f"🆔 <code>{msg.from_user.id}</code>\n"
        f"💰 {p} so'm\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    await bot.send_photo(ADMIN_ID, file_id, caption=caption, reply_markup=admin_kb(order_id))

    if CHANNEL_ID:
        await bot.send_photo(CHANNEL_ID, file_id, caption=caption)


@dp.message(S.check)
async def wrong(msg: Message):
    await msg.answer("❗ Rasm (skrinshot) yuboring.")


@dp.callback_query(F.data.startswith("ok_"))
async def approve(cq: CallbackQuery):
    if cq.from_user.id != ADMIN_ID:
        return await cq.answer("Ruxsat yo'q!", show_alert=True)
    order_id = int(cq.data.split("_")[1])
    order = await get_order(order_id)
    if not order or order["status"] == "approved":
        return await cq.answer("Allaqachon tasdiqlangan!", show_alert=True)

    await set_status(order_id, "approved")
    text = "🎉 <b>To'lovingiz tasdiqlandi!</b>\n\n"
    text += f"Guruhga qo'shilish:\n👉 {GROUP_LINK}" if GROUP_LINK else "Tez orada guruh linki yuboriladi."
    await bot.send_message(order["tg_id"], text)
    await cq.message.edit_caption(cq.message.caption + "\n\n✅ TASDIQLANDI")
    await cq.answer("✅")


@dp.callback_query(F.data.startswith("no_"))
async def reject(cq: CallbackQuery):
    if cq.from_user.id != ADMIN_ID:
        return await cq.answer("Ruxsat yo'q!", show_alert=True)
    order_id = int(cq.data.split("_")[1])
    order = await get_order(order_id)
    if not order:
        return await cq.answer("Topilmadi!", show_alert=True)

    await set_status(order_id, "rejected")
    await bot.send_message(order["tg_id"], "❌ To'lov tasdiqlanmadi. Chekni qayta yuboring.")
    await cq.message.edit_caption(cq.message.caption + "\n\n❌ RAD ETILDI")
    await cq.answer("❌")


@dp.message(Command("stats"), F.from_user.id == ADMIN_ID)
async def stats(msg: Message):
    total, approved, pending = await get_stats()
    await msg.answer(
        f"📊 Jami: <b>{total}</b>\n"
        f"✅ Tasdiqlangan: <b>{approved}</b>\n"
        f"⏳ Kutilayotgan: <b>{pending}</b>"
    )


# ─── MAIN ─────────────────────────────
async def main():
    await init_db()
    logging.basicConfig(level=logging.WARNING)
    logging.warning("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
