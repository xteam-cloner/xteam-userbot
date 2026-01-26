import asyncio
import re
import io
from . import LOGS, ultroid_cmd, eod
from . import *

REGEXA = r"t\.me\/c\/(\d+)\/(\d+)"

@ultroid_cmd(
    pattern="cmedia(?: |$)((?:.|\n)*)",
)
async def bulk_fwd(e):
    ghomst = await e.eor("`Processing protected media...`")
    args = e.pattern_match.group(1)
    
    if not args:
        reply = await e.get_reply_message()
        if reply and reply.text:
            args = reply.text
        else:
            return await eod(ghomst, "Berikan link pesan awal.", time=10)

    match = re.search(REGEXA, args)
    if not match:
        return await ghomst.edit("`Format link salah!`")

    try:
        channel_id = int("-100" + match.group(1))
        start_msg_id = int(match.group(2))
    except Exception as ex:
        return await ghomst.edit(f"`Error parsing ID: {ex}`")

    success = 0
    await ghomst.edit("`Downloading to memory & re-uploading...`")

    try:
        async for msg in e.client.iter_messages(channel_id, min_id=start_msg_id - 1, reverse=True):
            if msg.media:
                try:
                    # Menghindari error proteksi dengan download ke buffer (RAM)
                    file_buffer = io.BytesIO()
                    await e.client.download_media(msg.media, file_buffer)
                    file_buffer.seek(0)
                    
                    # Beri nama file sederhana agar Telegram tahu tipenya
                    filename = getattr(msg.file, 'name', 'file') or "media"
                    if not "." in filename and msg.file.ext:
                        filename += msg.file.ext

                    await e.client.send_file(e.chat_id, file_buffer, force_document=False, caption=None)
                    success += 1
                    
                    # Jeda agar tidak terkena Limit
                    await asyncio.sleep(2.0) 
                except Exception as err:
                    LOGS.error(f"Gagal mengirim {msg.id}: {err}")
                    if "FloodWait" in str(err):
                        wait_seconds = int(re.findall(r'\d+', str(err))[0])
                        await asyncio.sleep(wait_seconds + 5)
            
    except Exception as ex:
        LOGS.exception(ex)
        return await ghomst.edit(f"**Stop Error:** `{ex}`")

    await ghomst.edit(f"**Selesai!** Berhasil mengirim `{success}` media terproteksi.")
                                           
