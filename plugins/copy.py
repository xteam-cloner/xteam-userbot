import os
import re
import time
import asyncio
from datetime import datetime as dt
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from . import LOGS, time_formatter, downloader, random_string, ultroid_cmd, eod
from . import *

REGEXA = r"^(?:(?:https|tg):\/\/)?(?:www\.)?(?:t\.me\/|openmessage\?)(?:(?:c\/(\d+))|(\w+)|(?:user_id\=(\d+)))(?:\/|&message_id\=)(\d+)(?:\?single)?$"
DL_DIR = "resources/downloads"

def rnd_filename(path):
    if not os.path.exists(path):
        return path
    name, ext = os.path.splitext(path)
    return f"{name}_{int(time.time())}{ext}"

@ultroid_cmd(
    pattern="cmedia(?: |$)((?:.|\n)*)",
)
async def fwd_dl(e):
    ghomst = await e.eor("`checking...`")
    args = e.pattern_match.group(1)
    if not args:
        reply = await e.get_reply_message()
        if reply and reply.text:
            args = reply.message
        else:
            return await eod(ghomst, "Give a tg link to download", time=10)
    
    remgx = re.findall(REGEXA, args)
    if not remgx:
        return await ghomst.edit("`Link tidak valid!`")

    try:
        chat, id = [i for i in remgx[0] if i]
        channel = int(chat) if chat.isdigit() else chat
        msg_id = int(id)
    except Exception:
        return await ghomst.edit("`Gagal memproses link.`")

    try:
        msg = await e.client.get_messages(channel, ids=msg_id)
    except Exception as ex:
        return await ghomst.edit(f"**Error:** `{ex}`")

    if not msg or not msg.media:
        return await ghomst.edit("`Pesan tidak mengandung media.`")

    start_ = dt.now()
    chat_dir = os.path.join(DL_DIR, str(e.chat_id))
    os.makedirs(chat_dir, exist_ok=True)
    
    try:
        if hasattr(msg.media, "photo"):
            dls = await e.client.download_media(msg, chat_dir)
        elif hasattr(msg.media, "document"):
            fn = msg.file.name or f"{channel}_{msg_id}{msg.file.ext}"
            filename = rnd_filename(os.path.join(chat_dir, fn))
            dlx = await downloader(
                filename,
                msg.document,
                ghomst,
                time.time(),
                f"Downloading {filename}...",
            )
            dls = dlx.name
        else:
            return await ghomst.edit("`Tipe media tidak didukung.`")

        end_ = dt.now()
        ts = time_formatter(((end_ - start_).seconds) * 1000)
        await ghomst.edit(f"**Downloaded in {ts} !!**\n » `{dls}`")

    except Exception as ex:
        LOGS.exception(ex)
        await ghomst.edit(f"**Error:** `{ex}`")
            
