from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
import asyncio
from telethon.errors import FloodWaitError, UserAdminInvalidError, ChatAdminRequiredError
from . import ultroid_cmd
from . import *


@ultroid_cmd(pattern="limited$")
async def demn(ult):
    chat = "@SpamBot"
    await ult.edit("Checking If You Are Limited...")
    async with ult.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(incoming=True, from_users=178220800))
            await ult.client.send_message(chat, "/start")
            response = await response
        except YouBlockedUserError:
            await ult.reply("Boss! Please Unblock @SpamBot ")
            return
        await eor(ult, f"<blockquote>{response.message.message}</blockquote>", parse_mode="html")


@ultroid_cmd(pattern="banall(?: (.*))?")
async def banall(event):
    """Ban all members in a specified group (Dangerous, use carefully)"""
    if event.is_private:
        return await event.edit("`This command can only be used in groups!`")
    
    args = event.pattern_match.group(1)
    
    if not args:
        return await event.edit("`Please provide a group ID!`")
    
    try:
        chat_id = int(args.strip())
    except ValueError:
        return await event.edit("`Invalid group ID! Please provide a valid numeric ID.`")
    
    try:
        # Get the chat entity to verify it exists and bot has access
        chat = await event.client.get_entity(chat_id)
        chat_title = chat.title
    except Exception as e:
        return await event.edit(f"`Couldn't access the group: {str(e)}`")
    
    # Confirmation message and counter
    await event.edit(f"`Getting members from {chat_title}...`")
    
    try:
        total = 0
        banned = 0
        failed = 0
        
        async for user in event.client.iter_participants(chat_id):
            total += 1
            # Skip banning the bot itself
            if user.id == event.client.uid:
                continue
                
            try:
                await event.client.edit_permissions(
                    chat_id, 
                    user.id, 
                    view_messages=False
                )
                banned += 1
                await event.edit(
                    f"`Banning members in {chat_title}...\n`"
                    f"Progress: {banned}/{total}\n"
                    f"Success: {banned} | Failed: {failed}"
                )
            except FloodWaitError as e:
                # Handle flood wait
                await event.edit(f"`Hit FloodWait restriction. Sleeping for {e.seconds} seconds.`")
                await asyncio.sleep(e.seconds)
            except (UserAdminInvalidError, ChatAdminRequiredError):
                # Can't ban admins
                failed += 1
            except Exception as e:
                failed += 1
                
            # Sleep briefly between bans to reduce flood chance
            await asyncio.sleep(0.2)
            
        await event.edit(
            f"`Operation completed in {chat_title}\n`"
            f"Total members: {total}\n"
            f"Successfully banned: {banned}\n"
            f"Failed to ban: {failed}"
        )
    except Exception as e:
        await event.edit(f"`An error occurred: {str(e)}`")

# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

# Asumsi impor internal yang diperlukan sudah ada:
from . import ultroid_cmd, LOGS, eor 

@ultroid_cmd(pattern="limit$") 
async def demn(ult):
    """
    Checks the user's account for Telegram limitations using @SpamBot.
    Displays the result by editing the original message (most reliable method).
    """
    chat = "@SpamBot"
    # Edit the message immediately to show activity
    await ult.edit("Checking If You Are Limited... ⏳")
    
    # Start a conversation with SpamBot
    async with ult.client.conversation(chat) as conv:
        try:
            # Prepare to wait for the bot's response (from ID 178220800)
            response = conv.wait_event(events.NewMessage(incoming=True, from_users=178220800))
            
            # Send the /start command
            await ult.client.send_message(chat, "/start")
            
            # Wait for the bot's message
            spambot_message = await response
            
        except YouBlockedUserError:
            return await ult.reply("Boss! Please **Unblock @SpamBot** to run the check.")
        except BaseException as er:
            LOGS.exception(er)
            return await ult.eor("An **Error** occurred while communicating with @SpamBot.")
            
    # Use eor (edit or reply) to display the final result directly.
    await eor(
        ult, 
        f"**@SpamBot Result:**\n\n<blockquote>{spambot_message.message}</blockquote>", 
        parse_mode="html"
    )
