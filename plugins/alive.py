import re
import time
from git import Repo
from telethon import Button
from platform import python_version as pyver
from pyrogram import __version__ as pver
from telethon import __version__ as tver
from random import choice
from telethon.utils import resolve_bot_file_id
from xteam.fns.helper import time_formatter 
from assistant import asst
from . import (
    OWNER_ID,
    OWNER_NAME,
    LOGS,
    udB,
    ultroid_cmd,
    start_time,
)
from xteam._misc._assistant import callback, in_pattern

# ================================================#
# --- BUTTONS KHUSUS ALIVE ---
# ================================================#

ALIVE_BUTTONS = [
    [
        Button.inline("Modules", data="uh_Official_"),
    ],
]

# ================================================#
# --- ALIVE UTILITY ---
# ================================================#

def format_message_text(uptime, branch_info=None):
    repo = Repo().remotes[0].config_reader.get("url")
    branch = Repo().active_branch
    rep = repo.replace(".git", f"/tree/{branch}")
    branch_html = f"<a href='{rep}'>{branch}</a>"
    
    bot_header_text = "<b><a href='https://github.com/xteam-cloner/xteam-urbot'>✰ xᴛᴇᴀᴍ ᴜʀʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ✰</a></b>" 
    
    if branch_info:
        branch_display = branch_info
    else:
        branch_display = branch_html
        
    msg = f"""
{bot_header_text}
_______________________________
‣ Uptime: {uptime}
‣ Telethon: {tver}
‣ Kurigram: {pver}
‣ Python: {pyver()}
‣ Branch: {branch_display}
‣ Owner: <a href='tg://user?id={OWNER_ID}'>{OWNER_NAME}</a>
_______________________________
"""
    return msg


# ================================================#
# --- PERINTAH DAN INLINE HANDLERS ALIVE ---
# ================================================#

@ultroid_cmd(pattern="alive$")
async def alive_command(event):
    client = event.client
    try:
        results = await client.inline_query(asst.me.username, "aliv")
        if results:
            await results[0].click(
                event.chat_id, 
                reply_to=event.id, 
                hide_via=True
            )
            await event.delete() 
        else:
            await event.reply(f"❌ Gagal mendapatkan status **alive** melalui inline query.")
    except Exception as e:
        LOGS.exception(e)
        await event.reply(f"Terjadi kesalahan saat memanggil inline **alive**: `{type(e).__name__}: {e}`")

@in_pattern("alive", owner=False)
async def inline_alive_query_handler(ult):
    try:
        uptime = time_formatter((time.time() - start_time) * 1000) 
        repo = Repo().active_branch
        rep = Repo().remotes[0].config_reader.get("url").replace(".git", f"/tree/{repo}")
        branch_info = f"<a href='{rep}'>{repo}</a>"
    except NameError:
        uptime = "N/A" 
        branch_info = "N/A"
        
    message_text = format_message_text(uptime, branch_info) 
    
    result = await ult.builder.article(
        text=message_text, 
        buttons=ALIVE_BUTTONS,
        title="✰ xᴛᴇᴀᴍ ᴜʀʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ✰", 
        description=f"Uptime: {uptime}",
        parse_mode="html",
    )
    await ult.answer([result], cache_time=0)

@in_pattern("aliv", owner=True)
async def inline_alive_owner(ult):
    pic = udB.get_key("ALIVE_PIC") 
    
    if not isinstance(pic, (str, list)):
        pic = None

    if isinstance(pic, list):
        pic = choice(pic)
        
    uptime = time_formatter((time.time() - start_time) * 1000)
    
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f"<a href={rep}>{y}</a>"
    
    als = format_message_text(uptime, kk) 

    builder = ult.builder
    
    if pic:
        try:
            if ".jpg" in pic:
                results = [
                    await builder.photo(
                        pic, text=als, parse_mode="html", buttons=ALIVE_BUTTONS
                    )
                ]
            else:
                if _pic := resolve_bot_file_id(pic):
                    pic = _pic
                
                results = [
                    await builder.document(
                        pic,
                        title="Inline Alive",
                        description="@TeamUltroid",
                        parse_mode="html",
                        buttons=ALIVE_BUTTONS,
                        text=als
                    )
                ]
            return await ult.answer(results)
        except BaseException as er:
            LOGS.exception(er)
            
    result = [
        await builder.article(
            "Alive", text=als, parse_mode="html", link_preview=False, buttons=ALIVE_BUTTONS
        )
    ]
    await ult.answer(result)


@callback(re.compile("alive_btn(.*)"), owner=False)
async def callback_alive_handler(ult):
    try:
        uptime = time_formatter((time.time() - start_time) * 1000) 
        repo = Repo().active_branch
        rep = Repo().remotes[0].config_reader.get("url").replace(".git", f"/tree/{repo}")
        branch_info = f"<a href='{rep}'>{repo}</a>"
    except NameError:
        uptime = "N/A" 
        branch_info = "N/A"
        
    message_text = format_message_text(uptime, branch_info) 
    
    await ult.edit(
        message_text, 
        buttons=ALIVE_BUTTONS,
        link_preview=False,
        parse_mode="html"
    )
    await ult.answer(f"Status ALIVE diperbarui. Uptime: {uptime}", alert=False)
    
