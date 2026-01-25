# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from datetime import datetime

from pytz import timezone as tz
from telethon import Button, events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.utils import get_display_name

from xteam._misc import SUDO_M, owner_and_sudos
from xteam.dB.base import KeyManager
from xteam.fns.helper import inline_mention
from strings import get_string
from . import asst
from . import *


BOT_USERNAME = asst.me.username

Owner_info_msg = udB.get_key("BOT_INFO_START")
custom_info = True
if Owner_info_msg is None:
    custom_info = False
    Owner_info_msg = f"""
**Owner** - {OWNER_NAME}
**OwnerID** - `{OWNER_ID}`

**Message Forwards** - {udB.get_key("PMBOT")}

**Xteam [v{ultroid_version}](https://github.com/TeamUltroid/Ultroid), powered by @TeamUltroid**
"""


_settings = [
    [
        Button.inline("API Kᴇʏs", data="cbs_apiset"),
        Button.inline("Pᴍ Bᴏᴛ", data="cbs_chatbot"),
    ],
    [
        Button.inline("Aʟɪᴠᴇ", data="cbs_alvcstm"),
        Button.inline("PᴍPᴇʀᴍɪᴛ", data="cbs_ppmset"),
    ],
    [
        Button.inline("Fᴇᴀᴛᴜʀᴇs", data="cbs_otvars"),
        Button.inline("VC Sᴏɴɢ Bᴏᴛ", data="cbs_vcb"),
    ],
    [Button.inline("« Bᴀᴄᴋ", data="mainmenu")],
]

_start = [
    [
        Button.url("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
    ],
    [
        Button.inline("⚙️ Settings ⚙️", data="setter"),
        Button.inline("Module", data="uh_Official_"),
    ],
    [
        Button.inline("👥 Multi Client", data="cbs_m_client"), # Tombol menuju menu Multi-Client
        Button.inline("✨ Stats ✨", data="stat"),
    ],
    [
        Button.inline("📻 Broadcast 📻", data="bcast"),
        Button.inline("🌐 Bahasa 🌐", data="lang"),
    ],
]

@callback("restart", owner=True)
async def restart_callback(e):
    global restart_counter
    ok = await e.reply("`Processing...`")
    who = "bot" if e.client._bot else "user"
    udB.set_key("_RESTART", f"{who}_{e.chat_id}_{ok.id}")
    if heroku_api and restart_counter < 10:
        restart_counter += 1
    #        return await restart_callback(e)
    await bash("git pull && pip3 install -r requirements.txt")
    os.execl(sys.executable, sys.executable, "-m", "xteam")
    


@callback("ownerinfo")
async def own(event):
    msg = Owner_info_msg.format(
        mention=event.sender.mention, me=inline_mention(ultroid_bot.me)
    )
    if custom_info:
        msg += "\n\n• Powered by **@xteam-cloner**"
    await event.edit(
        msg,
        buttons=[Button.inline("Close", data="closeit")],
        link_preview=False,
    )


@callback("closeit")
async def closet(lol):
    try:
        await lol.delete()
    except MessageDeleteForbiddenError:
        await lol.answer("MESSAGE_TOO_OLD", alert=True)


"""@asst_cmd(pattern="start( (.*)|$)", forwards=False, func=lambda x: not x.is_group)
async def ultroid(event):
    args = event.pattern_match.group(1).strip()
    keym = KeyManager("BOT_USERS", cast=list)
    if not keym.contains(event.sender_id) and event.sender_id not in owner_and_sudos():
        keym.add(event.sender_id)
        kak_uiw = udB.get_key("OFF_START_LOG")
        if not kak_uiw or kak_uiw != True:
            msg = f"{inline_mention(event.sender)} `[{event.sender_id}]` started your [Assistant bot](@{asst.me.username})."
            buttons = [[Button.inline("Info", "itkkstyo")]]
            if event.sender.username:
                buttons[0].append(
                    Button.mention(
                        "User", await event.client.get_input_entity(event.sender_id)
                    )
                )
            await event.client.send_message(
                udB.get_key("LOG_CHANNEL"), msg, buttons=buttons
            )
    if event.sender_id not in SUDO_M.fullsudos:
        ok = ""
        me = inline_mention(ultroid_bot.me)
        mention = inline_mention(event.sender)
        if args and args != "set":
            await get_stored_file(event, args)
        if not udB.get_key("STARTMSG"):
            if udB.get_key("PMBOT"):
                ok = "You can contact my master using this bot!!\n\nSend your Message, I will Deliver it To Master."
            await event.reply(
                f"Hey there {mention}, this is Assistant of {me}!\n\n{ok}",
                file=udB.get_key("STARTMEDIA"),
                buttons=[Button.inline("Info.", data="ownerinfo")]
                if Owner_info_msg
                else None,
            )
        else:
            await event.reply(
                udB.get_key("STARTMSG").format(me=me, mention=mention),
                file=udB.get_key("STARTMEDIA"),
                buttons=[Button.inline("Info.", data="ownerinfo")]
                if Owner_info_msg
                else None,
            )
    else:
        name = get_display_name(event.sender)
        if args == "set":
            await event.reply(
                "Choose from the below options -",
                buttons=_settings,
            )
        elif args:
            await get_stored_file(event, args)
        else:
            await event.respond(
                f"<blockquote>Hey {name}. Please browse through the options</blockquote>",
                message_effect_id=5104841245755180586,
                buttons=_start,
                parse_mode="html",
            )
            await event.react("🔥")  # Add a thumbs-up emoji reaction
"""

# Assuming 'start_photo.jpg' is in a 'media' folder relative to your bot's root
# You'll need to import os if you use relative paths
import os 

# ... (rest of your imports)

@asst_cmd(pattern="start( (.*)|$)", forwards=False, func=lambda x: not x.is_group)
async def ultroid(event):
    args = event.pattern_match.group(1).strip()
    keym = KeyManager("BOT_USERS", cast=list)
    if not keym.contains(event.sender_id) and event.sender_id not in owner_and_sudos():
        keym.add(event.sender_id)
        kak_uiw = udB.get_key("OFF_START_LOG")
        if not kak_uiw or kak_uiw != True:
            msg = f"{inline_mention(event.sender)} `[{event.sender_id}]` started your [Assistant bot](@{asst.me.username})."
            buttons = [[Button.inline("Info", "itkkstyo")]]
            if event.sender.username:
                buttons[0].append(
                    Button.mention(
                        "User", await event.client.get_input_entity(event.sender_id)
                    )
                )
            await event.client.send_message(
                udB.get_key("LOG_CHANNEL"), msg, buttons=buttons
            )
    if event.sender_id not in SUDO_M.fullsudos:
        ok = ""
        me = inline_mention(ultroid_bot.me)
        mention = inline_mention(event.sender)
        if args and args != "set":
            await get_stored_file(event, args)
        
        # Define the path to your photo
        # You can replace this with a direct file path, e.g., "path/to/your/photo.jpg"
        # Or if you've uploaded it to Telegram and have its file ID, you can use that
        photo_path = "https://files.catbox.moe/20rxet.jpg" # Example: Assuming 'media' folder

        if not udB.get_key("STARTMSG"):
            if udB.get_key("PMBOT"):
                ok = "You can contact my master using this bot!!\n\nSend your Message, I will Deliver it To Master."
            await event.reply(
                f"Hey there {mention}, this is Assistant of {me}!\n\n{ok}",
                file=photo_path,  # Use your photo path here
                buttons=[Button.inline("Info.", data="ownerinfo")]
                if Owner_info_msg
                else None,
            )
        else:
            await event.reply(
                udB.get_key("STARTMSG").format(me=me, mention=mention),
                file=photo_path,  # Use your photo path here
                buttons=[Button.inline("Info.", data="ownerinfo")]
                if Owner_info_msg
                else None,
            )
    else:
        name = get_display_name(event.sender)
        if args == "set":
            await event.reply(
                "Choose from the below options -",
                buttons=_settings,
            )
        elif args:
            await get_stored_file(event, args)
        else:
            await event.respond(
                f"<blockquote>Hey {name}. Please browse through the options</blockquote>",
                message_effect_id=5104841245755180586,
                buttons=_start,
                parse_mode="html",
            )
            

@callback("itkkstyo", owner=True)
async def ekekdhdb(e):
    text = f"When New Visitor will visit your Assistant Bot. You will get this log message!\n\nTo Disable : {HNDLR}setdb OFF_START_LOG True"
    await e.answer(text, alert=True)


@callback("mainmenu", owner=True, func=lambda x: not x.is_group)
async def ultroid(event):
    await event.edit(
        get_string("ast_3").format(OWNER_NAME),
        message_effect_id=5104841245755180586,
        buttons=_start,
    )


@callback("stat", owner=True)
async def botstat(event):
    ok = len(udB.get_key("BOT_USERS") or [])
    msg = """Xteam Assistant - Stats
Total Users - {}""".format(
        ok,
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast", owner=True)
async def bdcast(event):
    keym = KeyManager("BOT_USERS", cast=list)
    total = keym.count()
    await event.edit(f"• Broadcast to {total} users.")
    async with event.client.conversation(OWNER_ID) as conv:
        await conv.send_message(
            "Enter your broadcast message.\nUse /cancel to stop the broadcast.",
        )
        response = await conv.get_response()
        if response.message == "/cancel":
            return await conv.send_message("Cancelled!!")
        success = 0
        fail = 0
        await conv.send_message(f"Starting a broadcast to {total} users...")
        start = datetime.now()
        for i in keym.get():
            try:
                await asst.send_message(int(i), response)
                success += 1
            except BaseException:
                fail += 1
        end = datetime.now()
        time_taken = (end - start).seconds
        await conv.send_message(
            f"""
**Broadcast completed in {time_taken} seconds.**
Total Users in Bot - {total}
**Sent to** : `{success} users.`
**Failed for** : `{fail} user(s).`""",
        )


@callback("setter", owner=True)
async def setting(event):
    await event.edit(
        "Choose from the below options -",
        buttons=_settings,
    )


@callback("tz", owner=True)
async def timezone_(event):
    await event.delete()
    pru = event.sender_id
    var = "TIMEZONE"
    name = "Timezone"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send Your TimeZone From This List [Check From Here](http://www.timezoneconverter.com/cgi-bin/findzone.tzc)"
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("mainmenu"),
            )
        try:
            tz(themssg)
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} changed to {themssg}\n",
                buttons=get_back_button("mainmenu"),
            )
        except BaseException:
            await conv.send_message(
                "Wrong TimeZone, Try again",
                buttons=get_back_button("mainmenu"),
            )
