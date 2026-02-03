# made by eris. for [ultroid]
# for the love of Thanos.. ((◡‿◡)) 

""" 
✘ Commands Available -

• `{i}thanos`  </>

⚠️Warning⚠️: This is not an Animation Plugin.

⚠️ **USING THIS PLUGIN WILL WIPE HALF THE MEMBERS OF YOUR CHAT.**⚠️

  💜 __#Purple_Guy__ 💜
"""

from random import shuffle
from telethon import functions
from asyncio import sleep
from telethon.tl.types import ChannelParticipantsAdmins as peru

from . import *

@ultroid_cmd(
    pattern="thanos",
    groups_only=True,
    )
async def snap(e):
    if e.fwd_from:
        return
    here = await ultroid_bot.get_entity(e.chat_id)
    eris = ultroid_bot.uid
    immune = [eris]
    count = 0
    to_ban = []
    xceptions = [1493434512, 1212184059, 1434595544, 1187804106, 7653207520]
    thanos = await e.edit("**Thanos was Summoned..**")
    await sleep(3)
    await thanos.edit(
        "**Thanos: I don't like how this Place is so Overpopulated;**",
    )
    await sleep(3)
    await thanos.edit(
        "**Thanos: Raises his hands; and Snaps his Finger;**",
    )
    await sleep(3)

    if here.id in xceptions:
        await thanos.edit("`This Group has Immunity senpai` 😋🙏")
        await thanos.respond(
            "bde harami ho sar 😹",
            file="CAADAgAD6AwAAr4C8Unepq_f7qo3AwI",
        )
        return

    if here.creator or (here.admin_rights and here.admin_rights.ban_users):
        for perus in await ultroid_bot.get_participants(here.id, filter=peru):
            immune.append(perus.id)
        for members in await ultroid_bot.get_participants(here.id, limit=2000):
            if members.id not in immune:
                to_ban.append(members.id)
    else:
        await thanos.respond(
            "**Thanos:** `You're not Worthy enough Son 😎🤏😳`",
            file="https://telegra.ph/file/54b33c7f8a03a8f1eed0b.jpg",
        )
        await thanos.delete() # impossible
        return

    shuffle(to_ban)
    for i in range(len(to_ban)//2):
        try:
            await ultroid_bot.edit_permissions(
                here.id,
                to_ban[i],
                view_messages=False, 
            )
                # doesn't works in small chats, for obv reasons..
            count += 1
            await sleep(4)
        except Exception:
            pass
    await thanos.respond(
        f"`[Streak: {count}]`",
        file="https://telegra.ph/file/877b26300622eddb81d6f.jpg",
    )
    await thanos.delete() # pika surprise face 


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
  
