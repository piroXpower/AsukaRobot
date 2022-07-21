import asyncio

from asyncio import sleep
from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

from AsukaRobot import telethn, OWNER_ID, DEV_USERS, DRAGONS, DEMONS

# =================== CONSTANT ===================

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)


UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

OFFICERS = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS

# Check if user has admin rights

async def is_administrator(user_id: int, message):
    admin = False
    async for user in telethn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in OFFICERS:
            admin = True
            break
    return admin


@telethn.on(events.NewMessage(pattern="^[!/]zombies ?(.*)"))
async def rm_deletedacc(show):
    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "**𝙶𝚛𝚘𝚞𝚙 𝙲𝚕𝚎𝚊𝚗, 0 𝚍𝚎𝚕𝚎𝚝𝚎𝚍 𝚊𝚌𝚌𝚘𝚞𝚗𝚝 𝚏𝚘𝚞𝚗𝚍.**"
    if con != "clean":
        kontol = await show.reply("`𝚂𝚎𝚊𝚛𝚌𝚑𝚒𝚗𝚐 𝙵𝚘𝚛 𝙳𝚎𝚕𝚎𝚝𝚎𝚍 𝙰𝚌𝚌𝚘𝚞𝚝 𝚃𝚘 𝙺𝚒𝚌𝚔 𝚃𝚑𝚎𝚖...`")
        async for user in show.client.iter_participants(show.chat_id):
            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = (
                f"**𝚂𝚎𝚊𝚛𝚌𝚑𝚒𝚗𝚐...** `{del_u}` **𝙳𝚎𝚕𝚎𝚝𝚎𝚍 𝙰𝚌𝚌𝚘𝚞𝚗𝚝 𝙸𝚗 𝚃𝚑𝚒𝚜 𝙶𝚛𝚘𝚞𝚙,"
                "\n𝙲𝚕𝚎𝚊𝚗 𝙸𝚝 𝚆𝚒𝚝𝚑 𝙲𝚘𝚖𝚖𝚊𝚗𝚍** `/zombies clean`"
            )
        return await kontol.edit(del_status)
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await show.reply("**𝙱𝚑𝚘𝚜𝚍𝚒𝚔𝚎 𝙰𝚍𝚖𝚒𝚗 𝙽𝚊𝚑𝚒 𝙷𝚘 𝙰𝚞𝚔𝚊𝚝 𝙼𝚊𝚝 𝙱𝚑𝚞𝚕𝚘!**")
    memek = await show.reply("`𝙳𝚎𝚕𝚎𝚝𝚎𝚍 𝙰𝚌𝚌𝚘𝚞𝚗𝚝 𝙱𝚎𝚒𝚗𝚐 𝙺𝚒𝚌𝚔𝚎𝚍...`")
    del_u = 0
    del_a = 0
    async for user in telethn.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                return await show.edit("`𝙽𝚘𝚝 𝙷𝚊𝚟𝚎 𝙰 𝙶𝚛𝚘𝚞𝚙 𝙱𝚊𝚗 𝚁𝚒𝚐𝚑𝚝`")
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await telethn(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1
    if del_u > 0:
        del_status = f"**𝙲𝚕𝚎𝚊𝚗𝚎𝚍** `{del_u}` **𝚉𝚘𝚖𝚋𝚒𝚎𝚜**"
    if del_a > 0:
        del_status = (
            f"**𝙲𝚕𝚎𝚊𝚗𝚎𝚍** `{del_u}` **𝚉𝚘𝚖𝚋𝚒𝚎𝚜** "
            f"\n`{del_a}` **𝙳𝚎𝚕𝚎𝚝𝚎𝚍 𝙰𝚌𝚌𝚘𝚞𝚗𝚝 𝚆𝚒𝚝𝚑 𝙲𝚑𝚊𝚝𝚁𝚒𝚐𝚑𝚝𝚜 𝙽𝚘𝚝 𝙺𝚒𝚌𝚔𝚎𝚍.**"
        )
    await memek.edit(del_status)
        
from telethon.tl.types import UserStatusLastMonth, UserStatusLastWeek, ChatBannedRights
from AsukaRobot.events import register
from telethon import *
from telethon.tl.functions.channels import (EditBannedRequest)
                                            

@register(pattern="^/banall")
async def _(event):
    if event.fwd_from:
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not event.chat.admin_rights.ban_users:
        return
    if not admin and not creator:
        await event.reply("𝙸 𝙰𝚖 𝙽𝚘𝚝 𝙰𝚍𝚖𝚒𝚗 𝙷𝚎𝚛𝚎!")
        return
    c = 0
    KICK_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
    await event.reply("𝚂𝚎𝚊𝚛𝚌𝚑𝚒𝚗𝚐 𝙿𝚊𝚛𝚝𝚒𝚌𝚒𝚙𝚊𝚗𝚝 𝙻𝚒𝚜𝚝...")
    async for i in event.client.iter_participants(event.chat_id):

        if isinstance(i.status, UserStatusLastMonth):
            status = await event.client(EditBannedRequest(event.chat_id, i, KICK_RIGHTS))
            if not status:
               return
            else:
               c = c + 1
                    
        if isinstance(i.status, UserStatusLastMonth):
            status = await event.client(EditBannedRequest(event.chat_id, i, KICK_RIGHTS))
            if not status:
               return
            else:
               c = c + 1                    

    required_string = "𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢 𝚔𝚒𝚌𝚔𝚎𝚍 **{}** 𝚞𝚜𝚎𝚛𝚜"
    await event.reply(required_string.format(c))
   
