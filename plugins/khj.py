# plugins/my_utility_plugin.py
from xteam._misc import *
from . import * # Import semua yang diperlukan dari core Ultroid
#from pyrogram import Client
#from pyrogram.errors import UserNotParticipant

async def get_all_user_ids():
    user_ids = []
    
    # Dapatkan ID bot yang sedang berjalan (Ultroid client)
    try:
        me = await bot.get_me()
        user_ids.append(me.id)
    except Exception as e:
        LOGS.error(f"Gagal mendapatkan ID bot utama: {e}")

    # Tambahkan SUDO_USERS dari konfigurasi Ultroid
    if udB.get_key("FULLSUDO"):
        for sudo_id in udB.get_key("FULLSUDO"):
            try:
                # Pastikan SUDO_USERS adalah integer
                user_ids.append(int(sudo_id))
            except ValueError:
                LOGS.warning(f"SUDO_USER yang tidak valid di konfigurasi: {sudo_id}")
    
    # Jika ada kebutuhan untuk client lain, Anda harus menginisialisasinya secara terpisah
    # atau memiliki logika untuk mengaksesnya, yang tidak langsung ditangani Ultroid secara default.
    # Misalnya, jika Anda memiliki sesi Pyrogram lain yang dikelola.

    return list(set(user_ids)) # Gunakan set untuk menghindari duplikasi ID


@ultroid_cmd(pattern="myids")
async def my_ids_command(event):
    """
    Menampilkan semua ID pengguna yang terdaftar (bot dan sudo).
    """
    user_ids = await get_all_user_ids()
    response_msg = "🪪 **Daftar ID Pengguna:**\n"
    for uid in user_ids:
        response_msg += f"- `{uid}`\n"
    
    await event.eor(response_msg)
