# 🍀 © @tofik_dn
# FROM Man-Userbot <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de
# ⚠️ Do not remove credits

import os
import requests
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from secrets import choice
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterVoice
from telethon.tl.types import InputMessagesFilterPhotos
from . import ultroid_bot, eor, ultroid_cmd, get_string, OWNER_NAME

@ultroid_cmd(pattern="asupan$")
async def _(event):
    xx = await event.eor(get_string("asupan_1"))
    try:
        asupannya = [
            asupan
            async for asupan in event.client.iter_messages(
                "@xcryasupan", filter=InputMessagesFilterVideo
            )
        ]
        await event.client.send_file(
            event.chat_id, file=choice(asupannya), caption=f"Asupan BY 🥀{OWNER_NAME}🥀", reply_to=event.reply_to_msg_id
        )
        await xx.delete()
    except Exception:
        await xx.edit("**Tidak bisa menemukan video asupan.**")

@ultroid_cmd(pattern="pap$")
async def _(event):
    xx = await event.eor(get_string("asupan_1"))
    try:
        papnya = [
            pap
            async for pap in event.client.iter_messages(
                "@CeweLogoPack", filter=InputMessagesFilterPhotos
            )
        ]
        await event.client.send_file(
            event.chat_id, file=choice(papnya), reply_to=event.reply_to_msg_id
        )
        await xx.delete()
    except Exception:
        await xx.edit("**Tidak bisa menemukan pap.**")

@ultroid_cmd(pattern="ppcp$")
async def _(event):
    xx = await event.eor(get_string("asupan_1"))
    try:
        ppcpnya = [
            ppcp
            async for ppcp in event.client.iter_messages(
                "@ppcpcilik", filter=InputMessagesFilterPhotos
            )
        ]
        await event.client.send_file(
            event.chat_id, file=choice(ppcpnya), reply_to=event.reply_to_msg_id
        )
        await xx.delete()
    except Exception:
        await xx.edit("**Tidak bisa menemukan pap couple.**")

@ultroid_cmd(pattern="desah$")
async def _(event):
    xx = await event.eor(get_string("asupan_1"))
    try:
        desahcewe = [
            desah
            async for desah in event.client.iter_messages(
                "@desahancewesangesange", filter=InputMessagesFilterVoice
            )
        ]
        await event.client.send_file(
            event.chat_id, file=choice(desahcewe), reply_to=event.reply_to_msg_id
        )
        await xx.delete()
    except Exception:
        await xx.edit("**Tidak bisa menemukan desahan cewe.**")


@ultroid_cmd(pattern="autowaifu$")
async def set_random_waifu(e):
    """Fetches a random waifu and sets it as the profile picture."""
    
    msg = await eor(e, "`Searching for a new waifu...`")

    try:
        # 1. Fetch the API for an image URL
        api_url = "https://api.waifu.pics/sfw/waifu"
        api_response = requests.get(api_url)

        if api_response.status_code != 200:
            await eor(msg, "`❌ The waifu API is currently unavailable.`")
            return
            
        image_url = api_response.json().get("url")
        if not image_url:
            await eor(msg, "`❌ The waifu API did not return a valid image URL.`")
            return

        # 2. Download the actual image file
        await eor(msg, "`Waifu found! Verifying and Downloading...`")
        temp_file = "temp_waifu.jpg"
        
        image_response = requests.get(image_url)
        
        # --- NEW CHECKS START HERE ---
        # Check 1: Ensure the download was successful
        if image_response.status_code != 200:
            await eor(msg, f"`❌ Failed to download the image file from the source. (Status: {image_response.status_code})`")
            return
            
        # Check 2: Ensure the content type is an image
        content_type = image_response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            await eor(msg, f"`❌ The downloaded file was not a valid image. (Type: {content_type})`")
            return
        
        # Check 3: Ensure the file has content
        image_content = image_response.content
        if not image_content:
            await eor(msg, "`❌ The downloaded image file was empty.`")
            return
        # --- NEW CHECKS END HERE ---

        with open(temp_file, "wb") as f:
            f.write(image_content)

        # 3. Set the new profile picture
        await eor(msg, "`Uploading as new DP...`")
        uploaded_file = await ultroid_bot.upload_file(temp_file)
        
        # Using a keyword argument for clarity, as the error suggests
        await ultroid_bot(UploadProfilePhotoRequest(file=uploaded_file))
        
        # 4. Send confirmation
        await eor(msg, "`✅ New waifu has been set as your DP!`")
    
    except Exception as err:
        await eor(msg, f"`An unexpected error occurred: {err}`")
        print(f"[AutoWaifu Error]: {err}")

    finally:
        # Make sure the temporary file is always deleted
        if os.path.exists(temp_file):
            os.remove(temp_file)
