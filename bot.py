import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioEnded
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

queues = {}  # {chat_id: [song1, song2, ...], max 10}

# ---------- YOUTUBE DOWNLOADER ---------- #
async def download_audio(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        return ydl.prepare_filename(info)


# ---------- PLAYBACK LOGIC ---------- #
async def play_next(chat_id):
    if chat_id not in queues or len(queues[chat_id]) == 0:
        await vc.leave_group_call(chat_id)
        return

    song = queues[chat_id].pop(0)

    await vc.join_group_call(
        chat_id,
        AudioPiped(song),
    )


@vc.on_stream_end()
async def on_end(_, update: StreamAudioEnded):
    chat_id = update.chat_id
    await play_next(chat_id)


# ---------- COMMANDS ---------- #
@app.on_message(filters.command("play") & filters.group)
async def play_handler(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply("❌ Song name/link do.")

    if m.chat.id not in queues:
        queues[m.chat.id] = []

    if len(queues[m.chat.id]) >= 10:
        return await m.reply("❌ Queue full (max 10).")

    msg = await m.reply("⏳ Downloading...")

    file = await download_audio(query)
    queues[m.chat.id].append(file)

    if not vc.active_calls.get(m.chat.id):
        await msg.edit("▶ Playing now...")
        await play_next(m.chat.id)
    else:
        await msg.edit("➕ Added to queue.")


@app.on_message(filters.command("playforce") & filters.group)
async def playforce_handler(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply("❌ Song name/link do.")

    msg = await m.reply("⏳ Downloading...")

    file = await download_audio(query)

    queues[m.chat.id] = [file]  # clear queue + add song

    await vc.join_group_call(
        m.chat.id,
        AudioPiped(file),
    )

    await msg.edit("⚡ Force playing now!")


@app.on_message(filters.command("next") & filters.group)
async def next_handler(_, m):
    member = await m.chat.get_member(m.from_user.id)
    if not (member.status in ["administrator", "creator"]):
        return await m.reply("❌ Only admins can use /next")

    await m.reply("⏭ Skipping...")
    await play_next(m.chat.id)


@app.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, m):
    member = await m.chat.get_member(m.from_user.id)
    if not (member.status in ["administrator", "creator"]):
        return await m.reply("❌ Only admins can use /stop")

    queues[m.chat.id] = []
    await vc.leave_group_call(m.chat.id)
    await m.reply("⏹ Stopped.")


# ---------- START ---------- #
async def main():
    await app.start()
    await vc.start()
    print("Bot started!")
    await idle()

asyncio.run(main())
