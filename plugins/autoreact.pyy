from random import choice

from telethon.events import NewMessage
from telethon.tl.types import ReactionEmoji

from . import ultroid_bot, ultroid_cmd


EMO = ('🥱', '🤪', '🙉', '😍', '🦄', '🐳', '😘', '💘', '😈', '❤️‍🔥', '🌭', '❤️', '🤔', '🎄', '🥴', '💩', '😁', '👾', '👨‍💻', '🕊', '😐', '👌', '👍', '🔥', '🙈', '🤬', '💋', '😴', '🤷', '🆒', '🤓', '🍌', '😡', '🤡', '👀', '💔', '🤗', '☃️', '🙊', '😭', '🤮', '✍️', '🎃', '😇', '👻', '🏆', '🤝', '💯', '😢', '😱', '🤯', '🤨', '🌚', '😨', '⚡️', '🎉', '🫡', '🤩', '🥰', '🍾', '👏', '🙏', '🎅', '😎', '💊', '👎', '🤣', '🗿', '💅', '🍓', '🖕', '🤷‍♂️', '🤷', '🤷‍♀️')


async def autoreact(e):
    try:
        emoji = choice(EMO)
        # Pastikan event adalah pesan (NewMessage) dan bukan event lain
        if isinstance(e, NewMessage.Event): 
            await e.react([ReactionEmoji(emoji)])
    except Exception:
        pass


def autoreact_status():
    for func, _ in ultroid_bot.list_event_handlers():
        if func == autoreact:
            return True


@ultroid_cmd(pattern="autoreact( (.*)|$)")
async def self_react(e):
    args = e.pattern_match.group(2)
    eris = await e.eor("...")
    if args == "on":
        if autoreact_status():
            return await eris.edit("AutoReact is Already Enabled..")
        
        # PERUBAHAN UTAMA DI SINI
        ultroid_bot.add_event_handler(
            autoreact,
            NewMessage(
                outgoing=False, # Reaksi pada pesan MASUK (dari orang lain)
                func=lambda e: not (e.fwd_from or e.via_bot),
            )
        )
        await eris.edit("AutoReact Enabled for ALL INCOMING messages!")
        
    elif args == "off":
        if not autoreact_status():
            return await eris.edit("AutoReact is Already Disabled..")
        ultroid_bot.remove_event_handler(autoreact)
        await eris.edit("AutoReact Disabled!")
        
    else:
        await eris.edit("Usage: .autoreact on/off")

from random import choice
from telethon import events, types
from . import ultroid_bot

# List of Premium Emoji IDs
premium_emoji_ids = [
    6170163662544707658,
    6176905893616031802,
    5276239041052828276,
    6267298050205553492,
    6267152480878990865,
    6265037836550936046,
    5330424644811901502,
    5451975792701483896,
    4963308045988791045,
    5438496463044752972,
    5456140674028019486,
    5217822164362739968,
    6172264674646559807,
    5069103192252351318,
    5276417256425805738,
    5965025312839306409,
    5965424233696726051,
    5965343106059472334,
    5965281048077012942,
    5039661745489052379,
    5042127383134470945,
    5039834781131474002,
    5231179572782847122,
    5231019684035326678,
    6194737030165959506,
]

@ultroid_bot.on(events.NewMessage)
async def rootedcyber(event):
    try:
        # pick a random premium emoji ID
        emoji_id = choice(premium_emoji_ids)
        await event.react(
            [types.ReactionCustomEmoji(document_id=emoji_id)],
            big=choice((True, False))
        )
    except Exception as e:
        print(f"Reaction failed: {e}")
