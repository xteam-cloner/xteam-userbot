# Port by Koala 🐨/@manuskarakitann
# Recode by @mrismanaziz
# FROM Man-Userbot <https://github.com/mrismanaziz/Man-Userbot/>
# t.me/SharingUserbot & t.me/Lunatic0de
# Nyenyenye bacot

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest

from . import ultroid_cmd as man_cmd
from . import eor, OWNER_NAME


@man_cmd(pattern="sosmed(?: |$)(.*)")
async def insta(event):
    xxnx = event.pattern_match.group(1)
    if xxnx:
        link = xxnx
    elif event.reply:
        link = await event.get_reply_message()
    else:
        return await event.reply("**Berikan Link Sosmed atau Reply Link Sosmed Untuk di Download**",
        )
    xx = await event.eor("`Processing Download...`")
    chat = "@SaveAsbot"
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=523131145)
            )
            await event.client.send_message(chat, link)
            response = await response
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            await event.client.send_message(chat, link)
            response = await response
        if response.text.startswith("Forward"):
            await xx.edit("Forward Private .")
        else:
            await xx.delete()
            await event.client.send_file(
                event.chat_id,
                response.message.media,
                caption=f"**Upload By: {OWNER_NAME}**",
            )
            await event.client.send_read_acknowledge(conv.chat_id)
            await event.client(DeleteHistoryRequest(peer=chat, max_id=0))
            await xx.delete()


@man_cmd(pattern="tiktok(?: |$)(.*)")
async def _(event):
    xxnx = event.pattern_match.group(1)
    if xxnx:
        d_link = xxnx
    elif event.reply:
        d_link = await event.get_reply_message()
    else:
        return await event.eor("**Berikan Link Tiktok Pesan atau Reply Link Tiktok Untuk di Download**",
        )
    xx = await event.eor("`Video Sedang Diproses...`")
    chat = "@SaveOFFbot"
    async with event.client.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        await event.client.send_file(event.chat_id, video)
        await event.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id, text.id]
        )
        await xx.delete()
