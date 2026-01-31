# xteam-urbot 
# Copyright (C) 2024-2025 xteamdev

"""
✘ Help for YouTube

๏ Command: video
◉ Description: Download Videos from YouTube.

๏ Command: song
◉ Description: Download Songs from YouTube.
"""

import os
from asyncio import get_event_loop
from functools import partial
from urllib.parse import urlparse

import wget
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from . import *


def run_sync(func, *args, **kwargs):
    return get_event_loop().run_in_executor(None, partial(func, *args, **kwargs))


@ultroid_cmd(pattern="video( (.*)|$)")
async def yt_video(e):
    infomsg = await e.eor("`Processing...`")
    try:
        raw_query = str(e.text.split(None, 1)[1])
        cleaned_query = raw_query.split('?')[0] 

        search = (
            SearchVideos(
                cleaned_query, offset=1, mode="dict", max_results=1
            )
            .result()
            .get("search_result")
        )
        link = f"https://youtu.be/{search[0]['id']}"
    except Exception as error:
        return await infomsg.edit(f"**Pencarian...\n\n❌ Error: {error}**")
        
    ydl = YoutubeDL(
        {
            "quiet": True,
            "no_warnings": True,
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "nocheckcertificate": True,
            "geo_bypass": True,
            "cookiefile": "cookies.txt",
            "merge_output_format": "mp4", 
            # Perbaikan Streaming Video
            "postprocessor_args": ['-movflags', 'faststart'], 
        }
    )
    
    await infomsg.eor("Download ...")
    try:
        ytdl_data = await run_sync(ydl.extract_info, link, download=True)
        file_path = ydl.prepare_filename(ytdl_data)
        videoid = ytdl_data["id"]
        title = ytdl_data["title"]
        duration = ytdl_data["duration"]
        channel = ytdl_data["uploader"]
        views = f"{ytdl_data['view_count']:,}".replace(",", ".")
        thumbs = f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"
    except Exception as error:
        return await infomsg.eor(f"**Gagal...\n\n❌ Error: {error}**")
        
    thumbnail = wget.download(thumbs)
    await e.client.send_file(
        e.chat.id,
        file=file_path,
        thumb=thumbnail,
        file_name=title,
        duration=duration,
        supports_streaming=True,
        caption=f'<blockquote>💡 Informasi {"video"}\n\n🏷 Nama: {title}\n🧭 Durasi: {duration}\n👀 Dilihat: {views}\n📢 Channel: {channel}\n🧑‍⚕️ Upload by: {ultroid_bot.full_name}</blockquote>',
        reply_to=e.reply_to_msg_id,
        parse_mode="html",
    )
    await infomsg.delete()
    for files in (thumbnail, file_path):
        if files and os.path.exists(files):
            os.remove(files)


@ultroid_cmd(pattern="song( (.*)|$)")
async def yt_audio(e):
    infomsg = await e.eor("`Processing...`")
    
    raw_query = str(e.text.split(None, 1)[1])
    cleaned_query = raw_query.split('?')[0].strip()
    
    is_playlist_url = 'list=' in raw_query or 'playlist?' in raw_query
    parsed_url = urlparse(cleaned_query if "://" in cleaned_query else f"https://{cleaned_query}")
    hostname = (parsed_url.hostname or "").lower()
    allowed_youtube_hosts = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }
    is_youtube_url = hostname in allowed_youtube_hosts

    link = cleaned_query
    
    if not is_youtube_url and not is_playlist_url:
        try:
            search = (
                SearchVideos(cleaned_query, offset=1, mode="dict", max_results=1)
                .result()
                .get("search_result")
            )
            link = f"https://youtu.be/{search[0]['id']}"
        except Exception as error:
            return await infomsg.eor(f"**Pencarian...\n\n❌ Error: {error}**")

    ydl_params = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "256",
                "nopostoverwrites": True,
            }
        ],
        "postprocessor_args": ['-movflags', 'faststart'],
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "nocheckcertificate": True,
        "geo_bypass": True,
        "cookiefile": "cookies.txt",
    }
    
    if is_playlist_url:
        ydl_params["playlist_items"] = '1-50'
        
    ydl = YoutubeDL(ydl_params)
    
    await infomsg.edit("Download ...")
    files_to_remove_after_upload = []

    try:
        ytdl_data = await run_sync(ydl.extract_info, link, download=True)
        
        entries = ytdl_data.get('entries', [ytdl_data])
        
        if ytdl_data.get('_type') == 'playlist':
            await infomsg.edit(f"`Playlist terdeteksi. Mengunggah {len(entries)} lagu...`")

        for entry in entries:
            if not entry: continue

            file_path = ydl.prepare_filename(entry) 
            base_path = os.path.splitext(file_path)[0]
            
            if not os.path.exists(file_path):
                 file_path = base_path + '.m4a'
                 if not os.path.exists(file_path):
                      await e.respond(f"❌ Gagal menemukan file: {entry.get('title')}. Mungkin diblokir.")
                      continue

            videoid = entry.get("id")
            title = entry.get("title")
            duration = entry.get("duration")
            channel = entry.get("uploader")
            views = f"{entry.get('view_count', 0):,}".replace(",", ".")
            thumbs = f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"

            thumbnail = wget.download(thumbs)
            
            await e.client.send_file(
                e.chat.id,
                file=file_path,
                thumb=thumbnail,
                file_name=f"{title}.m4a",
                duration=duration,
                supports_streaming=True,
                caption=f'<blockquote>💡 Informasi {"Audio"}\n\n🏷 Nama: {title}\n🧭 Durasi: {duration}\n👀 Dilihat: {views}\n📢 Channel: {channel}\n🧑‍⚕️ Upload by: {ultroid_bot.full_name}</blockquote>',
                reply_to=e.reply_to_msg_id,
                parse_mode="html",
            )
            
            files_to_remove_after_upload.extend([thumbnail, file_path, base_path + '.webm', base_path + '.mp3'])
            
            await sleep(1.5) 

        
    except Exception as error:
        return await infomsg.edit(f"**Downloader...\n\n❌ Error: {error}**")
    
    await infomsg.delete()

    for files in files_to_remove_after_upload:
        if files and os.path.exists(files):
            os.remove(files)
            
