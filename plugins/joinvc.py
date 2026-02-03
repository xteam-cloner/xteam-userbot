from xteam.vcbot import *
from . import ultroid_cmd, eor as edit_or_reply, eod as edit_delete
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.messages import GetFullChatRequest # Tambahkan ini
from telethon.tl.types import InputGroupCall # Tambahkan ini

@ultroid_cmd(pattern="joinvc", group_only=True)
async def join_voice_chat(event):
    chat_id = event.chat_id
    
    try:
        # Ambil informasi lengkap chat untuk mendapatkan akses ke Group Call ID
        full_chat = await event.client(GetFullChatRequest(chat_id))
        
        # Cek apakah ada VC yang sedang aktif
        if not full_chat.full_chat.call:
            return await edit_delete(event, "**Tidak ada Voice Chat yang aktif di grup ini.**", time=10)
        
        # Ambil objek InputGroupCall dari chat tersebut
        group_call = InputGroupCall(
            id=full_chat.full_chat.call.id,
            access_hash=full_chat.full_chat.call.access_hash
        )

        # Gunakan objek group_call, bukan chat_id
        await event.client.join_group_call(
            group_call, 
            join_as=event.input_chat
        ) 

        await edit_or_reply(event, "**Berhasil bergabung ke Voice Chat!**")

    except UserAlreadyParticipantError:
        await edit_delete(event, "**Akun sudah berada di Obrolan Suara.**", time=10)
    except Exception as e:
        # Menangani error EditMessageRequest yang tadi juga sempat muncul
        try:
            await edit_delete(event, f"**Gagal bergabung ke VC :** `{e}`", time=20)
        except:
            print(f"Error: {e}")

@ultroid_cmd(pattern="leavevc", group_only=True)
async def leave_voice_chat(event):
    chat_id = event.chat_id
    try:
        # Ambil data call terlebih dahulu untuk keluar
        full_chat = await event.client(GetFullChatRequest(chat_id))
        if full_chat.full_chat.call:
            group_call = InputGroupCall(
                id=full_chat.full_chat.call.id,
                access_hash=full_chat.full_chat.call.access_hash
            )
            await event.client.leave_group_call(group_call)
            await edit_or_reply(event, "**Meninggalkan Voice Chat.**")
        else:
            await edit_delete(event, "**Tidak ada Voice Chat aktif.**", time=10)
    
    except Exception as e:
        await edit_delete(event, f"**Gagal Keluar:** `{e}`", time=10)
        
