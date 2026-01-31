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
    join_call,
AssistantAdd,
cleanup_file,
get_playlist_ids
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
        
        
@asst_cmd(pattern="Play( (.*)|$)")
@AssistantAdd
async def vc_play(event):
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


@asst_cmd(pattern="Vplay( (.*)|$)")
@AssistantAdd
async def vc_vplay(event):
    title = event.pattern_match.group(2)
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



@man_cmd(pattern="play( (.*)|$)")
@AssistantAdd
async def vc_play(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    status_msg = await edit_or_reply(event, "⏳ **Processing...**")
    added_songs = []
   
    if title and ("youtube.com/playlist" in title or "&list=" in title):
        await status_msg.edit("📂 **Processing Playlist...**")
        ids = await get_playlist_ids(title, limit=20)
        if not ids: 
            return await status_msg.edit("**Playlist Failed or Empty!**")
        
        for index, v_id in enumerate(ids):
            url = f"https://www.youtube.com/watch?v={v_id}"
            search = ytsearch(url)
            if search != 0:
                _sn, _u, _du, _th, _vi, _ar = search
                songname = f"{_ar} - {_sn}"
                add_to_queue(chat_id, songname, _u, _du, _th, _vi, _ar, from_user, False)
                added_songs.append(songname)
                
                if index == 0 and chat_id not in active_messages:
                    ok, ytlink = await ytdl(_u, False)
                    if ok:
                        await join_call(chat_id, ytlink, False)
                        asyncio.create_task(cleanup_file(ytlink, 1800))
                
                if index % 5 == 0:
                    await status_msg.edit(f"**Processing:** {index+1}/{len(ids)} songs...")
        
        list_text = "\n".join([f"{i+1}. {song}" for i, song in enumerate(added_songs[:10])])
        return await status_msg.edit(f"<blockquote><b>✅ Playlist Added ({len(added_songs)} songs)</b>\n\n{list_text}\n...dst</blockquote>", parse_mode='html')

    if replied and (replied.audio or replied.voice or replied.video or replied.document):
        path = await replied.download_media()
        songname = f"{getattr(replied.file, 'performer', 'Artist')} - {getattr(replied.file, 'title', 'Music')}"
        ytlink, duration, url, artist = path, getattr(replied.file, 'duration', 0), "telegram", "Local"
    
    elif title:
        search = ytsearch(title)
        if search == 0: 
            return await status_msg.edit("**Result Not Found!**")
        
        _sn, url, duration, thumbnail, videoid, artist = search
        songname = f"{artist} - {_sn}"
        
        await status_msg.edit(f"📥 **Downloading:**\n`{songname}`")
        ok, ytlink = await ytdl(url, False)
        if not ok: 
            return await status_msg.edit(f"**Error Download:** `{ytlink}`")
    else:
        return await status_msg.edit("**Provide a title, YouTube link, or reply to media!**")

    if ytlink and os.path.exists(ytlink): 
        asyncio.create_task(cleanup_file(ytlink, 1800))

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, songname, url, duration, None, None, artist, from_user, False)
        await status_msg.delete()
        return await event.client.send_message(chat_id, f"<blockquote><b>🎧 Added to Queue</b>\n{songname}</blockquote>", buttons=MUSIC_BUTTONS, parse_mode='html')
    else:
        try:
            add_to_queue(chat_id, songname, url, duration, None, None, artist, from_user, False)
            await asyncio.sleep(1.5)
            await join_call(chat_id, ytlink, False)
            await status_msg.delete()
            
            msg = await event.client.send_message(
                chat_id, 
                f"<blockquote><b>🎵 Now Playing</b>\n{songname}</blockquote>", 
                buttons=telegram_markup_timer("00:00", duration), 
                parse_mode='html'
            )
            active_messages[chat_id] = msg.id
            asyncio.create_task(timer_task(event.client, chat_id, msg.id, duration))
        except Exception as e:
            if ytlink and os.path.exists(ytlink): 
                os.remove(ytlink)
            await status_msg.edit(f"**Error:** `{e}`")



@man_cmd(pattern="vplay( (.*)|$)")
@AssistantAdd
async def vc_vplay(event):
    title = event.pattern_match.group(2)
    replied = await event.get_reply_message()
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    status_msg = await edit_or_reply(event, "⏳ **ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ...**")
    added_vids = []
    
    if title and ("youtube.com/playlist" in title or "&list=" in title):
        await status_msg.edit("📂 **ᴘʀᴏᴄᴇssɪɴɢ ᴠɪᴅᴇᴏ ᴘʟᴀʏʟɪsᴛ...**")
        ids = await get_playlist_ids(title, limit=15)
        if not ids: 
            return await status_msg.edit("**ᴘʟᴀʏʟɪsᴛ ɴᴏᴛ ғᴏᴜɴᴅ ᴏʀ ᴇᴍᴘᴛʏ!**")
        
        for index, v_id in enumerate(ids):
            url = f"https://www.youtube.com/watch?v={v_id}"
            search = ytsearch(url)
            if search != 0:
                _sn, _u, _du, _th, _vi, _ar = search
                add_to_queue(chat_id, _sn, _u, _du, _th, _vi, _ar, from_user, True)
                added_vids.append(_sn)
                
                if index == 0 and chat_id not in active_messages:
                    ok, ytlink = await ytdl(_u, True)
                    if ok:
                        await join_call(chat_id, ytlink, True)
                        asyncio.create_task(cleanup_file(ytlink, 1800))

                if (index + 1) % 3 == 0:
                    await status_msg.edit(f"📽 **ᴘʀᴏᴄᴇssɪɴɢ:** {index+1}/{len(ids)} ᴠɪᴅᴇᴏs...")
        
        list_text = "\n".join([f"{i+1}. {vid}" for i, vid in enumerate(added_vids[:10])])
        return await status_msg.edit(f"<blockquote><b>✅ ᴠɪᴅᴇᴏ ᴘʟᴀʏʟɪsᴛ ᴀᴅᴅᴇᴅ ({len(added_vids)})</b>\n\n{list_text}\n...ᴅsᴛ</blockquote>", parse_mode='html')

    query = title if title else (replied.message if replied and replied.message else None)
    if not query:
        return await status_msg.edit("**ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠɪᴅᴇᴏ ᴛɪᴛʟᴇ ᴏʀ ʟɪɴᴋ!**")

    search = ytsearch(query)
    if search == 0: 
        return await status_msg.edit("**ᴠɪᴅᴇᴏ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
    sn, url, du, th, vi, ar = search
    
    await status_msg.edit(f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ")
    ok, ytlink = await ytdl(url, True)
    if not ok: 
        return await status_msg.edit(f"**ᴅᴏᴡɴʟᴏᴀᴅ ᴇʀʀᴏʀ:** `{ytlink}`")

    if ytlink and os.path.exists(ytlink): 
        asyncio.create_task(cleanup_file(ytlink, 1800))

    if chat_id in QUEUE and len(QUEUE[chat_id]) > 0:
        add_to_queue(chat_id, sn, url, du, th, vi, ar, from_user, True)
        await status_msg.delete()
        return await event.client.send_message(
            chat_id, 
            f"<blockquote><b>📽 ᴀᴅᴅᴇᴅ ᴛᴏ ᴠɪᴅᴇᴏ ǫᴜᴇᴜᴇ</b>\n{sn}</blockquote>", 
            buttons=MUSIC_BUTTONS, 
            parse_mode='html'
        )
    else:
        try:
            add_to_queue(chat_id, sn, url, du, th, vi, ar, from_user, True)
            await asyncio.sleep(1.5)
            await join_call(chat_id, ytlink, True)
            await status_msg.delete()
            
            msg = await event.client.send_message(
                chat_id, 
                f"<blockquote><b>🎬 ɴᴏᴡ ᴘʟᴀʏɪɴɢ ᴠɪᴅᴇᴏ</b>\n{sn}</blockquote>", 
                buttons=telegram_markup_timer("00:00", du), 
                parse_mode='html'
            )
            active_messages[chat_id] = msg.id
            asyncio.create_task(timer_task(event.client, chat_id, msg.id, du))
        except Exception as e:
            if ytlink and os.path.exists(ytlink): 
                os.remove(ytlink)
            await status_msg.edit(f"**ᴇʀʀᴏʀ:** `{e}`")

             
async def vc_end(event):
    chat_id = event.chat_id
    try:
        await call_py.leave_call(chat_id)
        clear_queue(chat_id)
        if chat_id in active_messages:
            del active_messages[chat_id]
        await edit_or_reply(event, "✅ **sᴛʀᴇᴀᴍɪɴɢ sᴛᴏᴘᴘᴇᴅ!!**")
    except Exception as e:
        await edit_delete(event, f"**ᴇʀʀᴏʀ:** `{e}`", 5)

async def skip(event):
    chat_id = event.chat_id
    op = await skip_current_song(chat_id)
    if op == 0:
        await edit_delete(event, "**Tidak ada streaming aktif.**")
    elif op == 1:
        await edit_delete(event, "**Antrean habis.**")
    else:
        thumb = await gen_thumb(op[4])
        cap = get_play_text(op[0], op[5], op[2], op[6])
        msg = await event.client.send_file(
            chat_id, thumb, 
            caption=f"**⏭ Skip Berhasil**\n{cap}", 
            buttons=telegram_markup_timer("00:00", op[2])
        )
        active_messages[chat_id] = msg.id
        asyncio.create_task(timer_task(event.client, chat_id, msg.id, op[2]))

async def pause(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.pause(chat_id)
            await edit_or_reply(event, "**⏸ Streaming Dijeda**")
        except Exception as e:
            await edit_delete(event, f"**ERROR:** `{e}`")
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")

async def resume(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.resume(chat_id)
            await edit_or_reply(event, "**▶️ Streaming Dilanjutkan**")
        except Exception as e:
            await edit_or_reply(event, f"**ERROR:** `{e}`")
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")

async def playlist(event):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if not chat_queue:
            return await edit_delete(event, "**Tidak Ada Lagu Dalam Antrian**", time=10)
        PLAYLIST = f"**🎧 Sedang Memutar:**\n**• [{chat_queue[0][0]}]({chat_queue[0][2]})** | `{chat_queue[0][3]}` \n\n**• Daftar Putar:**"
        l = len(chat_queue)
        for x in range(1, l): 
            PLAYLIST += f"\n**#{x}** - [{chat_queue[x][0]}]({chat_queue[x][2]}) | `{chat_queue[x][3]}`"
        await edit_or_reply(event, PLAYLIST, link_preview=False)
    else:
        await edit_delete(event, "**Tidak Sedang Memutar Streaming**")


@man_cmd(pattern="(end|stop)$", group_only=True)
async def vc_end_m(e):
    await vc_end(e)

@asst_cmd(pattern="^(end|stop)")
async def vc_end_a(e):
    if e.text.startswith('/'):
        await vc_end(e)

@man_cmd(pattern="skip$", group_only=True)
async def vc_skip_m(e):
    await skip(e)

@asst_cmd(pattern="^skip")
async def vc_skip_a(e):
    if e.text.startswith('/'):
        await skip(e)

@man_cmd(pattern="pause$", group_only=True)
async def vc_pause_m(e):
    await pause(e)

@asst_cmd(pattern="^pause")
async def vc_pause_a(e):
    if e.text.startswith('/'):
        await pause(e)

@man_cmd(pattern="resume$", group_only=True)
async def vc_resume_m(e):
    await resume(e)

@asst_cmd(pattern="^resume")
async def vc_resume_a(e):
    if e.text.startswith('/'):
        await resume(e)

@man_cmd(pattern="playlist$", group_only=True)
async def vc_playlist_m(e):
    await playlist(e)

@asst_cmd(pattern="^playlist")
async def vc_playlist_a(e):
    if e.text.startswith('/'):
        await playlist(e)

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
                msg = await event.client.send_file(chat_id, caption=f"{caption}", buttons=telegram_markup_timer("00:00", duration))
                active_messages[chat_id] = msg.id
                
                asyncio.create_task(timer_task(client, chat_id, msg.id, duration))
        else:
            try:
                await call_py.leave_call(chat_id)
            except: pass
            clear_queue(chat_id)
            
