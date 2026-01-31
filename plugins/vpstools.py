import os
import shutil
import psutil
from datetime import datetime
from . import ultroid_cmd, get_string

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

@ultroid_cmd(pattern="clean$")
async def clean_vps(event):
    if not event.out:
        return await event.edit("`Admin privileges required!`")

    msg = await event.edit("🧹 **Starting VPS Cleanup...**")
    
    dl_path = "downloads"
    dl_note = ""
    if os.path.exists(dl_path):
        try:
            shutil.rmtree(dl_path)
            os.makedirs(dl_path)
            dl_note = "✅ **Downloads:** Folder cleared\n"
        except Exception as e:
            dl_note = f"❌ **Downloads:** Failed to clear ({str(e)})\n"
    else:
        dl_note = "ℹ️ **Downloads:** Folder not found\n"

    try:
        os.system("sync && echo 3 > /proc/sys/vm/drop_caches")
        os.system("pip cache purge")
        os.system("apt-get autoclean -y && apt-get autoremove -y")
        
        await msg.edit(
            "✅ **Cleanup Successful!**\n\n"
            f"{dl_note}"
            "• **RAM Cache:** Flushed\n"
            "• **Pip Cache:** Purged\n"
            "• **System APT:** Autoclean & Autoremove done"
        )
    except Exception as e:
        await msg.edit(f"❌ **Cleanup Failed:**\n`{str(e)}` \n\n*Make sure the bot has root/sudo access.*")

@ultroid_cmd(pattern="sysinfo$")
async def sys_info(event):
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_hours = int(uptime_seconds // 3600)
    
    def make_bar(perc):
        dashes = int(perc / 10)
        return f"[{'●' * dashes}{'○' * (10 - dashes)}]"

    info = (
        "🖥 **VPS Server Status**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **RAM:** {make_bar(ram.percent)} `{ram.percent}%` \n"
        f"   (Used: {get_size(ram.used)} / {get_size(ram.total)})\n\n"
        f"💽 **Disk:** {make_bar((disk.used/disk.total)*100)} \n"
        f"   (Used: {get_size(disk.used)} / {get_size(disk.total)})\n\n"
        f"⏳ **Uptime:** `{uptime_hours} Hours`\n"
        f"🕒 **Time:** `{datetime.now().strftime('%H:%M:%S')}`"
    )
    await event.edit(info)
    
