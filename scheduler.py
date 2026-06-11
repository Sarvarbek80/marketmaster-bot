from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
import database as db
import keyboards as kb
import texts as tx


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    # 30-daqiqa reminder (har 5 daqiqada tekshiradi)
    scheduler.add_job(
        send_30min_reminders,
        "interval",
        minutes=5,
        args=[bot],
        id="reminder_30min"
    )

    # 24-soat reminder (har soat tekshiradi)
    scheduler.add_job(
        send_24h_reminders,
        "interval",
        hours=1,
        args=[bot],
        id="reminder_24h"
    )

    return scheduler


async def send_30min_reminders(bot: Bot):
    """30 daqiqa ichida hech narsa qilmagan foydalanuvchilarga xabar"""
    users = db.get_inactive_users(30)
    for user in users:
        if user.get("status") in ("visited", "interested"):
            try:
                await bot.send_message(
                    user["tg_id"],
                    tx.REMINDER_30MIN,
                    reply_markup=kb.reminder_kb()
                )
                db.update_user_status(user["tg_id"], "reminded_30min")
            except Exception:
                pass


async def send_24h_reminders(bot: Bot):
    """24 soat ichida to'lov qilmagan foydalanuvchilarga xabar"""
    users = db.get_inactive_users(1440)  # 1440 min = 24h
    for user in users:
        if user.get("status") in ("reminded_30min", "selected_tarif"):
            try:
                await bot.send_message(
                    user["tg_id"],
                    tx.REMINDER_24H,
                    reply_markup=kb.reminder_kb()
                )
                db.update_user_status(user["tg_id"], "reminded_24h")
            except Exception:
                pass
