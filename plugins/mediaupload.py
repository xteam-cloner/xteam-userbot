import asyncio
import os
import aiohttp # <<< Perlu diimpor untuk permintaan HTTP Asinkron
import json
from . import ultroid_cmd, eor, ULTROID_IMAGES
from random import choice

# URL API untuk envs.sh
ENVS_SH_API_URL = "https://envs.sh/"

# Fungsi untuk mendapatkan gambar inline (tetap)
def inline_pic():
    return choice(ULTROID_IMAGES)

@ultroid_cmd(pattern="envs(?: |$)(.*)")
async def envs_sh_upload_plugin(event):
    """
    Plugin untuk mengunggah file ke envs.sh (atau memperpendek URL).
    Sintaks: .envs [secret|expires=N|shorten=URL]
    """
    # Mengurai argumen perintah
    args = event.pattern_match.group(1).split()
    
    is_secret = 'secret' in args
    expires = None
    shorten_url = None
    
    for arg in args:
        if arg.startswith("expires="):
            try:
                # Mengambil nilai N setelah 'expires='
                expires = arg.split("=", 1)[1]
                # Cek validitas, misalnya hanya menerima bilangan
                if not expires.isdigit():
                    return await eor(event, "❌ Nilai 'expires' harus berupa angka (jam) atau timestamp Epoch Milliseconds.")
            except IndexError:
                pass # Tetap None jika tidak ada nilai
        elif arg.startswith("shorten="):
            shorten_url = arg.split("=", 1)[1]

    # --- Mode URL Shortener ---
    if shorten_url:
        message = await eor(event, "Memperpendek URL...")
        payload = {'shorten': shorten_url}
        if is_secret:
            payload['secret'] = ''
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ENVS_SH_API_URL, data=payload) as response:
                    
                    if response.status == 200:
                        uploaded_url = await response.text()
                        await message.edit(
                            f"<blockquote>🔗 Successful URL Shorten!\nOriginal: {shorten_url}\nShort URL: {uploaded_url.strip()}</blockquote>", 
                            parse_mode="html"
                        )
                    else:
                        error_text = await response.text()
                        await message.edit(f"❌ Terjadi kesalahan saat memperpendek URL ({response.status}): {error_text.strip()}")
        except Exception as e:
            await message.edit(f"❌ Terjadi kesalahan koneksi: {e}")
        return

    # --- Mode Unggah File ---
    if not event.reply_to_msg_id:
        return await eor(event, "Balas ke media atau file untuk mengunggahnya ke envs.sh. Gunakan `.envs shorten=URL` untuk memperpendek URL.")

    reply_message = await event.get_reply_message()

    if not reply_message.media:
        return await eor(event, "Balas ke media atau file untuk mengunggahnya ke envs.sh.")

    message = await eor(event, "Mengunduh media...")
    filePath = None  # Inisialisasi filePath
    
    try:
        # Unduh file, dapatkan jalur lokal
        filePath = await reply_message.download_media()
        # Ambil nama file dari jalur unduhan
        fileName = os.path.basename(filePath) 

        await message.edit("Mengunggah ke envs.sh...")
        
        # Buka file dalam mode biner untuk diunggah
        with open(filePath, 'rb') as file_data:
            
            # Buat aiohttp.FormData untuk mengirim multipart/form-data
            data = aiohttp.FormData()
            
            # Tambahkan file ke form data. Kunci harus 'file'
            data.add_field(
                'file',
                file_data,
                filename=fileName,
                content_type=reply_message.file.mime_type or 'application/octet-stream'
            )
            
            # Tambahkan parameter opsional
            if is_secret:
                data.add_field('secret', '')
            if expires:
                data.add_field('expires', expires)

            # Kirim permintaan POST asinkron
            async with aiohttp.ClientSession() as session:
                async with session.post(ENVS_SH_API_URL, data=data) as response:
                    
                    if response.status == 200:
                        uploaded_url = await response.text()
                        await message.edit(
                            f"<blockquote>📤 Successful upload to envs.sh!\nFile: {fileName}\nURL: {uploaded_url.strip()}</blockquote>", 
                            parse_mode="html"
                        )
                    else:
                        error_text = await response.text()
                        await message.edit(f"❌ Terjadi kesalahan saat mengunggah ({response.status}): {error_text.strip()}")

    except Exception as e:
        await message.edit(f"❌ Terjadi kesalahan saat memproses unggahan: {e}")
    finally:
        # Hapus file lokal setelah diunggah
        if filePath and os.path.exists(filePath):
            os.remove(filePath)

                
import asyncio
import os
import httpx 
from . import ultroid_cmd, eor, ULTROID_IMAGES
from random import choice


# Fungsi untuk mendapatkan gambar inline (opsional, dari kode Anda sebelumnya)
def inline_pic():
    return choice(ULTROID_IMAGES)

@ultroid_cmd(pattern="litbox") # PERUBAHAN DI SINI: pattern hanya "catbox"
async def litterbox_upload_plugin(event):
    """
    Plugin untuk mengunggah file ke Litterbox.catbox.moe.
    Waktu kedaluwarsa selalu 72 jam (3 hari).
    Sintaks: .catbox (cukup balas media)
    """
    if not event.reply_to_msg_id:
        return await eor(event, "Balas ke media atau file untuk mengunggahnya ke Litterbox.")

    reply_message = await event.get_reply_message()

    if not reply_message.media:
        return await eor(event, "Balas ke media atau file untuk mengunggahnya ke Litterbox.")

    # Tetapkan waktu kedaluwarsa secara permanen ke '72h'
    expiry_time = "72h" 
    
    # URL dan Data untuk Litterbox
    LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"
    
    message = await eor(event, "Mengunduh media...")
    filePath = None
    
    try:
        # Unduh media
        filePath = await reply_message.download_media()

        await message.edit("Mengunggah ke Litterbox.catbox.moe (Expiry: 72h)...")

        # --- LOGIKA UNGGAH LITTERBOX DENGAN HTTPX ---
        
        # Buka file dalam mode binary untuk diunggah
        with open(filePath, 'rb') as f:
            
            # Data form yang diperlukan oleh API
            data_payload = {
                'reqtype': 'fileupload',
                'time': expiry_time # Nilai kini selalu '72h'
            }
            
            # Bagian file untuk unggahan multipart/form-data
            files_payload = {
                'fileToUpload': f 
            }

            # Gunakan httpx.AsyncClient untuk permintaan POST asinkron
            # Timeout ditingkatkan untuk file besar
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    LITTERBOX_URL, 
                    data=data_payload, 
                    files=files_payload
                )

        # Cek status respons dan ambil URL
        if response.status_code == 200:
            uploaded_url = response.text.strip()
            await message.edit(
                f"<blockquote>📤 Successful Litterbox upload!\n**Expiry:** {expiry_time}\nURL: {uploaded_url}</blockquote>", 
                parse_mode="html"
            )
        else:
            await message.edit(f"Terjadi kesalahan saat mengunggah (Status: {response.status_code}): {response.text}")

    except Exception as e:
        await message.edit(f"Terjadi kesalahan saat mengunggah: <code>{type(e).__name__}: {e}</code>", parse_mode="html")
    finally:
        # Hapus file lokal setelah diunggah
        if filePath and os.path.exists(filePath):
            os.remove(filePath)
