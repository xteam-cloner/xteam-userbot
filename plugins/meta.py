import requests
from . import *
from telethon import events

@ultroid_cmd(pattern="metaim")
async def buat_gambar(event):
    if event.text[1:].split():
        # Get the API Key from the database/config
        llama_api_key = udB.get_key("LLAMA_API_KEY") 
        if not llama_api_key:
            await event.respond("LLAMA_API_KEY tidak ditemukan di database.")
            return

        prompt = event.text[1:].split(' ', 1)[1]
        
        response = requests.post(
            url="https://api.llama.com/v1/images/generations",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llama_api_key}"
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "prompt": prompt,
                "size": "1024x1024"
            }
        )
        
        # Add error handling for the API response
        try:
            image_url = response.json()["data"][0]["url"]
            await event.respond(file=image_url)
        except (KeyError, IndexError):
            await event.respond(f"Gagal mendapatkan URL gambar dari API. Respons: {response.text}")

    else:
        await event.respond("Mohon masukkan prompt!")


import requests
from . import *
from telethon import events

@ultroid_cmd(pattern="meta")
async def meta_ai(event):
    if event.text[1:].split():
        # Get the API Key from the database/config
        llama_api_key = udB.get_key("LLAMA_API_KEY") 
        if not llama_api_key:
            await event.respond("LLAMA_API_KEY tidak ditemukan di database.")
            return

        prompt = event.text[1:].split(' ', 1)[1]
        
        response = requests.post(
            url="https://api.llama.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llama_api_key}"
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        # Add error handling for the API response
        try:
            content = response.json()["choices"][0]["message"]["content"]
            await event.respond(content)
        except (KeyError, IndexError):
            await event.respond(f"Gagal mendapatkan respons chat dari API. Respons: {response.text}")
            
    else:
        await event.respond("Mohon masukkan prompt!")
        
