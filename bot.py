import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types import StreamType
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

API_ID = "36549849"
API_HASH = "ad1fc69799c0dcda94eec0d444e399ed"
BOT_TOKEN = "8055723339:AAEV59ZFb0zL_jMFnLANkxtPjn8p99AZRpw"
SESSION_NAME = "BQIttNkAfDTMpvQVYuSTgZo5-dHiDor_mBtwy5SfZ3j923oT_zyQx6nPCpXfv8lPN-o720AoqPJQkUSjPMNiOzSglD-pWikKdcc0D28y0rM6L4FoKAqBhU3m2imBcLaEVR6rnKluH7nTZvyz1ZZ0mCEo-pjuGjDupNLXtQ4Ks0BISgfrltx6cYyZmNKuB54MynHhw2m-EQVMIZWRQiRsrrCFkCBnnqJGgf6w4Qszy1hbAXiKKWJ1ZW458eGxUDypR9LxG5Xt2DO1qLvnpMiLLhO1r0OLSIkgf8iLeBoZhGfN_oGWeRC5h4NcSEDTjL4mSRxSIh0w0iTiwKv98wyqMZy_9vz5XQAAAAH5PpfdAA"

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

pytgcalls = PyTgCalls(app)

ytdl_opts = {
    "format": "bestaudio",
    "quiet": True,
    "nocheckcertificate": True,
    "extract_flat": False,
    "cookiefile": None,
}

ydl = YoutubeDL(ytdl_opts)

# ──────────────────────────────
# START
# ──────────────────────────────
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎵 **Music Bot Online!**\n\n"
        "`/play <song name or url>`\n"
        "`/pause`\n"
        "`/resume`\n"
        "`/stop`"
    )

# ──────────────────────────────
# PLAY
# ──────────────────────────────
@app.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if not message.command[1:]:
        return await message.reply("❌ Song name ya URL do")

    query = " ".join(message.command[1:])

    await message.reply("🔍 Searching...")

    info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    url = info["url"]
    title = info["title"]

    await pytgcalls.join_group_call(
        message.chat.id,
        AudioPiped(url),
        stream_type=StreamType().pulse_stream
    )

    await message.reply(f"▶️ **Playing:** `{title}`")

# ──────────────────────────────
# PAUSE
# ──────────────────────────────
@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message: Message):
    await pytgcalls.pause_stream(message.chat.id)
    await message.reply("⏸️ Paused")

# ──────────────────────────────
# RESUME
# ──────────────────────────────
@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message: Message):
    await pytgcalls.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed")

# ──────────────────────────────
# STOP
# ──────────────────────────────
@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply("⏹️ Stopped & Left VC")

# ──────────────────────────────
# RUN
# ──────────────────────────────
async def main():
    await app.start()
    await pytgcalls.start()
    print("🎵 Music Bot Started")
    await asyncio.Event().wait()

asyncio.run(main())

