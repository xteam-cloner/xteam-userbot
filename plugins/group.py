from telethon.tl.types import Channel, Chat, User
from . import ultroid_cmd, ultroid_bot, start_time

client = ultroid_bot 

@ultroid_cmd(pattern="totalgroup( (.*)|$)", fullsudo=True)
async def hitung_total_grup_plugin(event):
    await event.edit("🔄 Mulai menghitung semua dialog...")

    total_grup_kecil = 0
    total_supergroup = 0
    total_channel_broadcast = 0
    total_chat_pribadi = 0 
    
    async for dialog in event.client.iter_dialogs(): 
        entity = dialog.entity
        
        if isinstance(entity, User):
            total_chat_pribadi += 1
        elif isinstance(entity, Channel):
            if entity.megagroup:
                total_supergroup += 1
            elif entity.broadcast:
                total_channel_broadcast += 1
        elif isinstance(entity, Chat): 
            total_grup_kecil += 1
            
    total_semua_grup = total_grup_kecil + total_supergroup
    total_grup_channel = total_semua_grup + total_channel_broadcast
    
    output = (
        "<blockquote>📊 Hasil Total Entitas\n"
        "--------------------------------------------------\n"
        f"👤 Total Obrolan Pribadi : {total_chat_pribadi}\n"
        f"👥 Total Group : {total_semua_grup}\n"
        f"📣 Total Channel : {total_channel_broadcast}\n"
        "--------------------------------------------------\n"
        f"✨ TOTAL SELURUH GRUP & CHANNEL: {total_grup_channel} entitas</blockquote>"
    )

    await event.edit(output, parse_mode="html")

 
import time
from datetime import timedelta

START_TIME = start_time 

client = ultroid_bot 

@ultroid_cmd(pattern="status(| (.*))$", fullsudo=True)
async def status_checker(event):
    # 1. Kirim pesan placeholder baru sebagai respons, bukan mengedit pesan perintah
    placeholder = await event.respond("🔄 Mengambil status klien dan menghitung dialog...") 
    
    total_grup_kecil = 0
    total_supergroup = 0
    total_chat_pribadi = 0 
    
    async for dialog in event.client.iter_dialogs(): 
        entity = dialog.entity
        
        if isinstance(entity, User):
            total_chat_pribadi += 1
        elif isinstance(entity, Channel):
            if entity.megagroup:
                total_supergroup += 1
        elif isinstance(entity, Chat): 
            total_grup_kecil += 1
            
    total_semua_grup = total_grup_kecil + total_supergroup
    
    try:
        me = await event.client.get_me()
        is_premium = getattr(me, 'premium', False)
        dc_id = event.client.session.dc_id
    except Exception:
        is_premium = False
        dc_id = 'Unknown'

    try:
        ping_result = await event.client.ping_service(dc_id=dc_id)
        ping_dc = ping_result.get('duration', float('inf')) * 1000
    except Exception:
        ping_dc = float('inf')

    current_time = time.time()
    uptime_seconds = current_time - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    
    status_level = "Ultra Max" if is_premium else "Standard"
    
    output = (
        f"**Status: [{status_level}]**\n"
        "--------------------------------------------------\n"
        f"    `is_premium:` `{is_premium}`\n"
        f"    `peer_users:` `{total_chat_pribadi}`\n" 
        f"    `peer_group:` `{total_semua_grup}`\n"
        f"    `dc_id:` `{dc_id}`\n"
        f"    `ping_dc:` `{ping_dc:.3f} ms`\n"
        f"    `uptime:` `{uptime_str}`"
    )

    # 2. Edit pesan placeholder yang baru saja dikirim
    await placeholder.edit(output)

