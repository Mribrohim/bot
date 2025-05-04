import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

# Logging
logging.basicConfig(level=logging.INFO)

# TOKEN va adminlar
API_TOKEN = "7888564984:AAF7PK6_BUK-vJj4M5NDSyK21lBQM09A8OE"
ADMINS = [5726395446, 7551604665]  # admin ID-lar

# Bot va dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Xabar bog‘lovchi lug‘atlar
user_to_admin = {}
admin_to_user = {}


@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("👋 Salom! Bot ishga tushdi.")


@dp.message()
async def handle_user_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Javob yozish", callback_data=f"reply_{user_id}")]
        ]
    )

    # Adminlarga yuborish
    for admin_id in ADMINS:
        await bot.send_message(
            admin_id,
            f"📨 <b>Yangi xabar:</b>\n\n<b>Foydalanuvchi ID:</b> <code>{user_id}</code>\n<b>Xabar:</b> {text}",
            reply_markup=keyboard
        )
        user_to_admin[user_id] = admin_id

    await message.answer("✅ Xabaringiz adminlarga yuborildi.")


@dp.callback_query(F.data.startswith("reply_"))
async def reply_callback(callback: CallbackQuery):
    admin_id = callback.from_user.id
    user_id = int(callback.data.split("_")[1])

    admin_to_user[admin_id] = user_id
    await callback.message.answer("✍️ Endi foydalanuvchiga xabar yozing.")
    await callback.answer()


@dp.message(F.from_user.id.in_(ADMINS))
async def handle_admin_reply(message: Message):
    admin_id = message.from_user.id

    if admin_id in admin_to_user:
        user_id = admin_to_user[admin_id]
        text = f"💬 Admin javobi:\n{message.text}"
        await bot.send_message(user_id, text)

        # Boshqa adminlarga xabar
        for other_admin in ADMINS:
            if other_admin != admin_id:
                await bot.send_message(other_admin, f"👀 Boshqa admin javobi:\n\n{text}")

        del admin_to_user[admin_id]
    else:
        await message.reply("⚠️ Avval 'Javob yozish' tugmasini bosing.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())