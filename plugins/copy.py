import asyncio
import re
from . import LOGS, ultroid_cmd, eod
from . import *

# Regex khusus untuk menangkap ID Channel Private dan ID Pesan
REGEXA = r"t\.me\/c\/(\d+)\/(\d+)"

@ultroid_cmd(
    pattern="cmedia(?: |$)((?:.|\n)*)",
)
async def bulk_fwd(e):
    ghomst = await e.eor("`Processing private channel link...`")
    args = e.pattern_match.group(1)
    
    if not args:
        reply = await e.get_reply_message()
        if reply and reply.text:
            args = reply.text
        else:
            return await eod(ghomst, "Berikan link pesan awal.", time=10)

    match = re.search(REGEXA, args)
    if not match:
        return await ghomst.edit("`Gunakan format link private: https://t.me/c/3668675664/93`")

    try:
        # Untuk link /c/, ID channel harus ditambah -100 di depannya
        channel_id = int("-100" + match.group(1))
        start_msg_id = int(match.group(2))
    except Exception as ex:
        return await ghomst.edit(f"`Error parsing ID: {ex}`")

    success = 0
    await ghomst.edit("`Scanning and sending media only...`")

    try:
        # Mengambil pesan dari ID tersebut ke atas
        async for msg in e.client.iter_messages(channel_id, min_id=start_msg_id - 1, reverse=True):
            if msg.media:
                try:
                    # Mengirim hanya file media tanpa caption/teks
                    await e.client.send_file(e.chat_id, msg.media)
                    success += 1
                    await asyncio.sleep(1.5) # Jeda lebih lama agar tidak terkena Flood
                except Exception as err:
                    LOGS.error(f"Gagal mengirim {msg.id}: {err}")
                    if "FloodWait" in str(err):
                        wait_seconds = int(re.findall(r'\d+', str(err))[0])
                        await asyncio.sleep(wait_seconds + 5)
            
    except Exception as ex:
        LOGS.exception(ex)
        return await ghomst.edit(f"**Stop Error:** `{ex}`\nPastikan kamu sudah bergabung di channel tersebut.")

    await ghomst.edit(f"**Selesai!** Berhasil mengirim `{success}` media tanpa teks.")
                        
