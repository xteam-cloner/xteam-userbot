""" Google Text to Speech
Available Commands:
• tts <LanguageCode> ; <text>
• tts <text> (uses 'en' by default)
• tts <LanguageCode> (as reply to a message)
"""

import os
import subprocess
import re
from datetime import datetime

from gtts import gTTS

# Menggunakan impor spesifik dari Xteam/Ultroid yang Anda berikan
from xteam._misc._decorators import ultroid_cmd
from xteam._misc._wrappers import eod, eor 


# ====================================================================
# FUNGSI ALTERNATIF PENGGANTI deEmojify
# ====================================================================

def de_emojify_alt(text):
    """Menghapus emoji dan karakter yang tidak dapat diucapkan TTS."""
    # Pattern untuk menemukan sebagian besar emoji (Unicode)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    # Ganti emoji dengan spasi kosong atau hapus
    return emoji_pattern.sub(r'', text)

# ====================================================================
# DEKORATOR DAN FUNGSI UTAMA
# ====================================================================

@ultroid_cmd(pattern="tts(?:\s|$)([\s\S]*)")
async def tts_cmd(event):
    "Text to speech command"
    input_str = event.pattern_match.group(1)
    start = datetime.now()
    
    # PERUBAHAN: Menggunakan event.reply_to_msg_id secara langsung
    reply_to_id = event.reply_to_msg_id

    lan = "en" 
    text = None

    if ";" in input_str:
        try:
            lan, text = input_str.split(";", 1)
            lan = lan.strip()
            text = text.strip()
        except ValueError:
            text = input_str.strip()
            lan = "en"
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str.strip() or "en"
    else:
        text = input_str.strip()
        lan = "en"

    if not text:
        return await eor(event, "Invalid Syntax. Please provide text or reply to a message.", time=5)

    catevent = await eor(event, "`Recording......`")
    
    try:
        # PENGGANTIAN: Menggunakan fungsi alternatif yang kita buat
        text = de_emojify_alt(text)
        
        if not os.path.isdir("./temp/"):
            os.makedirs("./temp/")
            
        required_file_name = "./temp/" + "voice.ogg"
        
        # gTTS part
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)

        # FFMPEG Conversion to OGG Opus
        opus_file_name = f"{required_file_name}.opus"
        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            opus_file_name,
        ]

        try:
            subprocess.check_output(
                command_to_execute, stderr=subprocess.STDOUT
            )
            os.remove(required_file_name)
            final_file_name = opus_file_name
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            final_file_name = required_file_name

        # --- Send File and Cleanup ---
        end = datetime.now()
        ms = (end - start).seconds
        
        await event.client.send_file(
            event.chat_id,
            final_file_name,
            reply_to=reply_to_id, # Menggunakan variabel yang diperbarui
            allow_cache=False,
            voice_note=True,  
        )
        
        os.remove(final_file_name)
        if os.path.exists(required_file_name): 
             os.remove(required_file_name)
             
        await eod(
            catevent, f"`Processed text {text[:30]}... into voice in {ms} seconds!`", time=5
        )

    except Exception as e:
        await eor(catevent, f"**Error during TTS process:**\n`{e}`\n\n*Check language code (`{lan}`) or `ffmpeg` installation.*", time=10)
        
