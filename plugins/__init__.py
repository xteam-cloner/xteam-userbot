# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
import base64
import contextlib

from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.tl.types import MessageEntityMentionName
import asyncio
import os
import time
import datetime
from random import choice
import requests
import re
from telethon import Button, events
from telethon.tl import functions, types  # pylint:ignore
from xteam import udB
from xteam._misc._assistant import asst_cmd, callback, in_pattern
from xteam._misc._decorators import ultroid_cmd
from xteam._misc._wrappers import eod, eor
from xteam.dB import DEVLIST as devs, ULTROID_IMAGES, ALIVE_TEXT, ALIVE_NAME, QUOTES
from xteam.fns.helper import *
from xteam.fns.misc import *
from xteam.fns.tools import *
from xteam.startup._database import _BaseDatabase as Database
from xteam.version import __version__, ultroid_version
from strings import get_help, get_string
from xteam._misc._supporter import CMD_HNDLR
from xteam.dB import stickers
from xteam._misc._supporter import Config
from pyrogram import __version__ as pver
from telegram import __version__ as lver
from telethon import __version__ as tver
from pytgcalls import __version__ as pytver
from platform import python_version as pyver
from ntgcalls import NTgCalls
from git import Repo

BOT_NAME = asst.full_name
BOT_USERNAME = asst.username
    
ntgcalls = NTgCalls()
udB: Database
Redis = udB.get_key
con = TgConverter
quotly = Quotly()
OWNER_NAME = ultroid_bot.full_name
OWNER_ID = ultroid_bot.uid
OWNER_USERNAME = ultroid_bot.username
ultroid_bot: UltroidClient
asst: UltroidClient

LOG_CHANNEL = udB.get_key("LOG_CHANNEL")
StartTime = time.time()
xteam = ultroid_cmd

# DEFINISI FUNGSI BARU DENGAN DUA PARAMETER
def format_message_text(uptime, branch_info):
    return f"<blockquote><b>✰ xᴛᴇᴀᴍ ᴜʀʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ✰</b></blockquote>\n" \
                       f"✵ Owner : <a href='https://t.me/{OWNER_USERNAME}'>{OWNER_NAME}</a>\n" \
                       f"✵ Userbot : {ultroid_version}\n" \
                       f"✵ Telegram : {lver}\n" \
                       f"✵ Library : {__version__}\n" \
                       f"✵ Uptime : {uptime}\n" \
                       f"✵ Kurigram :  {pver}\n" \
                       f"✵ Python : {pyver()}\n" \
                       f"✵ Branch : {branch_info}\n" \
                       f"<blockquote>✵ <a href='https://t.me/xteam_cloner'>xᴛᴇᴀᴍ ᴄʟᴏɴᴇʀ</a> ✵</blockquote>\n"
    

def inline_pic():
    INLINE_PIC = udB.get_key("INLINE_PIC")
    if INLINE_PIC is None:
        INLINE_PIC = choice(ULTROID_IMAGES)
    elif INLINE_PIC == False:
        INLINE_PIC = None
    return INLINE_PIC

def ping_pic():
    PING_PIC = udB.get_key("PING_PIC")
    if PING_PIC is None:
        PING_PIC = choice(ULTROID_IMAGES)
    elif PING_PIC == False:
        PING_PIC = None
    return PING_PIC

def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += f"{time_list.pop()}, "

    time_list.reverse()
    readable_time += ":".join(time_list)

    return readable_time


Telegraph = telegraph_client()

List = []
Dict = {}
InlinePlugin = {}
N = 0
cmd = ultroid_cmd
STUFF = {}

# Chats, which needs to be ignore for some cases
# Considerably, there can be many
# Feel Free to Add Any other...

NOSPAM_CHAT = [
    -1001361294038,  # UltroidSupportChat
    -1001387666944,  # PyrogramChat
    -1001109500936,  # TelethonChat
    -1001050982793,  # Python
    -1001256902287,  # DurovsChat
    -1001473548283,  # SharingUserbot
    -1001599474353,
    -1001692751821,
    -1001473548283,
    -1001459812644,
    -1001433238829,
    -1001476936696,
    -1001327032795,
    -1001294181499,
    -1001419516987,
    -1001209432070,
    -1001296934585,
    -1001481357570,
    -1001459701099,
    -1001109837870,
    -1001485393652,
    -1001354786862,
    -1001109500936,
    -1001387666944,
    -1001390552926,
    -1001752592753,
    -1001777428244,
    -1001771438298,
    -1001287188817,
    -1001812143750,
    -1001883961446,
    -1001753840975,
    -1001896051491,
    -1001578091827,
    -1001284445583,
    -1001927904459,
    -1001675396283,
    -1001825363971,
    -1001537280879,
    -1001302879778,
    -1001797285258,
    -1001864253073,
    -1001876092598,
    -1001608847572,
    -1001451642443,
    -1001538826310,
    -1001608701614,
    -1001861414061,
    -1001406767793,
    -1001306409796,
    -1002136866494,
    -1002234906165,
    -1001557462351,
    -1001185324811,
    -1002341392113,
    -1002385138723,
    -1001967927814,
    -1002385138723,
    -1001412793637,
    -1001642830120,
    -1002021708108,
    -1001959795445,
    -1002527076716,
    -1002423575637,
    -1002145187257,
    -1001565185455,
    -1002499477370,
    -1001361294038,
    -1002660045875,
    -1001648363067,
    5833984187,
    1064619217,
    -1002211540481,
    -1002479806260,
    -1001127623478,
    -1001608847572,
    -1002519094633,
    -1002230988371,
    -1001266867995,
    -1001515039426,
    -1002071984353,
    -1001473548283,
    -1001756554066,
    -1001311820878,
    -1001341570295,
    -1001396570230,
    -1001518177837,
    -1002623388730,
    -1001913016880,
    -1002384331014,
    -1002785759023,
    -1001904750758,
    -1001705737689,
    -1002564660639,
    -1001999755950,
]

KANGING_STR = [
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "Hehe me stel ur stiker...",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pack looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal-Your-Sticker is stealing this sticker... ",
]

ATRA_COL = [
    "DarkCyan",
    "DeepSkyBlue",
    "DarkTurquoise",
    "Cyan",
    "LightSkyBlue",
    "Turquoise",
    "MediumVioletRed",
    "Aquamarine",
    "Lightcyan",
    "Azure",
    "Moccasin",
    "PowderBlue",
]
