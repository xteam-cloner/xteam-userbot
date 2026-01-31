# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}gemini <prompt>`
    Get response from Google Gemini.

• `{i}antr <prompt>`
    Get response from Anthropic Claude.

• `{i}gpt <prompt>`
    Get response from OpenAI GPT.

• `{i}deepseek <prompt>`
    Get response from DeepSeek AI.

Set custom models using:
    • OPENAI_MODEL
    • ANTHROPIC_MODEL
    • GEMINI_MODEL
    • DEEPSEEK_MODEL
"""

import json
from . import LOGS, eor, get_string, udB, ultroid_cmd, async_searcher
import aiohttp
import asyncio
from telethon import Button
from . import *

ENDPOINTS = {
    "gpt": "https://api.openai.com/v1/chat/completions",
    "antr": "https://api.anthropic.com/v1/messages",
    # Gunakan v1beta dan pastikan model name sesuai dengan output LIST tadi
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
    "deepseek": "https://api.deepseek.com/v3/chat/completions"
}

DEFAULT_MODELS = {
    "gpt": "gpt-3.5-turbo",
    "antr": "claude-3-haiku",
    "gemini": "gemini-3-flash-preview", # Ubah ke nama yang ada di daftar tadi
    "deepseek": "DeepSeek-V3"
}



def get_model(provider):
    """Get model name from database or use default"""
    model_keys = {
        "gpt": "OPENAI_MODEL",
        "antr": "ANTHROPIC_MODEL",
        "gemini": "GEMINI_MODEL",
        "deepseek": "DEEPSEEK_MODEL"
    }
    return udB.get_key(model_keys[provider]) or DEFAULT_MODELS[provider]


async def stream_response(msg, text):
    """Stream response by editing message"""
    current = ""
    # Split into chunks of ~100 characters at word boundaries
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) > 100:
            chunks.append(" ".join(current_chunk[:-1]))
            current_chunk = [word]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    for chunk in chunks:
        current += chunk + " "
        try:
            await msg.edit(current)
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return current


async def get_ai_response(provider, prompt, api_key, stream=False):
    """Get response from AI provider"""
    try:
        headers = {"Content-Type": "application/json"}
        model = get_model(provider)
        
        if provider == "gpt":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream
            }
            if not stream:
                response = await async_searcher(
                    ENDPOINTS[provider],
                    headers=headers,
                    post=True,
                    json=data,
                    re_json=True
                )
                yield response["choices"][0]["message"]["content"]
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    ENDPOINTS[provider],
                    headers=headers,
                    json=data
                ) as resp:
                    async for line in resp.content:
                        if line:
                            try:
                                json_line = json.loads(line.decode('utf-8').strip().strip('data:').strip())
                                if 'choices' in json_line and json_line['choices']:
                                    content = json_line['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content
                            except Exception:
                                continue

        elif provider == "antr":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream
            }
            if not stream:
                response = await async_searcher(
                    ENDPOINTS[provider],
                    headers=headers,
                    post=True,
                    json=data,
                    re_json=True
                )
                yield response["content"][0]["text"]
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    ENDPOINTS[provider],
                    headers=headers,
                    json=data
                ) as resp:
                    async for line in resp.content:
                        if line:
                            try:
                                json_line = json.loads(line.decode('utf-8').strip())
                                if 'content' in json_line:
                                    content = json_line['content'][0]['text']
                                    if content:
                                        yield content
                            except Exception:
                                continue
            
        elif provider == "gemini":
            params = {"key": api_key}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = await async_searcher(
                ENDPOINTS[provider],
                params=params,
                headers=headers,
                post=True,
                json=data,
                re_json=True
            )

            # Cek jika ada error dari Google
            if "error" in response:
                yield f"❌ Google API Error: {response['error'].get('message')}"
                return

            # Cek keberadaan candidates secara aman
            candidates = response.get("candidates")
            if not candidates or len(candidates) == 0:
                yield "⚠️ Google tidak memberikan jawaban (Mungkin terfilter/Safety)."
                return

            try:
                text = candidates[0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                yield "❌ Gagal memproses format respons Gemini."
                return

            if not stream:
                yield text
                return
                
            # Simulate streaming by yielding chunks
            words = text.split()
            buffer = []
            for word in words:
                buffer.append(word)
                if len(' '.join(buffer)) > 20:  # Adjust chunk size as needed
                    yield ' '.join(buffer) + ' '
                    buffer = []
            if buffer:
                yield ' '.join(buffer)

        elif provider == "deepseek":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream
            }
            if not stream:
                response = await async_searcher(
                    ENDPOINTS[provider],
                    headers=headers,
                    post=True,
                    json=data,
                    re_json=True
                )
                yield response["choices"][0]["message"]["content"]
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    ENDPOINTS[provider],
                    headers=headers,
                    json=data
                ) as resp:
                    async for line in resp.content:
                        if line:
                            try:
                                json_line = json.loads(line.decode('utf-8').strip())
                                if 'choices' in json_line and json_line['choices']:
                                    content = json_line['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content
                            except Exception:
                                continue

    except Exception as e:
        LOGS.exception(e)
        yield f"Error: {str(e)}"


@ultroid_cmd(pattern="gemini( (.*)|$)")
async def gemini_ai(event):
    """Use Google Gemini"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    api_key = udB.get_key("GEMINI_API_KEY")
    if not api_key:
        return await event.eor("⚠️ Please set Gemini API key using `setdb GEMINI_API_KEY your_api_key`")

    msg = await event.eor(f"<blockquote>🤔 Thinking...</blockquote>", parse_mode="html")
    model = get_model("gemini")
    
    header = (
        f"<blockquote>🔍 Prompt:\n{prompt}</blockquote>\n"
        "<blockquote>💡 Response:</blockquote>\n"
    )
    
    if event.client.me.bot:
        await msg.edit(header)
        response = ""
        async for chunk in get_ai_response("gemini", prompt, api_key, stream=False):
            response += chunk
            try:
                await msg.edit(header + f"<blockquote>{response}</blockquote>", parse_mode="html")
            except Exception:
                pass
    else:
        response = ""
        async for chunk in get_ai_response("gemini", prompt, api_key, stream=False):
            response += chunk
        try:
            await msg.edit(header + f"<blockquote>{response}</blockquote>", parse_mode="html")
        except Exception:
            pass

@ultroid_cmd(pattern="antr( (.*)|$)")
async def anthropic_ai(event):
    """Use Anthropic Claude"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    api_key = udB.get_key("ANTHROPIC_KEY")
    if not api_key:
        return await event.eor("⚠️ Please set Anthropic API key using `setdb ANTHROPIC_KEY your_api_key`")

    msg = await event.eor("🤔 Thinking...")
    model = get_model("antr")
    
    formatted_response = (
        "🧠 **Anthropic Claude**\n"
        f"**Model:** `{model}`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**🔍 Prompt:**\n{prompt}\n\n"
        f"**💡 Response:**\n"
    )
    
    if event.client.me.bot:
        await msg.edit(formatted_response)
        response = ""
        async for chunk in get_ai_response("antr", prompt, api_key, stream=True):
            response += chunk
            try:
                await msg.edit(formatted_response + response)
            except Exception:
                pass
    else:
        response = ""
        async for chunk in get_ai_response("antr", prompt, api_key, stream=True):
            response += chunk
        try:
            await msg.edit(formatted_response + response)
        except Exception:
            pass

@ultroid_cmd(pattern="gpt( (.*)|$)")
async def openai_ai(event):
    """Use OpenAI GPT"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    api_key = udB.get_key("OPENAI_API_KEY")
    if not api_key:
        return await event.eor("⚠️ Please set GPT API key using `setdb OPENAI_API_KEY your_api_key`")

    msg = await event.eor("🤔 Thinking...")
    model = get_model("gpt")
    
    header = (
        "🌟 **OpenAI GPT**\n"
        f"**Model:** `{model}`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**🔍 Prompt:**\n{prompt}\n\n"
        "**💡 Response:**\n"
    )
    
    if event.client.me.bot:
        await msg.edit(header)
        response = ""
        async for chunk in get_ai_response("gpt", prompt, api_key, stream=True):
            response += chunk
            try:
                await msg.edit(header + response)
            except Exception:
                pass
    else:
        response =""
        async for chunk in get_ai_response("gpt", prompt, api_key, stream=True):
            response += chunk
        try:
            await msg.edit(header + response)
        except Exception:
            pass

@ultroid_cmd(pattern="deepseek( (.*)|$)")
async def deepseek_ai(event):
    """Use DeepSeek AI"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    api_key = udB.get_key("DEEPSEEK_API_KEY")
    if not api_key:
        return await event.eor("⚠️ Please set DeepSeek API key using `setdb DEEPSEEK_API_KEY your_api_key`")

    msg = await event.eor("🤔 Thinking...")
    model = get_model("deepseek")
    
    formatted_response = (
        "🤖 **DeepSeek AI**\n"
        f"**Model:** `{model}`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**🔍 Prompt:**\n{prompt}\n\n"
        f"**💡 Response:**\n"
    )
    
    if event.client.me.bot:
        await msg.edit(formatted_response)
        response = ""
        async for chunk in get_ai_response("deepseek", prompt, api_key, stream=True):
            response += chunk
            try:
                await msg.edit(formatted_response + response)
            except Exception:
                pass
    else:
        response = ""
        async for chunk in get_ai_response("deepseek", prompt, api_key, stream=True):
            response += chunk

        try:
            await msg.edit(formatted_response + response)
        except Exception:
            pass


@in_pattern("gemini( (.*)|$)")
async def gemini_inline_query(event):
    """Inline query for Google Gemini"""
    prompt = event.pattern_match.group(1).strip()
    if not prompt:
        return await event.answer(
    [
        InlineQueryResultArticle(
            title="Error",  # Title for the inline result
            description="Please provide a prompt!", # Description (optional, but good for context)
            input_message_content=InputTextMessageContent("❌ Please provide a prompt!"), # The actual message sent when user selects this result
        )
    ],
    cache_time=0
        )
        
    api_key = udB.get_key("GEMINI_API_KEY")
    if not api_key:
        return await event.answer("⚠️ Please set Gemini API key using `setdb GEMINI_API_KEY your_api_key`", cache_time=0)

    await event.answer([
        {
            "title": "Ask Gemini",
            "description": f"Ask Gemini: {prompt}",
            "thumb": "https://telegra.ph/file/111059e7943d699e126e8.jpg", # Ganti dengan URL thumbnail yang sesuai
            "input_message": f"<blockquote>🤔 Thinking...</blockquote>",
            "reply_markup": [
                [Button.inline("Get Gemini Response", data=f"gemini_ask_{prompt}")]
            ]
        }
    ], cache_time=0)


@callback("gemini_ask_( (.*)|$)")
async def gemini_callback_query(event):
    """Callback query for Google Gemini"""
    prompt = event.pattern_match.group(1)
    
    api_key = udB.get_key("GEMINI_API_KEY")
    if not api_key:
        return await event.answer("⚠️ Please set Gemini API key using `setdb GEMINI_API_KEY your_api_key`", cache_time=0)

    msg = await event.edit(f"<blockquote>🤔 Thinking...</blockquote>", parse_mode="html")
    
    header = (
        f"<blockquote>🔍 Prompt:\n{prompt}</blockquote>\n"
        "<blockquote>💡 Response:</blockquote>\n"
    )
    
    response = ""
    async for chunk in get_ai_response("gemini", prompt, api_key, stream=False):
        response += chunk
    
    try:
        await msg.edit(header + f"<blockquote>{response}</blockquote>", parse_mode="html")
    except Exception:
        pass
