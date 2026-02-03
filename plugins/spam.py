# < Source - t.me/testingpluginnn >
# < https://github.com/TeamUltroid/Ultroid >

"""
✘ Commands Available -
• `{i}spam <no of msgs> <your msg or reply message>`
    spams chat, the current limit for this is from 1 to 99.

• `{i}bigspam <no of msgs> <your msg>`
  `{i}bigspam <no of msgs> <reply message>`
    Spams chat, the current limit is above 100.

• `{i}delayspam <delay time> <count> <msg>`
    Spam chat with delays..

• `{i}tspam <text>`
    Spam Chat with One-One Character..

• **CMD:**
>  `{i}uspam <text>`
>  `{i}stopuspam`  ->  To stop spam.

•  **your account might get limited or banned!**
•  **use on your own risk !**
"""

import asyncio

from . import *
from asyncio import sleep
from telethon.errors import FloodWaitError
from . import udB, NOSPAM_CHAT as noU

udB.del_key("USPAM")

@ultroid_cmd(pattern="tspam", fullsudo=True)
async def tmeme(e):
    tspam = str(e.text[7:])
    message = tspam.replace(" ", "")
    for letter in message:
        await e.respond(letter)
    await e.delete()


@ultroid_cmd(pattern="spam", fullsudo=True)
async def spammer(e):
    message = e.text
    if e.reply_to:
        if not len(message.split()) >= 2:
            return await eod(e, "`Use in Proper Format`")
        spam_message = await e.get_reply_message()
    else:
        if not len(message.split()) >= 3:
            return await eod(e, "`Reply to a Message or Give some Text..`")
        spam_message = message.split(maxsplit=2)[2]
    counter = message.split()[1]
    try:
        counter = int(counter)
        if counter >= 100:
            return await eod(e, "`Use bigspam cmd`")
    except BaseException:
        return await eod(e, "`Use in Proper Format`")
    for i in range(counter):
        await e.respond(spam_message)
    await e.delete()


@ultroid_cmd(pattern="bigspam", fullsudo=True)
async def bigspam(e):
    message = e.text
    if e.reply_to:
        if not len(message.split()) >= 2:
            return await eod(e, "`Use in Proper Format`")
        spam_message = await e.get_reply_message()
    else:
        if not len(message.split()) >= 3:
            return await eod(e, "`Reply to a Message or Give some Text..`")
        spam_message = message.split(maxsplit=2)[2]
    counter = message.split()[1]
    try:
        counter = int(counter)
    except BaseException:
        return await eod(e, "`Use in Proper Format`")
    [await e.respond(spam_message) for i in range(counter)]
    await e.delete()


@ultroid_cmd(pattern="delayspam ?(.*)", fullsudo=True)
async def delayspammer(e):
    try:
        args = e.text.split(" ", 3)
        delay = float(args[1])
        count = int(args[2])
        msg = str(args[3])
    except BaseException:
        return await e.edit(f"**Usage :** {HNDLR}delayspam <delay time> <count> <msg>")
    await e.delete()
    try:
        for i in range(count):
            await e.respond(msg)
            await asyncio.sleep(delay)
    except Exception as u:
        await e.respond(f"**Error :** `{u}`")
            

@ultroid_cmd(
    pattern="uspam(?: |$)((?:.|\n)*)",
    fullsudo=True,
)
async def uspam(ult):
    eris = await ult.eor("...")
    input = ult.pattern_match.group(1)
    if not input:
        return await eod(eris, "`Give some text as well..`")

    # ult-spam and testingplug
    noU.extend([-1001212184059, -1001451324102])
    if ult.chat_id in noU:
        return await eris.edit("**I don't feel so good right now**")

    await eris.delete()
    udB.set_key("USPAM", True)
    while bool(udB.get_key("USPAM")):
        try:
            await ult.respond(str(input))
        except FloodWaitError as fw:
            udB.del_key("USPAM")
            await sleep(fw.seconds)
            return


@ultroid_cmd(pattern="s(top)?uspam$")
async def stopuspam(e):
    udB.del_key("USPAM")
    await e.eor("Unlimited spam stopped")
  
