# xteam-userbot
# Copyright (C) 2024-2026 xteam_cloner
# This file is a part of < https://github.com/xteam-cloner/xteam-userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/xteam-cloner/xteam-userbot/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}play <song name>`
   Play the song in voice chat, or add the song to queue.

• `{i}vplay <video name>`
   Play the video in voice chat, or add the song to queue.

1• `{i}paus`
   Pause stream
     
• `{i}volume <number>`
   Put number between 1 to 100

• `{i}skip`
   Skip the current song and play the next in queue, if any.

• `{i}playlist`
   List the songs in queue.
   
• `{i}end / stop`
   Stop Stream 

"""

from __future__ import annotations
import asyncio
import os
import logging
from telethon import events, Button
from . import *
from xteam.configs import Var 
from xteam import call_py, asst
from pytgcalls.types import Update, StreamEnded
from . import ultroid_bot, ultroid_cmd as man_cmd, eor as edit_or_reply, eod as edit_delete, callback
from xteam.vcbot.markups import timer_task
from xteam.vcbot import (
    gen_thumb,
    telegram_markup_timer,
    ytdl,
    ytsearch,
    get_play_text,
    get_play_queue,
    MUSIC_BUTTONS,
    join_call,
    AssistantAdd,
    cleanup_file,
    get_playlist_ids,
play_logs
)
from xteam.vcbot.queues import QUEUE, add_to_queue, clear_queue, get_queue, pop_an_item

logger = logging.getLogger(__name__)
active_messages = {}

def vcmention(user):
    full_name = getattr(user, 'first_name', 'User')
    if not hasattr(user, 'id'):
        return full_name
    return f'<a href="tg://user?id={user.id}">{full_name}</a>'

async def skip_current_song(chat_id):
    if chat_id not in QUEUE:
        return 0
    if chat_id in active_messages:
        try:
            await asst.delete_messages(chat_id, active_messages[chat_id])
            del active_messages[chat_id]
        except Exception:
            pass
    pop_an_item(chat_id)
    if len(QUEUE.get(chat_id, [])) > 0:
        next_song = QUEUE[chat_id][0]
        songname, url, duration, thumb_url, videoid, artist, requester, is_video = next_song
        try:
            stream_link_info = await ytdl(url, video_mode=is_video) 
            ytlink = stream_link_info[1] if isinstance(stream_link_info, tuple) else stream_link_info
            await join_call(chat_id, link=ytlink, video=is_video)
            return next_song
        except Exception:
            return await skip_current_song(chat_id)
    else:
        return 1

@asst_cmd(pattern="Play( (.*)|$)")
@AssistantAdd
async def vc_play_bot(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    if (replied and not replied.audio and not replied.voice and not title or not replied and not title):
        return await edit_delete(event, "**Please enter song title!**")
    status_msg = await edit_or_reply(event, "🔍")
    query = title if title else replied.message
    search = ytsearch(query)
    if search == 0:
        return await status_msg.edit("**Song not found.**")
    songname, url, duration, thumbnail, videoid, artist = search
    thumb = await gen_thumb(videoid)
    stream_link_info = await ytdl(url, video_mode=False) 
    ytlink = stream_link_info[1] if isinstance(stream_link_info, tuple) else stream_link_info
    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
        caption = get_play_queue(songname, artist, duration, from_user)
        await status_msg.delete()
        return await event.client.send_file(chat_id, thumb, caption=caption, buttons=MUSIC_BUTTONS)
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
            await join_call(chat_id, link=ytlink, video=False)
            await status_msg.delete()
            caption = get_play_text(songname, artist, duration, from_user)
            msg = await event.client.send_file(chat_id, thumb, caption=caption, buttons=telegram_markup_timer("00:00", duration))
            active_messages[chat_id] = msg.id
            asyncio.create_task(timer_task(event.client, chat_id, msg.id, duration))
        except Exception as e:
            clear_queue(chat_id)
            await status_msg.edit(f"**ERROR:** `{e}`")

@asst_cmd(pattern="Vplay( (.*)|$)")
@AssistantAdd
async def vc_vplay_bot(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    status_msg = await edit_or_reply(event, "🔍")
    query = title if title else (replied.message if replied else None)
    if not query: return await status_msg.edit("**Give the video a title!**")
    search = ytsearch(query)
    if search == 0: return await status_msg.edit("**Video not found!**")
    songname, url, duration, thumbnail, videoid, artist = search
    thumb = await gen_thumb(videoid)
    stream_link_info = await ytdl(url, video_mode=True) 
    ytlink = stream_link_info[1] if isinstance(stream_link_info, tuple) else stream_link_info
    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
        caption = get_play_queue(songname, artist, duration, from_user)
        await status_msg.delete()
        return await event.client.send_file(chat_id, thumb, caption=caption, buttons=MUSIC_BUTTONS)
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
            await join_call(chat_id, link=ytlink, video=True)
            await status_msg.delete()
            caption = get_play_text(songname, artist, duration, from_user)
            msg = await event.client.send_file(chat_id, thumb, caption=caption, buttons=telegram_markup_timer("00:00", duration))
            active_messages[chat_id] = msg.id
            asyncio.create_task(timer_task(event.client, chat_id, msg.id, duration))
        except Exception as e:
            clear_queue(chat_id); await status_msg.edit(f"**ERROR:** `{e}`")



@man_cmd(pattern="play( (.*)|$)")
@AssistantAdd
async def vc_play_user(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    status_msg = await edit_or_reply(event, "⏳ **Processing...**")
    search = ytsearch(title if title else (replied.message if replied else ""))
    if search == 0: return await status_msg.edit("**Result Not Found!**")
    sn, url, du, th, vi, ar = search
    songname = f"{ar} - {sn}"
    ok, ytlink = await ytdl(url, False)
    if not ok: return await status_msg.edit(f"**Error:** `{ytlink}`")
    
    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, du, None, None, ar, from_user, False)
        await status_msg.delete()
        return await event.client.send_message(chat_id, f"<blockquote><b>🎧 Added to Queue</b>\n{songname}</blockquote>", buttons=MUSIC_BUTTONS, parse_mode='html')
    else:
        try:
            add_to_queue(chat_id, songname, url, du, None, None, ar, from_user, False)
            success = await join_call(chat_id, ytlink, False)
            
            if success:
                await status_msg.delete()
                msg = await event.client.send_message(chat_id, f"<blockquote><b>🎵 Now Playing</b>\n{songname}</blockquote>", buttons=telegram_markup_timer("00:00", du), parse_mode='html')
                active_messages[chat_id] = msg.id
                asyncio.create_task(timer_task(event.client, chat_id, msg.id, du))
                await play_logs(event, songname, du, "Audio")
                
        except Exception as e: await status_msg.edit(f"**Error:** `{e}`")

@man_cmd(pattern="vplay( (.*)|$)")
@AssistantAdd
async def vc_vplay_user(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    status_msg = await edit_or_reply(event, "⏳ **Processing Video...**")
    search = ytsearch(title if title else (replied.message if replied else ""))
    if search == 0: return await status_msg.edit("**Video Not Found!**")
    sn, url, du, th, vi, ar = search
    ok, ytlink = await ytdl(url, True)
    if not ok: return await status_msg.edit(f"**Error:** `{ytlink}`")
    
    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, sn, url, du, None, None, ar, from_user, True)
        await status_msg.delete()
        return await event.client.send_message(chat_id, f"<blockquote><b>📽 Video Added to Queue</b>\n{sn}</blockquote>", buttons=MUSIC_BUTTONS, parse_mode='html')
    else:
        try:
            add_to_queue(chat_id, sn, url, du, None, None, ar, from_user, True)
            success = await join_call(chat_id, ytlink, True)
            
            if success:
                await status_msg.delete()
                msg = await event.client.send_message(chat_id, f"<blockquote><b>🎬 Now Streaming Video</b>\n{sn}</blockquote>", buttons=telegram_markup_timer("00:00", du), parse_mode='html')
                active_messages[chat_id] = msg.id
                asyncio.create_task(timer_task(event.client, chat_id, msg.id, du))
                await play_logs(event, sn, du, "Video")
                
        except Exception as e: await status_msg.edit(f"**Error:** `{e}`")
    

async def skip(event):
    chat_id = event.chat_id
    op = await skip_current_song(chat_id)
    
    if op == 0: 
        return await edit_delete(event, "<blockquote>No active streams.</blockquote>", parse_mode='html')
    
    if op == 1: 
        return await edit_delete(event, "<blockquote>The queue is finished.</blockquote>", parse_mode='html')
    
    try:
        title = op[0]
        artist = op[6]
        duration = op[2]
        songname = f"{artist} - {title}" if artist else title

        text = (
            "<blockquote>"
            "🎵 Now Playing\n"
            f"{songname}"
            "</blockquote>"
        )

        msg = await event.client.send_message(
            chat_id, 
            message=text, 
            buttons=telegram_markup_timer("00:00", duration), 
            parse_mode='html'
        )
        
        active_messages[chat_id] = msg.id
        asyncio.create_task(timer_task(event.client, chat_id, msg.id, duration))

    except Exception as e:
        await event.respond(f"Error: <code>{e}</code>", parse_mode='html')
    

async def pause(event):
    chat_id = event.chat_id
    try:
        await call_py.pause(chat_id); await edit_or_reply(event, "**⏸ Streaming Dijeda**")
    except: await edit_delete(event, "**Tidak ada streaming aktif.**")

async def resume(event):
    chat_id = event.chat_id
    try:
        await call_py.resume(chat_id); await edit_or_reply(event, "**▶️ Streaming Dilanjutkan**")
    except: await edit_delete(event, "**Tidak ada streaming aktif.**")

async def playlist(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if not chat_queue: return await edit_delete(event, "**Antrean Kosong**")
        text = f"**🎧 Sedang Memutar:**\n**• {chat_queue[0][0]}**\n\n**• Daftar Putar:**"
        for x in range(1, len(chat_queue)): text += f"\n**#{x}** - {chat_queue[x][0]}"
        await edit_or_reply(event, text)
    else: await edit_delete(event, "**Tidak ada streaming aktif.**")

async def end(event):
    chat_id = event.chat_id
    try:
        await call_py.leave_call(chat_id)
        clear_queue(chat_id)
        if chat_id in active_messages:
            del active_messages[chat_id]
        await edit_or_reply(event, "✅ **sᴛʀᴇᴀᴍɪɴɢ sᴛᴏᴘᴘᴇᴅ!!**")
    except Exception as e:
        await edit_delete(event, f"**ᴇʀʀᴏʀ:** `{e}`", 5)

@man_cmd(pattern="(end|stop)$", group_only=True)
async def vc_end(e):
    await end(e)

@asst_cmd(pattern="^(end|stop)")
async def vc_end(e):
    if e.text.startswith('/'):
        await end(e)

@man_cmd(pattern="skip$", group_only=True)
async def vc_skip(e):
    await skip(e)

@asst_cmd(pattern="^skip")
async def vc_skip(e):
    if e.text.startswith('/'):
        await skip(e)

@man_cmd(pattern="pause$", group_only=True)
async def vc_pause(e):
    await pause(e)

@asst_cmd(pattern="^pause")
async def vc_pause(e):
    if e.text.startswith('/'):
        await pause(e)

@man_cmd(pattern="resume$", group_only=True)
async def vc_resume(e):
    await resume(e)

@asst_cmd(pattern="^resume")
async def vc_resume(e):
    if e.text.startswith('/'):
        await resume(e)

@man_cmd(pattern="playlist$", group_only=True)
async def vc_playlist(e):
    await playlist(e)

@asst_cmd(pattern="^playlist")
async def vc_playlist(e):
    if e.text.startswith('/'):
        await playlist(e)

@man_cmd(pattern=r"volume(?: |$)(.*)", group_only=True)
async def vc_volume(event):
    query = event.pattern_match.group(1)
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            vol = int(query)
            await call_py.change_volume_call(chat_id, volume=vol)
            await edit_or_reply(event, f"**Volume diatur ke** `{vol}%`")
        except: await edit_delete(event, "**Masukkan angka 0-100.**")

@call_py.on_update()
async def unified_update_handler(client, update):
    chat_id = getattr(update, "chat_id", None)
    if not chat_id: return
    if isinstance(update, StreamEnded):
        if chat_id in active_messages:
            try: await asst.delete_messages(chat_id, active_messages[chat_id]); del active_messages[chat_id]
            except: pass
        if chat_id in QUEUE and len(QUEUE[chat_id]) > 1:
            data = await skip_current_song(chat_id)
            if data and data != 1:
                msg = await asst.send_message(chat_id, message=f"<blockquote><b>Now Playing</b>\n{data[0]}</blockquote>", buttons=telegram_markup_timer("00:00", data[2]), parse_mode='html')
                active_messages[chat_id] = msg.id
                asyncio.create_task(timer_task(asst, chat_id, msg.id, data[2]))
        else:
            try: await call_py.leave_call(chat_id)
            except: pass
            if chat_id in QUEUE: clear_queue(chat_id)
           
