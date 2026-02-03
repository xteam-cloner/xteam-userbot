from . import eor, SUDO_HNDLR as PREFIX, ultroid_cmd
from os import mkdir, listdir as ls
from xteam.fns.helper import inline_mention
from . import HNDLR as PREFIX, get_string, inline_mention, udB, ultroid_bot, ultroid_cmd, eor, SUDO_HNDLR

@ultroid_cmd(pattern="fsudo")
async def szudo(e):
  reply = await e.get_reply_message()
  rid = "{}".format(reply.sender_id)
  udB.set_key("SUDOS",list(rid))
  udB.set_key("FULLSUDO",rid)
  name = await e.client.get_entity(int(rid))
  una = name.username
  fn = name.first_name
  ln = name.last_name
  men = inline_mention(name)
  ii = udB.get_key("FULLSUDO")
  await e.reply(f"""**Added** {men} **as FULLSUDO and SUDO User**

First name : {fn}
Last name : {ln}
id : {ii}
username : {una}
HNDLR : {PREFIX}
SUDO_HNDLR : {PREFIX}
""")


from xteam._misc import sudoers


@ultroid_cmd(
    pattern="su$",
)
async def _(ult):
    x = await ult.eor("**Adding Sudo or Fullsodo.....**")
    n = udB.get_key("SUDOS") or []
    async for m in ult.client.iter_participants(ult.chat_id):
      if not (m.bot or m.deleted):
        n.append(m.id)

    n = list(set(n))
    udB.set_key('SUDOS', n)
    udB.set_key('FULLSUDO', " ".join(str(i) for i in n))
    reply_to_id = ult.reply_to_msg_id or ult.id
    await x.edit(f"""
<b>List of Sudo and Fullsudo users</b>
<pre>1. All members in this group</pre>

<b>Info</b>
<pre>My <code>HNDLR : {PREFIX}</code>
My <code>SUDO_HNDLR : {PREFIX}</code>
</pre>
<b>List of some commands<b>
<pre>1. ping
2. alive
3. eval
4. bash
5. sysinfo
6. rename
7. web
8. writer
9. upscale 
10. load
11. send = cd
12. sg
13. help
14. restart
15. open
16. speedtest
17. del
</pre>
""",parse_mode="html")
  
