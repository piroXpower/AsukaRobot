import time
import requests
import importlib
from sys import argv
import re
import os
import random
import platform
import asyncio
from typing import List
from typing import Optional
from pyrogram import Client, idle, filters

import AsukaRobot.modules.sql.users_sql as sql
from AsukaRobot.modules.sudoers import bot_sys_stats as bss

from AsukaRobot import (ALLOW_EXCL, CERT_PATH, DONATION_LINK, LOGGER,
                          OWNER_ID, PORT, SUPPORT_CHAT, TOKEN, URL, WEBHOOK,
                          SUPPORT_CHAT, dispatcher, StartTime, telethn, updater, pgram, pbot)
# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from AsukaRobot.modules import ALL_MODULES
from AsukaRobot.modules.helper_funcs.chat_status import is_user_admin
from AsukaRobot.modules.helper_funcs.misc import paginate_modules
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.error import (BadRequest, ChatMigrated, NetworkError,
                            TelegramError, TimedOut, Unauthorized)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          Filters, MessageHandler)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

PM_START_TEXT = """
*𝙷𝙴𝙻𝙻𝙾 {},*
*𝙼𝚈 𝙽𝙰𝙼𝙴 𝙸𝚂 {bn}, 𝙰 𝙿𝙾𝚆𝙴𝚁𝙵𝚄𝙻 𝚂𝙼𝙰𝚁𝚃 𝙶𝚁𝙾𝚄𝙿 𝚁𝙾𝙱𝙾𝚃\n𝚆𝙸𝚃𝙷 𝙼𝙰𝙽𝚈 𝙰𝙼𝙰𝚉𝙸𝙽𝙶 𝙵𝙴𝙰𝚃𝚄𝚁𝙴𝚂. 𝙸 𝙲𝙰𝙽 𝙷𝙴𝙻𝙿 𝚈𝙾𝚄 𝚃𝙾 𝙼𝙰𝙽𝙰𝙶𝙴 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿𝚂,\n𝙹𝚄𝚂𝚃 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿 𝙰𝙽𝙳 𝙴𝙽𝙹𝙾𝚈.*
"""

buttons = [
    [
                        InlineKeyboardButton(
                             text="➕️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ➕️",
                             url="https://t.me/innexiabot?startgroup=true"),
                    ],
                   [
                       InlineKeyboardButton(
                             text="ʜᴇʟᴘ",
                             callback_data="help_back"),
                       InlineKeyboardButton(
                             text="ᴀʙᴏᴜᴛ ᴍᴇ",
                             callback_data="asuka_"),
                   ],
                  [
                        InlineKeyboardButton(
                             text="sᴜᴘᴘᴏʀᴛɪᴠᴇ ɴᴇᴛᴡᴏʀᴋ",
                             url="https://t.me/DEADLY_SPONSER"),
                    ],
    ]

ABOUT1 = """
𝙷𝚎𝚢 𝚃𝚑𝚒𝚜 𝙸𝚜 innexia 𝙿𝚘𝚠𝚎𝚛𝚎𝚍 𝙱𝚢 𝙳𝚎𝚊𝚍𝚕𝚢\n𝙼𝚊𝚍𝚎 𝚆𝚒𝚝𝚑 𝙻𝚘𝚟𝚎 𝙱𝚢 𝙱𝚕𝚊𝚣𝚎 𝙵𝚘𝚛 𝙼𝚊𝚗𝚊𝚐𝚒𝚗𝚐 𝙶𝚛𝚘𝚞𝚙𝚜\n\n══════════════════\n\n.
"""

ABOUT2 = """
*‣ Asuka Support Chats*\nJoin My Support Group/Channel For Reporting Problems And Updates On @AsukaRobot.
"""

REPO_TXT = """
*‣ Owner:*
• [Xelcius](t.me/xelcius)
\n*‣ Note:*
• If You Want This Bot's Repo You Can Get It From The Button Below.
• Report Any Kind Of Bugs At [Support](t.me/AsukaSupport)
"""

ABOUT3 = """
**★ 𝙼𝚈 𝙽𝙰𝙼𝙴:** [𝙸𝙽𝙽𝙴𝚇𝙸𝙰](t.me/innexiaBot)\n**★ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁:** [𝙱𝙻𝙰𝚉𝙴-𝙾𝙿](t.me/trex_2_0)\n**★ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈:** [𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼](https://docs.pyrogram.org/)\n**★ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴:** [𝙿𝚈𝚃𝙷𝙾𝙽 𝟹](https://www.python.org/)\n**★ 𝙱𝙾𝚃 𝚂𝙴𝚁𝚅𝙴𝚁:** [𝙷𝙴𝚁𝙾𝙺𝚄](https://heroku.com)\n**★ 𝙱𝚄𝙸𝙻𝙳 𝚂𝚃𝙰𝚃𝚄𝚂:** v2.0 [𝚄𝙿𝙳𝙰𝚃𝙴-𝙻𝙸𝚂𝚃](https://t.me/DEADLY_BOTS)
"""
HELP_STRINGS = "𝙷𝙴𝚈.\n𝙷𝙴𝚁𝙴 𝙸𝚂 𝙼𝚈 𝙷𝙴𝙻𝙿 𝙼𝙴𝙽𝚄 𝙵𝙾𝚁 𝚈𝙾𝚄:"



TEXXT = "🙋‍♀️ 𝙷𝙴𝚈 ., \n𝙸𝙽𝙽𝙴𝚇𝙸𝙰 𝙷𝙴𝚁𝙴 :) 𝙿𝙼 𝙼𝙴 𝙸𝙵 𝚈𝙾𝚄 𝙷𝙰𝚅𝙴 𝙰𝙽𝚈 𝚀𝚄𝙴𝚂𝚃𝙸𝙾𝙽𝚂 𝙾𝚁 𝙳𝙾𝚄𝙱𝚃𝚂 𝙰𝙱𝙾𝚄𝚃 𝚄𝚂𝙸𝙽𝙶 𝙼𝙴!",

PHOTO = (
      "https://telegra.ph/file/0b5e88c90238c357641a7.jpg",
      "https://telegra.ph/file/3c93a66c6751088a00fbd.jpg",
      "https://telegra.ph/file/3b4eed00be4dfaa189fff.jpg",
      "https://telegra.ph/file/6cbc8452a2796ad58c2f9.jpg",
      "https://telegra.ph/file/3c6cb9b50381170c95278.jpg"

)

DONATE_STRING = """ Adding Me To Your Groups Is Donation For Me Though I Would Appreciate If You Join My Creator's Network @TheKaizuryu"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("AsukaRobot.modules." +
                                              module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception(
            "Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "get_help") and imported_module.get_help:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_photo(
        chat_id=chat_id,
        photo=(PM_PHOTO),
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard)



@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS.format(escape_markdown(update.effective_user.first_name), update.effective_user.id))
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                xx = HELPABLE[mod].get_help(chat)
                if isinstance(xx, list):
                    txt = str(xx[0])
                    kb = [xx[1], [InlineKeyboardButton(text="Back", callback_data="help_back")]]
                else:
                    txt = str(xx)
                    kb = [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                send_help(
                    update.effective_chat.id,
                    txt,
                    InlineKeyboardMarkup(kb),
                )
            elif args[0].lower() == "markdownhelp":
                IMPORTED["extras"].markdown_help_sender(update)
            elif args[0].lower() == "disasters":
                IMPORTED["disasters"].send_disasters(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(
                        match.group(1), update.effective_user.id, False)
                else:
                    send_settings(
                        match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.full_name
            id = update.effective_user.id

            update.effective_message.reply_photo(
                photo=random.choice{PHOTO},
                caption=PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    platform.python_version(),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        first = update.effective_user.full_name
        chat = update.effective_chat.title
        update.effective_message.reply_text(
            text=TEXXT,
            parse_mode=ParseMoxt):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove u   except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors

@run_async
def help_button(update, context):
    query = update.callback_query
    bot = context.bot
    chat = update.effective_chat
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            module = module.replace("_", " ")
            help_list = HELPABLE[module].get_help(update.effective_chat.id)
            if isinstance(help_list, list):
                help_text = help_list[0]
                help_buttons = help_list[1:]
            elif isinstance(help_list, str):
                help_text = help_list
                help_buttons = []
            text = (
                    "Here is the help for the *{}* module:\n".format(
                        HELPABLE[module].__mod_name__
                    )
                    + help_text
            )
            help_buttons.append(
                [
                    InlineKeyboardButton(text="Back", callback_data="help_back"),
                    InlineKeyboardButton(text='Support', url='https://t.me/AsukaSupport')
                ]
                    )
            query.message.edit_caption(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(help_buttons),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_caption(
                HELP_STRINGS.format(update.effective_user.first_name, update.effective_user.id),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_caption(
                HELP_STRINGS.format(update.effective_user.first_name, update.effective_user.id),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            query.message.edit_caption(
                HELP_STRINGS.format(update.effective_user.first_name, update.effective_user.id),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@run_async
def about_callback_data(update, context):
    query = update.callback_query
    bot = context.bot
    uptime = get_readable_time((time.time() - StartTime))
    if query.data == "about_":
        query.message.edit_caption(
            ABOUT1,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="asuka_")
                 ],
                ]
            ),
        )
    elif query.data == "about_back":
        first_name = update.effective_user.first_name
        user_name = update.effective_user.username
        query.message.edit_caption(
            ABOUT2,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Support", url="t.me/AsukaSupport"),
                    InlineKeyboardButton(text="Updates", url="t.me/AsukaUpdates"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="asuka_")
                 ],
                ]
            ),
        )

@run_async
def repo_callback_data(update, context):
    query = update.callback_query
    bot = context.bot
    uptime = get_readable_time((time.time() - StartTime))
    if query.data == "repo_":
        query.message.edit_caption(
            REPO_TXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Source Code", url="https://github.com/RimuruDemonlord/AsukaRobot"),
                    InlineKeyboardButton(text="Kaizuryu", url="t.me/TheKaizuryu"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="asuka_")
                 ],
                ]
            ),
        )
    elif query.data == "repo_back":
        first_name = update.effective_user.first_name
        user_name = update.effective_user.username
        query.message.edit_caption(
            "Test"
        )

@run_async
def asuka_callback_data(update, context):
    query = update.callback_query
    bot = context.bot
    uptime = get_readable_time((time.time() - StartTime))
    if query.data == "asuka_":
        query.message.edit_caption(
            ABOUT3.format(update.effective_user.first_name, update.effective_user.id, escape_markdown(context.bot.first_name)),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Try Inline", switch_inline_query_current_chat=""),
                    InlineKeyboardButton(text="Developer", url="t.me/Xelcius"),
                 ],
                 [
                    InlineKeyboardButton(text="Support", callback_data="about_back"),
                    InlineKeyboardButton(text="Source Code", url="https://github.com/RimuruDemonlord/AsukaRobot"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="asuka_back")
                 ],
                ]
            ),
        )
    elif query.data == "asuka_back":
        first_name = update.effective_user.full_name
        id = update.effective_user.id
        query.message.edit_caption(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    platform.python_version(),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
        )

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            first_name = update.effective_user.full_name
            update.effective_message.reply_photo(
            random.choice(Asuka_N_IMG), caption= f"Hey {first_name}, Click the Button Below to get help of {module.capitalize()}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="click here",
                        url="t.me/{}?start=ghelp_{}".format(
                            context.bot.username, module))
                ]]))
            return

        first_name = update.effective_user.full_name
        first_nam = update.effective_user.id
        update.effective_message.reply_photo(
            random.choice(Asuka_N_IMG), caption= "Hey [{}](tg://user?id={}) Click the Button Below to get the list of possible commands.".format(first_name, first_nam),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                  InlineKeyboardButton(text=" Click here", url="https://t.me/AsukaRobot?start=help")
                  ]
                ]
            ),
        )
        return

    elif len(args) >= 2:
        if any(args[1].lower() == x for x in HELPABLE):
            mod = args[1].lower()
            text = (
                "Here is the available help for the *{}* module:\n".format(
                    HELPABLE[mod].__mod_name__
                )
                + str(HELPABLE[mod].get_help(chat))
            )
            xx = HELPABLE[mod].get_help(chat)
            if isinstance(xx, list):
                txt = str(xx[0])
                kb = [xx[1], [InlineKeyboardButton(text="Back", callback_data="help_back")]]
            else:
                txt = str(xx)
                kb = [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            send_help(
                update.effective_chat.id,
                txt,
                InlineKeyboardMarkup(kb),
            )
        else:
            update.effective_message.reply_text(
                f"<code>{args[1].lower()}</code> is not a module",
                parse_mode=ParseMode.HTML,
            )
    else:
        send_help(update.effective_chat.id, HELP_STRINGS.format(update.effective_user.first_name, update.effective_user.id))


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join("*{}*:\n{}".format(
                mod.__mod_name__, mod.__user_settings__(user_id))
                                   for mod in USER_SETTINGS.values())
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN)

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN)

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                "Which module would you like to check {}'s settings for?"
                .format(chat_name),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN)


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(escape_markdown(chat.title),
                                                                                     CHAT_SETTINGS[module].__mod_name__) + \
                   CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_photo(
                photo=random.choice(PM_PHOTO),
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Back",
                        callback_data="stngs_back({})".format(chat_id))
                ]]))

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_photo(
                photo=random.choice(PM_PHOTO),
                caption="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_photo(
                photo=random.choice(PM_PHOTO),
                caption="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_photo(
                photo=random.choice(PM_PHOTO),
                caption="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in settings buttons. %s",
                             str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_photo(
                random.choice(Asuka_N_IMG), caption=text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Settings",
                        url="t.me/{}?start=stngs_{}".format(
                            context.bot.username, chat.id))
                ]]))
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@pgram.on_callback_query(filters.regex("pingCB"))
async def pingCB(_, CallbackQuery):
    uptime = get_readable_time((time.time() - StartTime))
    text = f"Haven't Slept Since {uptime}"
    await pgram.answer_callback_query(CallbackQuery.id, text)

@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

        if OWNER_ID != 5132611794 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN)

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)

            update.effective_message.reply_text(
                "I've PM'ed you about donating!")
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information.")


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            name = dispatcher.bot.first_name
            m = dispatcher.bot.send_photo(f"@{SUPPORT_CHAT}", Asuka_DISPACHER_PIC, caption=f"*{name} Started!\n• Evangelion Unit-02 Booted Up!\n*• Let's Get The Party Started!", parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                       InlineKeyboardButton(
                             text="Off-Topic",
                             url="https://t.me/Anime_Chat_XKaizuryu")
                     ]
                ]
            ),
        )
        except Unauthorized:
            LOGGER.warning(
                "Asuka can't able to send message to support_chat, go and check!")
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(asuka_callback_data, pattern=r"asuka_")
    asuka_callback_handler = CallbackQueryHandler(about_callback_data, pattern=r"about_")
    repo_callback_handler = CallbackQueryHandler(repo_callback_data, pattern=r"repo_")
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate,
                                     migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(repo_callback_handler)
    dispatcher.add_handler(asuka_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="127.0.0.1", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(
                url=URL + TOKEN, certificate=open(CERT_PATH, 'rb'))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Finally Asuka Is Online")
        allowed_updates = ['message', 'edited_message', 'callback_query', 'callback_query', 'my_chat_member',
                           'chat_member', 'chat_join_request', 'channel_post', 'edited_channel_post', 'inline_query']
        updater.start_polling(
                timeout=15, read_latency=4, allowed_updates=allowed_updates, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
