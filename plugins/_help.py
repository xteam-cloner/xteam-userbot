# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import base64
import inspect
from datetime import datetime
from html import unescape
from random import choice
from re import compile as re_compile

from bs4 import BeautifulSoup as bs
from telethon import Button
from telethon.tl.alltlobjects import LAYER, tlobjects
from telethon.tl.types import DocumentAttributeAudio as Audio
from telethon.tl.types import InputWebDocument as wb

from telethon.errors.rpcerrorlist import (
    BotInlineDisabledError,
    BotMethodInvalidError,
    BotResponseTimeoutError,
)
from telethon.tl.custom import Button
from assistant import *
from xteam.dB._core import HELP, LIST
from xteam.fns.tools import cmd_regex_replace

from . import HNDLR, LOGS, OWNER_NAME, asst, get_string, inline_pic, udB, ultroid_cmd, call_back, callback, def_logs, eor, get_string, heroku_logs, in_pattern

_main_help_menu = [
    [
        Button.inline("🏡 Modules 🏡", data="uh_Official_"),
    ],

]


@ultroid_cmd(pattern="help( (.*)|$)")
async def _help(ult):
    plug = ult.pattern_match.group(1).strip()
    chat = await ult.get_chat()
    if plug:
        try:
            if plug in HELP["Official"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Official"][plug]:
                    output += i
                output += "\n@xteam_cloner"
                await ult.eor(f"<blockquote>{output}</blockquote>", parse_mode="html")
            elif HELP.get("Addons") and plug in HELP["Addons"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Addons"][plug]:
                    output += i
                output += "\n@xteam_cloner"
                await ult.eor(output)
            elif HELP.get("VCBot") and plug in HELP["VCBot"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["VCBot"][plug]:
                    output += i
                output += "\n@xteam_cloner"
                await ult.eor(f"<blockquote>{output}</blockquote>", parse_mode="html")
            else:
                try:
                    x = get_string("help_11").format(plug)
                    for d in LIST[plug]:
                        x += "" + d
                        x += "\n"
                    x += "\n@xteam_cloner"
                    await ult.eor(f"<blockquote>{x}</blockquote>", parse_mode="html")
                except BaseException:
                    file = None
                    compare_strings = []
                    for file_name in LIST:
                        compare_strings.append(file_name)
                        value = LIST[file_name]
                        for j in value:
                            j = cmd_regex_replace(j)
                            compare_strings.append(j)
                            if j.strip() == plug:
                                file = file_name
                                break
                    if not file:
                        # the enter command/plugin name is not found
                        text = f"`{plug}` is not a valid plugin!"
                        best_match = None
                        for _ in compare_strings:
                            if plug in _ and not _.startswith("_"):
                                best_match = _
                                break
                        if best_match:
                            text += f"\nDid you mean `{best_match}`?"
                        return await ult.eor(text)
                    output = f"Command {plug} found in plugin - {file}\n"
                    if file in HELP["Official"]:
                        for i in HELP["Official"][file]:
                            output += i
                    elif HELP.get("Addons") and file in HELP["Addons"]:
                        for i in HELP["Addons"][file]:
                            output += i
                    elif HELP.get("VCBot") and file in HELP["VCBot"]:
                        for i in HELP["VCBot"][file]:
                            output += i
                    output += "\n@xteam_cloner"
                    await ult.eor(f"<blockquote>{output}</blockquote>", parse_mode="html")
        except BaseException as er:
            LOGS.exception(er)
            await ult.eor("Error 🤔 occured.")
    else:
        try:
            results = await ult.client.inline_query(asst.me.username, "help")
        except BotMethodInvalidError:
            z = []
            for x in LIST.values():
                z.extend(x)
            cmd = len(z) + 10
            if udB.get_key("MANAGER") and udB.get_key("DUAL_HNDLR") == "/":
                _main_help_menu[2:3] = [[Button.inline("• Manager Help •", "mngbtn")]]
            return await ult.reply(
                get_string("inline_4").format(
                    len(HELP["Official"]),
                    len(HELP["Addons"] if "Addons" in HELP else []),
                    cmd,
                    parse_mode="html",
                ),
                file=inline_pic(),
                buttons=_main_help_menu,
            )
        except BotResponseTimeoutError:
            return await ult.eor(
                get_string("help_2").format(HNDLR),
            )
        except BotInlineDisabledError:
            return await ult.eor(get_string("help_3"))
        await results[0].click(chat.id, reply_to=ult.reply_to_msg_id, hide_via=True)
        await ult.delete()
