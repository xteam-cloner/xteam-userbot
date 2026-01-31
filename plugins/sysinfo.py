"""
✘ Commands Available -

• `{i}sinfo`
    __Get all information about the server.__
"""

import os
import platform
import sys

import psutil
from xteam.fns.helper import humanbytes
from xteam.version import __version__ as UltVer
from telethon import __version__ as TelethonVer
from . import *

def find_lib_version(lib: str) -> str:
    """Find the version of a Python library installed via pip."""
    try:
        result = os.popen(f"python3 -m pip freeze | grep '^{lib}=='").read().strip()
        return result.split("==")[1] if result else "Not Installed"
    except IndexError:
        return "Not Installed"


def escape_html(text: str) -> str:
    """Escape special characters in HTML."""
    return text.replace("<", "").replace(">", "")


def get_system_info():
    """Get system-related information like CPU, RAM, and OS details."""
    try:
        cpu_cores = psutil.cpu_count(logical=True) or "n/a"
        cpu_percent = psutil.cpu_percent() or "n/a"
        ram_used = humanbytes(psutil.virtual_memory().used)
        ram_total = humanbytes(psutil.virtual_memory().total)
        ram_percent = psutil.virtual_memory().percent or "n/a"
        disk_used = humanbytes(psutil.disk_usage("/").used)
        disk_total = humanbytes(psutil.disk_usage("/").total)
        disk_percent = humanbytes(psutil.disk_usage("/").percent) or "n/a"
        kernel = escape_html(platform.release())
        architecture = escape_html(platform.architecture()[0])
        return (
            cpu_cores,
            cpu_percent,
            ram_used,
            ram_total,
            ram_percent,
            disk_used,
            disk_total,
            disk_percent,
            kernel,
            architecture,
        )
    except Exception:
        return ["n/a"] * 10


def get_os_info():
    """Get operating system distribution information."""
    try:
        system = os.popen("cat /etc/*release").read()
        b = system[system.find("PRETTY_NAME=") + 13 : -1]
        system = b[: b.find('"')]
        return escape_html(system)
    except Exception:
        return "N/A"


def get_python_info():
    """Get Python and pip version information."""
    try:
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        pip_version = os.popen("python3 -m pip --version").read().split()[1]
        return python_version, pip_version
    except Exception:
        return "n/a", "n/a"


def bandwidth():
    try:
        download = 0
        upload = 0
        for net_io in psutil.net_io_counters(pernic=True).values():
            download += net_io.bytes_recv
            upload += net_io.bytes_sent
        up = humanbytes(upload)
        down = humanbytes(download)
        total = humanbytes(upload + download)
        return up, down, total
    except:
        return ["N/A"] * 3


# Text template for displaying server info
INFO_TEMPLATE = (
    "<b><u><blockquote>👾 Server Info:</blockquote></u>\n"
    "<u><blockquote>🗄 Used resources:</u>\n"
    "    CPU: {} Cores ({}%)\n"
    "    RAM: {} / {} ({}%)\n"
    "    DISK: {} / {} ({}%)\n\n</blockquote>"
    "<u><blockquote>🌐 Network Stats:</u>\n"
    "    Upload: {}\n"
    "    Download: {}\n"
    "    Total: {}\n\n</blockquote>"
    "<u><blockquote>🧾 Dist info:</u>\n"
    "    Kernel: {}\n"
    "    Arch: {}\n"
    "    OS: {}\n\n</blockquote>"
    "<u><blockquote>📦 Python libs:</u>\n"
    "    Telethon: {}\n"
    "    Aiohttp: {}\n"
    "    GitPython: {}\n"
    "    Xteam: {}\n"
    "    Python: {}\n"
    "    Pip: {}</b></blockquote>"
)


@ultroid_cmd(pattern="sinfo$")
async def serverinfo_cmd(message):
    """server information."""
    await message.edit("<b><i><blockquote>🔄 Getting server info...</i></b></blockquote>", parse_mode="html")

    (
        cpu_cores,
        cpu_percent,
        ram_used,
        ram_total,
        ram_percent,
        disk_used,
        disk_total,
        disk_percent,
        kernel,
        architecture,
    ) = get_system_info()
    os_info = get_os_info()
    python_version, pip_version = get_python_info()
    up, down, total = bandwidth()

    telethon_version = TelethonVer
    aiohttp_version = find_lib_version("aiohttp")
    gitpython_version = find_lib_version("GitPython")
    xteam_version = UltVer

    # Format the final text
    info_text = INFO_TEMPLATE.format(
        cpu_cores,
        cpu_percent,
        ram_used,
        ram_total,
        ram_percent,
        disk_used,
        disk_total,
        disk_percent,
        up,
        down,
        total,
        kernel,
        architecture,
        os_info,
        telethon_version,
        aiohttp_version,
        gitpython_version,
        xteam_version,
        python_version,
        pip_version,
    )

    await message.eor(info_text, parse_mode="html")
