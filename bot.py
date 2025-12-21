import asyncio
import yt_dlp

from pyrogram import Client, filters
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio

# ===== CONFIG =====
API_ID = 123456
API_HASH = "API_HASH_HERE"
BOT_TOKEN = "BOT_TOKEN_HERE"
SESSION_STRING = "SESSION_STRING_HERE"
# ==================

bot = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

user = Client(
    "musicuser",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

call = PyTgCalls(user)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

def download_audio(query: str):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        return ydl.prepare_filename(info)

@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("song name ya link do")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔎 download ho raha hai...")

    file = download_audio(query)

    await call.join_group_call(
        message.chat.id,
        AudioPiped(file, HighQualityAudio()),
    )

    await msg.edit("▶️ music play ho raha hai")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    await call.leave_group_call(message.chat.id)
    await message.reply("⏹ music stop kar diya")

async def main():
    await bot.start()
    await user.start()
    await call.start()
    print("✅ Music bot started")
    await asyncio.Event().wait()

asyncio.run(main())

