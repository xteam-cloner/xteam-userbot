from telethon import Button, events

from . import *

import asyncio
import speedtest

# Commands

def testspeed(m):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        return
    return result

@ultroid_cmd(pattern="speedtest")
async def speedtest_function(message):
    m = await message.reply("Running Speed test")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    output = f"""<blockquote>✯ sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs ✯
    
❍ Client:
» ISP: {result['client']['isp']}
» Country: {result['client']['country']}
  
❍ Server:
» Name: {result['server']['name']}
» Country: {result['server']['country']}, {result['server']['cc']}
» Sponsor: {result['server']['sponsor']}
» Latency: {result['server']['latency']}  
» Ping: {result['ping']}</blockquote>"""
    await ultroid_bot.send_file(message.chat.id, result["share"], caption=output, parse_mode="html")
    await m.delete()


@ultroid_cmd(pattern="spt")
async def speedtest_function(ult):
    # ... your existing code ...
    try:
        result = speedtest.speedtest()  # Assuming 'speedtest' is your speedtest object
        if result and result.get('client') and result['client'].get('isp'): # Improved checking
            await ult.edit(
                f"**Speedtest Results:**\n"
                f"Download: {result['download'] / 1000 / 1000:.2f} Mbps\n"
                f"Upload: {result['upload'] / 1000 / 1000:.2f} Mbps\n"
                f"Ping: {result['ping']:.2f} ms\n"
                f"ISP: {result['client']['isp']}"
            )
        else:
            await ult.edit("**Error:** Could not retrieve speed test results or ISP information.") # Informative error message
    except Exception as e: # Catch potential exceptions during the speedtest
        await ult.edit(f"**Error:** An error occurred during the speed test: {e}") # More detailed error message
    # ... rest of your code ...
