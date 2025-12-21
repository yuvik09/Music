import asyncio
import yt_dlp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

bot = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

call = PyTgCalls(user)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True,
    "outtmpl": "downloads/%(id)s.%(ext)s"
}

def download(query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        return ydl.prepare_filename(info)

@bot.on_message(filters.command("play") & filters.group)
async def play(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("song name ya link do")

    q = " ".join(msg.command[1:])
    m = await msg.reply("download ho raha hai...")

    file = download(q)

    await call.join_group_call(
        msg.chat.id,
        AudioPiped(file, HighQualityAudio()),
    )

    await m.edit("music play ho raha hai 🎵")

@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, msg):
    await call.leave_group_call(msg.chat.id)
    await msg.reply("music stop kar diya ⏹")

async def main():
    await bot.start()
    await user.start()
    await call.start()
    print("Music bot running...")
    await asyncio.Event().wait()

asyncio.run(main())
