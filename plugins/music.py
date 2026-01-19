# xteam-urbot
# Copyright (C) 2021-2026 xteam_cloner
# This file is a part of < https://github.com/xteam-cloner/xteam-urbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/xteam-cloner/xteam-urbot/blob/main/LICENSE/>.

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
   
• `{i}end`
   Stop Stream 

"""

from __future__ import annotations
import asyncio
import os
import re
import contextlib 
import logging
import functools
import yt_dlp
from . import *
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import httpx
from telethon import events, TelegramClient, Button
from telethon.tl.types import Message, User, TypeUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import (
    UserPrivacyRestrictedError, 
    ChatAdminRequiredError, 
    UserAlreadyParticipantError
)
from xteam.configs import Var 
from xteam import call_py, asst
from telethon.utils import get_display_name
from xteam.fns.admins import admin_check 
from pytgcalls import PyTgCalls, filters as fl
from pytgcalls import filters as fl
from ntgcalls import TelegramServerError
from pytgcalls.exceptions import NoActiveGroupCall, NoAudioSourceFound, NoVideoSourceFound
from pytgcalls.types import (
    Update,
    ChatUpdate,
    MediaStream,
    StreamEnded,
    GroupCallConfig,
    GroupCallParticipant,
    UpdatedGroupCallParticipant,
)
from pytgcalls.types.stream import VideoQuality, AudioQuality
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import (
    UserNotParticipantError,
    UserAlreadyParticipantError
)
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from youtubesearchpython.__future__ import VideosSearch
from . import ultroid_bot, ultroid_cmd as man_cmd, eor as edit_or_reply, eod as edit_delete, callback
from youtubesearchpython import VideosSearch
from xteam import LOGS
from xteam.vcbot.markups import timer_task
from xteam.vcbot import (
    CHAT_TITLE,
    gen_thumb,
    telegram_markup_timer,
    skip_item,
    ytdl,
    ytsearch,
    get_play_text,
    get_play_queue,
MUSIC_BUTTONS,
    join_call
)
from xteam.vcbot.queues import QUEUE, add_to_queue, clear_queue, get_queue, pop_an_item

logger = logging.getLogger(__name__)

active_messages = {}

def vcmention(user):
    full_name = get_display_name(user)
    if not isinstance(user, types.User):
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
    if len(QUEUE[chat_id]) > 0:
        next_song = QUEUE[chat_id][0]
        songname, url, duration, thumb_url, videoid, artist, requester, is_video = next_song
        
        try:
            stream_link_info = await ytdl(url, video_mode=is_video) 
            hm, ytlink = stream_link_info if isinstance(stream_link_info, tuple) else (1, stream_link_info)
            
            await join_call(chat_id, link=ytlink, video=is_video)
            
            return next_song
        except Exception:
            return await skip_current_song(chat_id)
    else:
        return 1
        
        
@man_cmd(pattern="Play(?:\s|$)([\s\S]*)", group_only=True)
async def vc_play(event):
    title = event.pattern_match.group(1)
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
    hm, ytlink = stream_link_info if isinstance(stream_link_info, tuple) else (1, stream_link_info)
    
    if hm == 0:
        return await status_msg.edit(f"**Error:** `{ytlink}`")

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
        final_caption = f"{get_play_queue(songname, artist, duration, from_user)}"
        await status_msg.delete()
        return await event.client.send_file(chat_id, thumb, caption=final_caption, buttons=MUSIC_BUTTONS)
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
            await join_call(chat_id, link=ytlink, video=False)
            await status_msg.delete()
            
            caption_text = get_play_text(songname, artist, duration, from_user)
            pesan_audio = await event.client.send_file(chat_id, thumb, caption=caption_text, buttons=telegram_markup_timer("00:00", duration))
            
            active_messages[chat_id] = pesan_audio.id
            asyncio.create_task(timer_task(event.client, chat_id, pesan_audio.id, duration))
        except Exception as e:
            clear_queue(chat_id)
            await status_msg.edit(f"**ERROR:** `{e}`")


@man_cmd(pattern="Vplay(?:\s|$)([\s\S]*)", group_only=True)
async def vc_vplay(event):
    title = event.pattern_match.group(1)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    
    status_msg = await edit_or_reply(event, "🔍")
    query = title if title else (replied.message if replied else None)
    if not query:
        return await status_msg.edit("**Give the video a title!**")
        
    search = ytsearch(query)
    if search == 0:
        return await status_msg.edit("**Video not found!**")
        
    songname, url, duration, thumbnail, videoid, artist = search
    thumb = await gen_thumb(videoid)
    stream_link_info = await ytdl(url, video_mode=True) 
    hm, ytlink = stream_link_info if isinstance(stream_link_info, tuple) else (1, stream_link_info)
    
    if hm == 0:
        return await status_msg.edit(f"**Error:** `{ytlink}`")

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        pos = add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
        caption = f"{get_play_queue(songname, artist, duration, from_user)}"
        await status_msg.delete()
        return await event.client.send_file(chat_id, thumb, caption=caption, buttons=MUSIC_BUTTONS)
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
            await join_call(chat_id, link=ytlink, video=True)
            await status_msg.delete()
            
            caption = f"{get_play_text(songname, artist, duration, from_user)}"
            pesan_video = await event.client.send_file(chat_id, thumb, caption=caption, buttons=telegram_markup_timer("00:00", duration))
            
            active_messages[chat_id] = pesan_video.id
            asyncio.create_task(timer_task(event.client, chat_id, pesan_video.id, duration))
        except Exception as e:
            clear_queue(chat_id)
            await status_msg.edit(f"**ERROR:** `{e}`")


@man_cmd(pattern="play(?:\s|$)([\s\S]*)", group_only=True)
async def vc_play(event):
    title = event.pattern_match.group(1)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    
    status_msg = await edit_or_reply(event, "⏳ **Processing...**")
    
    if replied and (replied.audio or replied.voice or replied.video or replied.document):
        if replied.file.size > 100 * 1024 * 1024:
            return await status_msg.edit("**File too large!** Maximum limit is 100MB.")
            
        await status_msg.edit("📥 **Downloading media...**")
        path = await replied.download_media()
        
        _title = getattr(replied.file, 'title', "Telegram Music") or "Telegram Music"
        _artist = getattr(replied.file, 'performer', "Unknown Artist") or "Unknown Artist"
        
        songname = f"{_artist} - {_title}"
        artist = _artist
        duration = getattr(replied.file, 'duration', 0)
        ytlink = path 
        url = "https://t.me/c/telegram"
        thumbnail = None
        videoid = "local_file"

    elif title or (replied and replied.message):
        query = title if title else replied.message
        await status_msg.edit(f"🔍 **Searching:** `{query}`...")
        
        search = ytsearch(query)
        if search == 0:
            return await status_msg.edit("**Song not found.**")
            
        _songname, url, duration, thumbnail, videoid, _artist = search
        
        songname = f"{_artist} - {_songname}"
        artist = _artist
        
        stream_link_info = await ytdl(url, video_mode=False) 
        hm, ytlink = stream_link_info if isinstance(stream_link_info, tuple) else (1, stream_link_info)
        
        if hm == 0:
            return await status_msg.edit(f"**Error:** `{ytlink}`")
            
    else:
        return await status_msg.edit("**Please provide a song title or reply to an audio file!**")

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
        final_caption = (
            f"<blockquote><b>🎧 Added to Queue</b>\n\n"
            f"<b>Title:</b> {songname}\n"
            f"<b>Requester:</b> {from_user}</blockquote>"
        )
        await status_msg.delete()
        return await event.client.send_message(chat_id, final_caption, buttons=MUSIC_BUTTONS, parse_mode='html')
    
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, False)
            await join_call(chat_id, link=ytlink, video=False)
            await status_msg.delete()
            
            caption_text = (
                f"<blockquote><b>🎵 Now Playing</b>\n\n"
                f"<b>Title:</b> {songname}\n"
                f"<b>Duration:</b> {duration}\n"
                f"<b>Requester:</b> {from_user}</blockquote>"
            )
            
            pesan_audio = await event.client.send_message(
                chat_id, 
                caption_text, 
                buttons=telegram_markup_timer("00:00", duration), 
                parse_mode='html'
            )
            
            active_messages[chat_id] = pesan_audio.id
            asyncio.create_task(timer_task(event.client, chat_id, pesan_audio.id, duration))
            
        except Exception as e:
            clear_queue(chat_id)
            if os.path.exists(ytlink) and not ytlink.startswith("http"):
                os.remove(ytlink)
            await status_msg.edit(f"**ERROR:** `{e}`")


@man_cmd(pattern="vplay(?:\s|$)([\s\S]*)", group_only=True)
async def vc_vplay(event):
    title = event.pattern_match.group(1)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    
    status_msg = await edit_or_reply(event, "🔍")
    query = title if title else (replied.message if replied else None)
    if not query:
        return await status_msg.edit("**Give the video a title!**")
        
    search = ytsearch(query)
    if search == 0:
        return await status_msg.edit("**Video not found!**")
        
    songname, url, duration, thumbnail, videoid, artist = search
    stream_link_info = await ytdl(url, video_mode=True) 
    hm, ytlink = stream_link_info if isinstance(stream_link_info, tuple) else (1, stream_link_info)
    
    if hm == 0:
        return await status_msg.edit(f"**Error:** `{ytlink}`")

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        pos = add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
        caption = f"<blockquote><b>📽 Video Added to Queue</b>\n\n<b>Title:</b> {songname}\n<b>Artist:</b> {artist}\n<b>Requester:</b> {from_user}</blockquote>"
        await status_msg.delete()
        return await event.client.send_message(chat_id, caption, buttons=MUSIC_BUTTONS, parse_mode='html')
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, thumbnail, videoid, artist, from_user, True)
            await join_call(chat_id, link=ytlink, video=True)
            await status_msg.delete()
            
            caption = f"<blockquote><b>🎬 Now Playing Video</b>\n\n<b>Title:</b> {songname}\n<b>Artist:</b> {artist}\n<b>Duration:</b> {duration}\n<b>Requester:</b> {from_user}</blockquote>"
            pesan_video = await event.client.send_message(chat_id, caption, buttons=telegram_markup_timer("00:00", duration), parse_mode='html')
            
            active_messages[chat_id] = pesan_video.id
            asyncio.create_task(timer_task(event.client, chat_id, pesan_video.id, duration))
        except Exception as e:
            clear_queue(chat_id)
            await status_msg.edit(f"**ERROR:** `{e}`")
   
            
@man_cmd(pattern="end$", group_only=True)
async def vc_end(event):
    chat_id = event.chat_id
    try:
        await call_py.leave_call(chat_id)
        clear_queue(chat_id)
        await edit_or_reply(event, "**Streaming Stop!!**")
    except Exception as e:
        await edit_delete(event, f"**ERROR:** `{e}`")
        

@man_cmd(pattern="skip$", group_only=True)
async def vc_skip(event):
    chat_id = event.chat_id
    op = await skip_current_song(chat_id)
    if op == 0:
        await edit_delete(event, "**Tidak ada streaming aktif.**")
    elif op == 1:
        await edit_delete(event, "**Antrean habis.**")
    else:
        thumb = await gen_thumb(op[4])
        cap = get_play_text(op[0], op[5], op[2], op[6])
        msg = await event.client.send_file(chat_id, thumb, caption=f"**⏭ Skip Berhasil**\n{cap}", buttons=telegram_markup_timer("00:00", op[2]))
        active_messages[chat_id] = msg.id
        
        # AKTIFKAN TIMER DI SINI
        asyncio.create_task(timer_task(event.client, chat_id, msg.id, op[2]))

@man_cmd(pattern="pause$", group_only=True)
async def vc_pause(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.pause(chat_id)
            await edit_or_reply(event, "**Streaming Dijeda**")
        except Exception as e:
            await edit_delete(event, f"**ERROR:** `{e}`")
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")


@man_cmd(pattern="resume$", group_only=True)
async def vc_resume(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.resume(chat_id)
            await edit_or_reply(event, "**Streaming Dilanjutkan**")
        except Exception as e:
            await edit_or_reply(event, f"**ERROR:** `{e}`")
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")


@man_cmd(pattern=r"volume(?: |$)(.*)", group_only=True)
async def vc_volume(event):
    query = event.pattern_match.group(1)
    me = await event.client.get_me()
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    chat_id = event.chat_id
    
    if not admin and not creator:
        if not await admin_check(event):
             return await edit_delete(event, f"**Maaf {me.first_name} Bukan Admin 👮**", 30)

    if chat_id in QUEUE:
        try:
            volume_level = int(query)
            if not 0 <= volume_level <= 100:
                return await edit_delete(event, "**Volume harus antara 0 dan 100.**", 10)
            await call_py.change_volume_call(chat_id, volume=volume_level)
            await edit_or_reply(
                event, f"**Berhasil Mengubah Volume Menjadi** `{volume_level}%`"
            )
        except ValueError:
             await edit_delete(event, "**Mohon masukkan angka yang valid untuk volume.**", 10)
        except Exception as e:
            await edit_delete(event, f"**ERROR:** `{e}`", 30)
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")


@man_cmd(pattern="playlist$", group_only=True)
async def vc_playlist(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if not chat_queue:
            return await edit_delete(event, "**Tidak Ada Lagu Dalam Antrian**", time=10)

        PLAYLIST = f"**🎧 Sedang Memutar:**\n**• [{chat_queue[0][0]}]({chat_queue[0][2]})** | `{chat_queue[0][3]}` \n\n**• Daftar Putar:**"
        
        l = len(chat_queue)
        for x in range(1, l): 
            hmm = chat_queue[x][0]
            hmmm = chat_queue[x][2]
            hmmmm = chat_queue[x][3]
            PLAYLIST = PLAYLIST + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`"
            
        await edit_or_reply(event, PLAYLIST, link_preview=False)
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")


@call_py.on_update()
async def unified_update_handler(client, update: Update):
    chat_id = getattr(update, "chat_id", None)
    if isinstance(update, StreamEnded):
        if chat_id in active_messages:
            try:
                await asst.delete_messages(chat_id, active_messages[chat_id])
                del active_messages[chat_id]
            except: pass
            
        if chat_id in QUEUE and len(QUEUE[chat_id]) > 1:
            data = await skip_current_song(chat_id)
            if data and data != 1:
                songname, url, duration, thumb_url, videoid, artist, requester = data
                thumb = await gen_thumb(videoid)
                caption = get_play_text(songname, artist, duration, requester)
                
                # Kirim pesan dengan tombol timer
                msg = await event.client.send_file(chat_id, thumb, caption=f"{caption}", buttons=telegram_markup_timer("00:00", duration))
                active_messages[chat_id] = msg.id
                
                asyncio.create_task(timer_task(client, chat_id, msg.id, duration))
        else:
            try:
                await call_py.leave_call(chat_id)
            except: pass
            clear_queue(chat_id)
            
