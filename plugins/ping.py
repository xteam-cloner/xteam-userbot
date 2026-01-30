import re
import time
import asyncio
from telethon import TelegramClient, events, Button
from pytgcalls import PyTgCalls
from xteam import call_py
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

PING_BUTTONS = [
    [
        Button.inline("🔄 Refresh", data="ping_btn"),
    ],
]

async def get_ping_message_and_buttons(client):
    start_time_ping = time.time()
    await client.get_me() 
    latency_ms = round((time.time() - start_time_ping) * 1000)
    
    try:
        tgcalls_ms = round(call_py.ping, 3)
    except Exception:
        tgcalls_ms = "0.0"

    uptime = time_formatter((time.time() - start_time) * 1000)
    
    owner_entity = await client.get_entity(OWNER_ID)
    owner_name = owner_entity.first_name 
    
    emoji_ping = (str(udB.get_key("EMOJI_PING")) if udB.get_key("EMOJI_PING") else "🏓")
    emoji_uptime = (str(udB.get_key("EMOJI_UPTIME")) if udB.get_key("EMOJI_UPTIME") else "⏰")
    emoji_owner = (str(udB.get_key("EMOJI_OWNER")) if udB.get_key("EMOJI_OWNER") else "👑")
    
    owner_html_mention = f"<a href='tg://user?id={OWNER_ID}'>{owner_name}</a>"
    
    ping_message = f"""
<b>𖤓⋆xᴛᴇᴀᴍ ᴜʀʙᴏᴛ⋆𖤓</b>
<blockquote>
{emoji_ping} <b>Telethon:</b> <code>{latency_ms}ms</code>
🎵 <b>PyTgCalls:</b> <code>{tgcalls_ms}ms</code>
{emoji_uptime} <b>Uptime:</b> <code>{uptime}</code>
{emoji_owner} <b>Owner:</b> {owner_html_mention}
</blockquote>
"""
    return ping_message, PING_BUTTONS 

@ultroid_cmd(pattern="ping(?: |$)(.*)?", chats=[], type=["official", "assistant"])
async def ping_command_unified(event):
    match = event.pattern_match.group(1).strip().lower()

    if match in ["inline", "i"]:
        try:
            results = await event.client.inline_query(asst.me.username, "ping")
            if results:
                await results[0].click(event.chat_id, reply_to=event.id, hide_via=True)
                await event.delete() 
            else:
                await event.reply("❌ Gagal memanggil inline mode.")
        except Exception as e:
            LOGS.exception(e)
            await event.reply(f"Kesalahan Inline: `{e}`")

    elif not match:
        try:
            start = time.time()
            x = await event.eor("`Pinging...`")
            end = round((time.time() - start) * 1000)
            
            tg_ms = round(call_py.ping, 3)
            uptime = time_formatter((time.time() - start_time) * 1000)
            
            res = (
                f"**🏓 Pong!!**\n"
                f"📡 **Telethon:** `{end}ms`\n"
                f"⚙️ **PyTgCalls:** `{tg_ms}ms`\n"
                f"⏳ **Uptime:** `{uptime}`"
            )
            await x.edit(res)
        except Exception as e:
            LOGS.exception(e)
            await event.reply(f"Kesalahan: `{e}`")
    
    else:
        await event.reply(f"❌ Argumen tidak dikenal: `{match}`")

@in_pattern("ping", owner=False) 
async def inline_ping_handler(ult):
    ping_message, buttons = await get_ping_message_and_buttons(ult.client)
    
    result = [
        await ult.builder.article(
            "Bot Status", 
            text=ping_message,                 
            parse_mode="html", 
            link_preview=False, 
            buttons=buttons
        )
    ]
    await ult.answer(result, cache_time=0)

@callback(re.compile("ping_btn(.*)"), owner=False) 
async def callback_ping_handler(ult):
    ping_message, buttons = await get_ping_message_and_buttons(ult.client)
    
    try:
        await ult.edit(
            ping_message, 
            buttons=buttons,
            link_preview=False,
            parse_mode="html"
        )
        await ult.answer("Status Bot diperbarui.", alert=False)
    except Exception:
        await ult.answer("Status sudah yang terbaru.", alert=False)
