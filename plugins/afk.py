import asyncio
from datetime import datetime, timedelta
from telethon import events
from telegraph import upload_file as uf
import time
import pytz

# --- Impor Project-Specific (xteam/Ultroid) ---
from xteam._misc._decorators import ultroid_cmd
from xteam.dB.afk_db import add_afk, del_afk, is_afk
from xteam.dB.base import KeyManager
from . import (
    LOG_CHANNEL,
    NOSPAM_CHAT,
    Redis,
    asst,
    mediainfo,
    udB,
    ultroid_bot,
)
# --- Akhir Impor ---

# List global untuk melacak pesan status AFK yang perlu dihapus
old_afk_msg = []
# Asumsi KeyManager("PMPERMIT", cast=list).contains sudah didefinisikan/diimpor
is_approved = KeyManager("PMPERMIT", cast=list).contains

## 🛠️ Fungsi Utilitas

# Fungsi utilitas untuk mendapatkan waktu mulai dan zona waktu
def get_current_time_and_timezone():
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    # 👇 PERBAIKAN: Format yang konsisten dan mencakup tahun (%Y)
    START_TIME_FORMAT = "%B %d, %Y, %H:%M %p"
    start_time_str = now.strftime(START_TIME_FORMAT)
    return start_time_str, now, now.tzname(), START_TIME_FORMAT

def format_afk_duration(start_time_dt):
    # Mengambil waktu saat ini di zona waktu yang sama dengan waktu mulai
    now_dt = datetime.now(start_time_dt.tzinfo)
    delta = now_dt - start_time_dt

    total_seconds = int(delta.total_seconds())

    # Mencegah hasil negatif/error
    if total_seconds < 0:
        total_seconds = 0

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours} Hours, {minutes} Minutes, {seconds} Seconds"

# Pengganti untuk get_string
def get_string(key):
    strings = {
        "afk_status": (
            "<b><u>★ Since   : {start_time_str}</u></b>\n"
            "<b><u>𖤓 Timezone: {timezone}</u></b>\n"
            "<b><u>♨ Reason  : {text}</u></b>"
        ),
        "afk_back_msg": (
            "I'm back! I was AFK for:\n"
            "<blockquote>{afk_duration}</blockquote>"
        ),
    }
    return strings.get(key, "String not found")

def convert_afk_time(start_time_str):
    tz = pytz.timezone('Asia/Jakarta')
    # Format yang sama dengan yang digunakan di get_current_time_and_timezone
    START_TIME_FORMAT = "%B %d, %Y, %H:%M %p"
    
    try:
        # Mencoba mengkonversi dengan format yang benar
        naive_dt = datetime.strptime(start_time_str, START_TIME_FORMAT)
        start_time_dt = tz.localize(naive_dt)
    except Exception:
        # Fallback: Menggunakan waktu saat ini - 1 detik jika konversi gagal
        start_time_dt = datetime.now(tz) - timedelta(seconds=1)
        
    return start_time_dt

## ⚙️ Handler Utama

@ultroid_cmd(pattern="afk( (.*)|$)", owner_only=True)
async def set_afk(event):
    if event.client._bot or is_afk():
        return

    text, media, media_type = None, None, None
    msg1, msg2 = None, None

    # Mengambil alasan dari argumen atau reply
    reason_match = event.pattern_match.group(2)
    text = reason_match.strip() if reason_match else "No reason specified"

    start_time_str, start_time_dt, timezone, _ = get_current_time_and_timezone()

    reply = await event.get_reply_message()
    if reply:
        if reply.text and text == "No reason specified":
            text = reply.text
        if reply.media:
            media_type = mediainfo(reply.media)
            if media_type.startswith(("pic", "gif")):
                file = await event.client.download_media(reply.media)
                try:
                    iurl = uf(file)
                    media = f"https://graph.org{iurl[0]}"
                except Exception:
                    media = reply.file.id
            else:
                media = reply.file.id

    await event.eor("`Done`", time=2)

    # Menyimpan data AFK ke database
    add_afk(text, media_type, media, start_time_str, timezone)

    # Menambahkan Handler (Hanya untuk on_afk, handler remove_afk DIBUAT TERPISAH)
    # >>> BARIS INI DIHAPUS: ultroid_bot.add_handler(remove_afk, events.NewMessage(outgoing=True)) 
    
    ultroid_bot.add_handler(
        on_afk,
        events.NewMessage(
            incoming=True, func=lambda e: bool(e.mentioned or e.is_private)
        ),
    )

    afk_status_msg = get_string("afk_status").format(
        start_time_str=start_time_str,
        timezone=timezone,
        text=text
    )
    
    afk_header = f"<blockquote>Away from Keyboard</blockquote>"
    full_message = f"{afk_header}\n\n{afk_status_msg}"

    # Mengirim status AFK DENGAN parse_mode='html'
    if media:
        if "sticker" in media_type:
            msg1 = await ultroid_bot.send_file(event.chat_id, file=media)
            msg2 = await ultroid_bot.send_message(event.chat_id, full_message, parse_mode="html")
        else:
            # Menggunakan .send_message dengan file
            msg1 = await ultroid_bot.send_message(
                event.chat_id, full_message, file=media, parse_mode="html"
            )
    else:
        msg1 = await event.respond(full_message, parse_mode="html")

    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)

#---

async def remove_afk(event):
    if event.is_private and udB.get_key("PMSETTING") and not is_approved(event.chat_id):
        return
    elif event.text.lower().startswith(("afk", "/afk", ".afk")): # Hindari trigger jika perintah /afk dikirim
        return
    elif event.chat_id in NOSPAM_CHAT:
        return

    afk_data = is_afk()
    if afk_data:
        # Menangani skema DB lama (4 elemen) atau baru (5 elemen)
        try:
            text, media_type, media, start_time_str, timezone = afk_data
        except ValueError:
            text, media_type, media, _ = afk_data
            start_time_str, timezone = "Unknown", "Unknown"

        # PERBAIKAN KONVERSI WAKTU
        start_time_dt = convert_afk_time(start_time_str)

        afk_duration = format_afk_duration(start_time_dt)
        del_afk() # Hapus status AFK

        off = await event.reply(get_string("afk_back_msg").format(afk_duration=afk_duration), parse_mode="html")

        for x in old_afk_msg:
            try:
                await x.delete()
            except BaseException:
                pass
                
        old_afk_msg.clear() # Kosongkan list
        
        await asyncio.sleep(10)
        await off.delete()
        

@ultroid_cmd(pattern="unafk$")
async def unafk(event):
    if not is_afk():
        return await event.eor("`You are currently not AFK.`", time=3)
        
    afk_data = is_afk()
    # Menangani skema DB lama atau baru
    try:
        text, media_type, media, start_time_str, timezone = afk_data
    except ValueError:
        text, media_type, media, _ = afk_data
        start_time_str, timezone = "Unknown", "Unknown"

    # PERBAIKAN KONVERSI WAKTU
    start_time_dt = convert_afk_time(start_time_str)

    afk_duration = format_afk_duration(start_time_dt)

    # 1. Hapus status AFK dari database
    del_afk()

    # ======================================================
    # ✨ LANGKAH PENTING: HAPUS HANDLER PENDENGAR PESAN MASUK ✨
    # ======================================================
    try:
        # Panggil method remove_event_handler dari client bot Anda
        # untuk menghapus fungsi on_afk dari daftar listener aktif.
        ultroid_bot.remove_event_handler(on_afk)
    except Exception as e:
        # (Opsional) Log error jika handler gagal dihapus, 
        # tetapi ini biasanya diabaikan jika handler sudah dihapus sebelumnya.
        pass

    # 2. Kirim pesan kembali/konfirmasi
    off = await event.reply(get_string("afk_back_msg").format(afk_duration=afk_duration), parse_mode="html")
    try:
        await event.delete()  # <--- BARIS INI YANG DITAMBAHKAN
    except Exception:
        # Lewati jika gagal (misalnya, tidak ada hak admin)
        pass
    # 3. Hapus pesan status AFK lama
    for x in old_afk_msg:
        try:
            await x.delete()
        except BaseException:
            pass
            
    old_afk_msg.clear() # Kosongkan list

    # 4. Hapus pesan konfirmasi setelah 10 detik
    await asyncio.sleep(5)
    await off.delete()


#---

async def on_afk(event):
    if event.is_private and Redis("PMSETTING") and not is_approved(event.chat_id):
        return
    elif event.text.lower().startswith(("afk", "/afk", ".afk")): # Hindari trigger jika pesan adalah perintah afk
        return
    elif not is_afk():
        return
    if event.chat_id in NOSPAM_CHAT:
        return
        
    sender = await event.get_sender()
    if sender.bot or sender.verified:
        return

    afk_data = is_afk()
    if not afk_data: return

    # Menangani skema DB lama atau baru
    try:
        text, media_type, media, start_time_str, timezone = afk_data
    except ValueError:
        text, media_type, media, _ = afk_data
        start_time_str, timezone = "Unknown", "Unknown"

    # PERBAIKAN KONVERSI WAKTU
    start_time_dt = convert_afk_time(start_time_str)
    
    afk_duration = format_afk_duration(start_time_dt)

    status_msg = get_string("afk_status").format(
        start_time_str=start_time_str,
        timezone=timezone,
        text=text if text else "None"
    )

    # Format akhir dengan HTML <code>
    final_text = (
        f"<b>Away from Keyboard</b>\n\n"
        f"{status_msg}\n\n"
        f"<blockquote>{afk_duration}</blockquote>"
    )

    # Hapus pesan AFK lama sebelum mengirim yang baru
    for x in old_afk_msg:
        try:
            await x.delete()
        except BaseException:
            pass
            
    old_afk_msg.clear()

    # Mengirim pesan DENGAN parse_mode='html'
    msg1, msg2 = None, None
    if media:
        if "sticker" in media_type:
            msg1 = await event.reply(file=media)
            msg2 = await event.reply(final_text, parse_mode="html")
        else:
            msg1 = await event.reply(final_text, file=media, parse_mode="html")
    else:
        msg1 = await event.reply(final_text, parse_mode="html")

    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)

# Menambahkan handler secara persisten jika ada data AFK di DB saat bot dimulai
if udB.get_key("AFK_DB"):
    ultroid_bot.add_handler(remove_afk, events.NewMessage(outgoing=True))
    ultroid_bot.add_handler(
        on_afk,
        events.NewMessage(
            incoming=True, func=lambda e: bool(e.mentioned or e.is_private)
        ),
        )
