# < Source - t.me/testingpluginnn >
# < Made for Ultroid by @Spemgod! >
# < https://github.com/TeamUltroid/Ultroid >
# 
# 'TG Regex taken from @TheUserge'

"""
✘ **Download Forward restricted files!**

• **CMD:**
>  `{i}fwdl <msg_link>`
>  `{i}fwdl https://t.me/nofwd/14`
"""

import os
import re
import time
import asyncio
from datetime import datetime as dt

from telethon.errors.rpcerrorlist import MessageNotModifiedError

from . import LOGS, time_formatter, downloader, random_string, ultroid_cmd
from . import *


# Source: https://github.com/UsergeTeam/Userge/blob/7eef3d2bec25caa53e88144522101819cb6cb649/userge/plugins/misc/download.py#L76
REGEXA = r"^(?:(?:https|tg):\/\/)?(?:www\.)?(?:t\.me\/|openmessage\?)(?:(?:c\/(\d+))|(\w+)|(?:user_id\=(\d+)))(?:\/|&message_id\=)(\d+)(?:\?single)?$"
DL_DIR = "resources/downloads"


def rnd_filename(path):
    if not os.path.exists(path):
        return path
    spl = os.path.splitext(path)
    rnd = "_" + random_string(5).lower() + "_"
    return spl[0] + rnd + spl[1]


@ultroid_cmd(
    pattern="fwdl(?: |$)((?:.|\n)*)",
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
        return await ghomst.edit("`probably a invalid Link !?`")

    try:
        chat, id = [i for i in remgx[0] if i]
        channel = int(chat) if chat.isdigit() else chat
        msg_id = int(id)
    except Exception as ex:
        return await ghomst.edit("`Give a valid tg link to proceed`")

    try:
        msg = await e.client.get_messages(channel, ids=msg_id)
    except Exception as ex:
        return await ghomst.edit(f"**Error:**  `{ex}`")

    start_ = dt.now()
    if (msg and msg.media) and hasattr(msg.media, "photo"):
        dls = await e.client.download_media(msg, DL_DIR)
    elif (msg and msg.media) and hasattr(msg.media, "document"):
        fn = msg.file.name or f"{channel}_{msg_id}{msg.file.ext}"
        filename = rnd_filename(os.path.join(DL_DIR, fn))
        try:
            dlx = await downloader(
                filename,
                msg.document,
                ghomst,
                time.time(),
                f"Downloading {filename}...",
            )
            dls = dlx.name
        except MessageNotModifiedError as err:
            LOGS.exception(err)
            return await xx.edit(str(err))
    else:
        return await ghomst.edit("`Message doesn't contain any media to download.`")

    end_ = dt.now()
    ts = time_formatter(((end_ - start_).seconds) * 1000)
    await ghomst.edit(f"**Downloaded in {ts} !!**\n » `{dls}`")
  


import os
import re
import time
import asyncio
from datetime import datetime as dt

from telethon.errors.rpcerrorlist import MessageNotModifiedError

from . import LOGS, time_formatter, downloader, random_string, ultroid_cmd
from . import *


# Source: https://github.com/UsergeTeam/Userge/blob/7eef3d2bec25caa53e88144522101819cb6cb649/userge/plugins/misc/download.py#L76
REGEXA = r"^(?:(?:https|tg):\/\/)?(?:www\.)?(?:t\.me\/|openmessage\?)(?:(?:c\/(\d+))|(\w+)|(?:user_id\=(\d+)))(?:\/|&message_id\=)(\d+)(?:\?single)?$"
# DL_DIR = "resources/downloads" <--- BARIS INI DIHAPUS


# Fungsi rnd_filename tidak lagi relevan tetapi dipertahankan jika ada kebutuhan lain
def rnd_filename(path):
    if not os.path.exists(path):
        return path
    spl = os.path.splitext(path)
    rnd = "_" + random_string(5).lower() + "_"
    return spl[0] + rnd + spl[1]


@ultroid_cmd(
    pattern="fwdlol(?: |$)((?:.|\n)*)",
)
async def fwd_dl(e):
    
    ghomst = await e.eor("`mencari dan mengunduh...`")
    args = e.pattern_match.group(1)
    if not args:
        reply = await e.get_reply_message()
        if reply and reply.text:
            args = reply.message
        else:
            return await eod(ghomst, "Berikan tautan Telegram untuk diunduh.", time=10)
    
    remgx = re.findall(REGEXA, args)
    if not remgx:
        return await ghomst.edit("`Tampaknya tautan tidak valid!?" )

    try:
        chat, id = [i for i in remgx[0] if i]
        channel = int(chat) if chat.isdigit() else chat
        msg_id = int(id)
    except Exception as ex:
        return await ghomst.edit("`Berikan tautan Telegram yang valid untuk diproses`")

    try:
        msg = await e.client.get_messages(channel, ids=msg_id)
    except Exception as ex:
        return await ghomst.edit(f"**Kesalahan:** `{ex}`")

    start_ = dt.now()
    
    # --- LOGIKA UNGGAH FILE LANGSUNG KE CHAT ---
    try:
        if msg and msg.media:
            # Menggunakan send_file untuk mengunggah media langsung ke chat saat ini (e.chat_id)
            await e.client.send_file(
                e.chat_id, 
                msg.media, 
                caption=msg.message, 
                force_document=False, # Mengirim sebagai media (foto/video)
                allow_send_without_reply=True
            )
        else:
            return await ghomst.edit("`Pesan tidak mengandung media untuk diunduh/diunggah.`")

    except Exception as ex:
        LOGS.exception(ex)
        return await ghomst.edit(f"**Kesalahan Unggahan:** `{ex}`")
    # --- AKHIR LOGIKA UNGGAH ---

    end_ = dt.now()
    ts = time_formatter(((end_ - start_).seconds) * 1000)
    
    # Hapus pesan status awal dan kirim balasan konfirmasi ke chat
    await ghomst.delete()
    await e.reply(f"**Berhasil diunduh dan diunggah dalam {ts}!**")
