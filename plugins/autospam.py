# plugin: autospam
# usage: .autospam <Detik> <Jumlah> <Pesan>

#from xteam.fns.helper import edit_or_reply
import asyncio
from . import eor
from . import *

@ultroid_cmd(pattern="autospam ?(.*)")
async def autospam(event):
    args = event.pattern_match.group(1).split(" ", 2)
    if len(args) < 3:
        return await eor(event, "Gunakan format: .autospam <detik> <jumlah> <pesan>")

    try:
        delay = int(args[0])
        count = int(args[1])
    except ValueError:
        return await eor(event, "❌ Harus Angka!")

    message = args[2]
    await eor(event, f"Mulai Autospam {count}x Setiap {delay} Detik.")

    for _ in range(count):
        await event.respond(message)
        await asyncio.sleep(delay)
