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
    ghomst = await e.eor("`Processing media...`")
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
    await ghomst.edit("`Downloading to memory & fixing filenames...`")

    try:
        async for msg in e.client.iter_messages(channel_id, min_id=start_msg_id - 1, reverse=True):
            if msg.media:
                try:
                    # Tentukan nama file agar tidak 'unnamed'
                    # Mengambil nama asli jika ada, jika tidak beri nama default dengan ekstensinya
                    filename = getattr(msg.file, 'name', None) or f"file_{msg.id}{msg.file.ext or ''}"
                    
                    file_buffer = io.BytesIO()
                    await e.client.download_media(msg.media, file_buffer)
                    file_buffer.name = filename # Kunci utama agar nama tidak 'unnamed'
                    file_buffer.seek(0)
                    
                    await e.client.send_file(
                        e.chat_id, 
                        file_buffer, 
                        force_document=True, # Mengirim sebagai file agar nama tetap terjaga
                        caption=None
                    )
                    success += 1
                    await asyncio.sleep(1.5) 
                except Exception as err:
                    LOGS.error(f"Gagal mengirim {msg.id}: {err}")
                    await asyncio.sleep(1.0)
            
    except Exception as ex:
        LOGS.exception(ex)
        return await ghomst.edit(f"**Stop Error:** `{ex}`")

    await ghomst.edit(f"**Selesai!** Berhasil mengirim `{success}` media dengan nama yang benar.")
    



@ultroid_cmd(pattern="copymedia(?: |$)((?:.|\n)*)")
async def bulk_fwd(e):
    ghomst = await e.eor("`Processing media...`")
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
        return await ghomst.edit(f"`Error: {ex}`")

    success = 0
    try:
        async for msg in e.client.iter_messages(channel_id, min_id=start_msg_id - 1, reverse=True):
            if msg.media:
                try:
                    # Ambil nama asli atau buat nama default
                    filename = getattr(msg.file, 'name', None) or f"file_{msg.id}{msg.file.ext or ''}"
                    
                    file_buffer = io.BytesIO()
                    await e.client.download_media(msg.media, file_buffer)
                    file_buffer.name = filename
                    file_buffer.seek(0)
                    
                    # Cek jenis media
                    is_video = hasattr(msg.media, 'document') and msg.file.mime_type.startswith('video')
                    is_photo = hasattr(msg.media, 'photo')

                    # Kirim sebagai media (besar) jika foto/video, selain itu dokumen
                    await e.client.send_file(
                        e.chat_id, 
                        file_buffer, 
                        force_document=not (is_video or is_photo),
                        caption=None,
                        supports_streaming=True if is_video else False
                    )
                    
                    success += 1
                    await asyncio.sleep(1.5) 
                except Exception as err:
                    LOGS.error(f"Gagal mengirim {msg.id}: {err}")
            
    except Exception as ex:
        LOGS.exception(ex)
        return await ghomst.edit(f"**Stop Error:** `{ex}`")

    await ghomst.edit(f"**Selesai!** Berhasil mengirim `{success}` media.")
                
