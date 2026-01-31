# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_bot")

import os
import sys
import time
from platform import python_version as pyver
from random import choice

from telethon import __version__
from telethon.errors.rpcerrorlist import (
    BotMethodInvalidError,
    ChatSendMediaForbiddenError,
)

from xteam.version import __version__ as UltVer

from . import HOSTED_ON, LOGS

try:
    from git import Repo
except ImportError:
    LOGS.error("bot: 'gitpython' module not found!")
    Repo = None

from telethon.utils import resolve_bot_file_id
from xteam.configs import Var
from . import (
    ATRA_COL,
    LOGS,
    OWNER_NAME,
    ULTROID_IMAGES,
    Button,
    Carbon,
    Telegraph,
    allcmds,
    asst,
    bash,
    call_back,
    callback,
    def_logs,
    eor,
    get_string,
    heroku_logs,
    in_pattern,
    inline_pic,
    restart,
    shutdown,
    start_time,
    time_formatter,
    udB,
    ultroid_cmd,
    ultroid_version,
    updater,
)


def ULTPIC():
    return inline_pic() or choice(ULTROID_IMAGES)


buttons = [
    [
        Button.url(get_string("bot_3"), "https://github.com/TeamUltroid/Ultroid"),
        Button.url(get_string("bot_4"), "t.me/UltroidSupportChat"),
    ]
]

# Will move to strings
alive_txt = """
ᴜꜱᴇʀʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ

  ◍ ᴜꜱᴇʀʙᴏᴛ - {}
  ◍ ᴅᴀᴛᴀʙᴀꜱᴇ - {}
  ◍ ᴛᴇʟᴇᴛʜᴏɴ - {}
"""

in_alive = "{}\n\n🌀 <b>Ultroid Version -><b> <code>{}</code>\n🌀 <b>xteam -></b> <code>{}</code>\n🌀 <b>Python -></b> <code>{}</code>\n🌀 <b>Uptime -></b> <code>{}</code>\n🌀 <b>Branch -></b>[ {} ]\n\n• <b>Join @TeamUltroid</b>"


@callback("alive")
async def alive(event):
    text = alive_txt.format(ultroid_version, UltVer, __version__)
    await event.answer(text, alert=True)


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event, Telegraph)


heroku_api = Var.HEROKU_API


@ultroid_cmd(
    pattern="restart$",
    fullsudo=True,
)
async def restark(ult):
    ok = await ult.eor(get_string("bot_5"))
    who = "bot" if ult.client._bot else "user"
    udB.set_key("_RESTART", f"{who}_{ult.chat_id}_{ok.id}")
    if heroku_api:
        return await restart(ok)
    await bash("git pull && pip3 install -r requirements.txt")
    if len(sys.argv) > 1:
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        os.execl(sys.executable, sys.executable, "-m", "xteam")
        
@ultroid_cmd(
    pattern="gs$",
    fullsudo=False,
)
async def restart(e):
    try:
        await e.eor("`Processing...`")
        process = await bash("git pull && pip3 install -r requirements.txt")
        if process == 0:  # Check if the bash command was successful (exit code 0)
            await e.eor("`Restarting Success...`")
            os.execl(sys.executable, sys.executable, "-m", "xteam")
        else:
            await e.eor("`Restarting Failed!`\n`Check logs for more info.`")
    except Exception as err:
        await e.eor(f"`An error occurred during restart!`\n`{err}`")


@ultroid_cmd(
    pattern="shutdown$",
    fullsudo=True,
)
async def shutdownbot(ult):
    await shutdown(ult)


@ultroid_cmd(
    pattern="logs( (.*)|$)",
    chats=[],
)
async def _(event):
    opt = event.pattern_match.group(1).strip()
    file = f"userbot{sys.argv[-1]}.log" if len(sys.argv) > 1 else "userbot.log"
    if opt == "heroku":
        await heroku_logs(event)
    elif opt == "carbon" and Carbon:
        event = await event.eor(get_string("com_1"))
        with open(file, "r") as f:
            code = f.read()[-2500:]
        file = await Carbon(
            file_name="userbot-logs",
            code=code,
            backgroundColor=choice(ATRA_COL),
        )
        if isinstance(file, dict):
            await event.eor(f"`{file}`")
            return
        await event.reply("**Userbot Logs.**", file=file)
    elif opt == "open":
        with open("userbot.log", "r") as f:
            file = f.read()[-4000:]
        return await event.eor(f"`{file}`")
    elif (
        opt.isdigit() and 5 <= int(opt) <= 100
    ):  # Check if input is a number between 10 and 100
        num_lines = int(opt)
        with open("userbot.log", "r") as f:
            lines = f.readlines()[-num_lines:]
            file = "".join(lines)
        return await event.eor(f"`{file}`")
    else:
        await def_logs(event, file)
    await event.try_delete()


@ultroid_cmd(pattern="update( (.*)|$)")
async def _(e):
    xx = await e.eor(get_string("upd_1"))
    if e.pattern_match.group(1).strip() and (
        "fast" in e.pattern_match.group(1).strip()
        or "soft" in e.pattern_match.group(1).strip()
    ):
        await bash("git pull -f && pip3 install -r requirements.txt")
        call_back()
        await xx.edit(get_string("upd_7"))
        os.execl(sys.executable, "python3", "-m", "xteam")
        # return
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await asst.send_file(
            udB.get_key("LOG_CHANNEL"),
            ULTPIC(),
            caption="• **Update Available** •",
            force_document=False,
            buttons=Button.inline("Changelogs", data="changes"),
        )
        Link = x.message_link
        await xx.edit(
            f'<strong><a href="{Link}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await xx.edit(
            f'<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong><a href="https://github.com/TeamUltroid/Ultroid/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail", owner=True)
async def updava(event):
    await event.delete()
    await asst.send_file(
        udB.get_key("LOG_CHANNEL"),
        ULTPIC(),
        caption="• **Update Available** •",
        force_document=False,
        buttons=Button.inline("Changelogs", data="changes"),
    )
