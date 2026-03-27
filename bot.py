import os
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=['audio', 'voice', 'document'])
async def convert_to_voice(message: types.Message):
    try:
        await message.reply("⏳ Конвертирую...")

        if message.audio:
            file = message.audio
        elif message.voice:
            file = message.voice
        elif message.document:
            file = message.document
        else:
            return

        file_info = await bot.get_file(file.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        input_path = "input.ogg"
        output_path = "output.ogg"

        with open(input_path, "wb") as f:
            f.write(downloaded_file.getvalue())

        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-c:a", "libopus",
            "-ar", "48000",
            "-b:a", "64k",
            "-ac", "1",
            "-f", "ogg",
            output_path
        ], check=True)

        with open(output_path, "rb") as f:
            await message.reply_voice(f)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await message.reply(f"Ошибка: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
