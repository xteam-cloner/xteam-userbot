import re
import time
from telethon import Button
from xteam.fns.helper import time_formatter
from assistant import asst
from . import (
    OWNER_ID,
    LOGS,
    udB,
    ultroid_cmd,
    start_time,
get_string,
)
from xteam._misc._assistant import callback, in_pattern

# ================================================#
# --- BUTTONS KHUSUS PING ---
# ================================================#

PING_BUTTONS = [
    [
        Button.inline("Refresh", data="ping_btn"),
    ],
]

def ping_buttons():
    return [[Button.inline("🏡", data="ultd")]]

# ================================================#
# --- PING UTILITY ---
# ================================================#

async def get_ping_message_and_buttons(client):
    
    start_time_ping = time.time()
    await client.get_me() 
    latency_ms = round((time.time() - start_time_ping) * 100)
    
    uptime = time_formatter((time.time() - start_time) * 100)
    end = latency_ms
    
    owner_entity = await client.get_entity(OWNER_ID)
    owner_name = owner_entity.first_name 
    
    emoji_ping_html = (str(udB.get_key("EMOJI_PING")) if udB.get_key("EMOJI_PING") else "🏓") + " "
    emoji_uptime_html = (str(udB.get_key("EMOJI_UPTIME")) if udB.get_key("EMOJI_UPTIME") else "⏰") + " "
    emoji_owner_html = (str(udB.get_key("EMOJI_OWNER")) if udB.get_key("EMOJI_OWNER") else "👑") + " "
    
    bot_header_text = "<b><a href='https://github.com/xteam-cloner/xteam-urbot'>𖤓⋆xᴛᴇᴀᴍ ᴜʀʙᴏᴛ⋆𖤓</a></b>" 
    owner_html_mention = f"<a href='tg://user?id={OWNER_ID}'>{owner_name}</a>"
    display_name = f"OWNER : {owner_html_mention} | UB" 
    
    ping_message = f"""
<blockquote>{emoji_ping_html} Ping : {end}ms
{emoji_uptime_html} Uptime : {uptime}
{emoji_owner_html} {display_name}
</blockquote>
"""
    
    return ping_message, PING_BUTTONS 

# ================================================#
# --- PERINTAH DAN INLINE HANDLERS PING ---
# ================================================#


@ultroid_cmd(pattern="ping(?: |$)(.*)?", chats=[], type=["official", "assistant"])
async def ping_command_unified(event):
    client = event.client
    match = event.pattern_match.group(1).strip().lower()

    if match in ["inline", "i"]:
        try:
            results = await client.inline_query(asst.me.username, "ping")
            
            if results:
                await results[0].click(
                    event.chat_id, 
                    reply_to=event.id, 
                    hide_via=True
                )
                await event.delete() 
            else:
                await event.reply("❌ Gagal mendapatkan hasil status bot melalui inline query.")

        except Exception as e:
            LOGS.exception(e)
            await event.reply(f"Terjadi kesalahan saat memanggil inline ping: `{type(e).__name__}: {e}`")

    elif not match:
        try:
            start = time.time()
            
            x = await event.eor("Pong !")
            
            end = round((time.time() - start) * 1000)
            
            uptime = time_formatter((time.time() - start_time) * 1000)
            
            await x.edit(get_string("ping").format(end, uptime))

        except Exception as e:
            LOGS.exception(e)
            await event.reply(f"Terjadi kesalahan saat menjalankan ping biasa: `{type(e).__name__}: {e}`")
    
    else:
        await event.reply(f"❌ Argumen tidak dikenal: **`{match}`**. Gunakan `.ping` atau `.ping inline`.")
        


@in_pattern("ping", owner=False) 
async def inline_ping_handler(ult):
    ping_message, buttons = await get_ping_message_and_buttons(ult.client)
    
    pic = udB.get_key("PING_PIC")
    
    if pic:
        pass
            
    result = [
        await ult.builder.article(
            "Bot Status", 
            text=ping_message,                 
            parse_mode="html", 
            link_preview=False, 
            buttons=PING_BUTTONS
        )
    ]
    await ult.answer(result, cache_time=0)
    

@callback(re.compile("ping_btn(.*)"), owner=False) 
async def callback_ping_handler(ult):
    
    ping_message, _ = await get_ping_message_and_buttons(ult.client)
    
    await ult.edit(
        ping_message, 
        buttons=PING_BUTTONS,
        link_preview=False,
        parse_mode="html"
    )
    
    await ult.answer("Status Bot diperbarui.", alert=False)
      
