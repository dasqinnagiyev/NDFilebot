# (c) @dasqinnagiyev

import os
import asyncio
import traceback
from binascii import Error
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, FloodWait, QueryIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from configs import Config
from handlers.database import db
from handlers.add_user_to_db import AddUserToDatabase
from handlers.send_file import SendMediaAndReply
from handlers.helpers import b64_to_str, str_to_b64
from handlers.check_user_status import handle_user_status
from handlers.force_sub_handler import handle_force_sub
from handlers.broadcast_handlers import main_broadcast_handler
from handlers.save_media import SaveMediaInChannel, SaveBatchMediaInChannel

MediaList = {}
Bot = Client(Config.BOT_USERNAME, bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH)


@Bot.on_message(filters.private)
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)


@Bot.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):

    if cmd.from_user.id in Config.BANNED_USERS:
        await cmd.reply_text("Sən ban olmusan :).")
        return
    if Config.UPDATES_CHANNEL is not None:
        back = await handle_force_sub(bot, cmd)
        if back == 400:
            return
    
    usr_cmd = cmd.text.split("_", 1)[-1]
    if usr_cmd == "/start":
        await AddUserToDatabase(bot, cmd)
        await cmd.reply_text(
            Config.HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Dəstək Grupu", url="https://t.me/dasqing"),
                        InlineKeyboardButton("DAQO MODS", url="https://t.me/daqomods")
                    ],
                    [
                        InlineKeyboardButton("Bot haqqında", callback_data="aboutbot"),
                        InlineKeyboardButton("Gəlişdirici haqqında", callback_data="aboutdevs")
                    ]
                ]
            )
        )
    else:
        try:
            try:
                file_id = int(b64_to_str(usr_cmd).split("_")[-1])
            except (Error, UnicodeDecodeError):
                file_id = int(usr_cmd.split("_")[-1])
            GetMessage = await bot.get_messages(chat_id=Config.DB_CHANNEL, message_ids=file_id)
            message_ids = []
            if GetMessage.text:
                message_ids = GetMessage.text.split(" ")
            else:
                message_ids.append(int(GetMessage.message_id))
            for i in range(len(message_ids)):
                await SendMediaAndReply(bot, user_id=cmd.from_user.id, file_id=int(message_ids[i]))
        except Exception as err:
            await cmd.reply_text(f"Bir şeylər tərs getdi!\n\n**Xəta:** `{err}`")


@Bot.on_message((filters.document | filters.video | filters.audio) & ~filters.edited & ~filters.chat(Config.DB_CHANNEL))
async def main(bot: Client, message: Message):

    if message.chat.type == "private":

        await AddUserToDatabase(bot, message)

        if Config.UPDATES_CHANNEL is not None:
            back = await handle_force_sub(bot, message)
            if back == 400:
                return

        if message.from_user.id in Config.BANNED_USERS:
            await message.reply_text("Sən ban olmusan!!\n\nƏlaqə [Dəstək grupu](https://t.me/dasqing)",
                                     disable_web_page_preview=True)
            return

        if Config.OTHER_USERS_CAN_SAVE_FILE is False:
            return
        await message.reply_text(
            text="**Aşağıdan bir seçim et:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Toplu olaraq saxla", callback_data="addToBatchTrue")],
                [InlineKeyboardButton("Paylaşım linki ver", callback_data="addToBatchFalse")]
            ]),
            quote=True,
            disable_web_page_preview=True
        )
    elif message.chat.type == "channel":
        if (message.chat.id == int(Config.LOG_CHANNEL)) or (message.chat.id == int(Config.UPDATES_CHANNEL)) or message.forward_from_chat or message.forward_from:
            return
        elif int(message.chat.id) in Config.BANNED_CHAT_IDS:
            await bot.leave_chat(message.chat.id)
            return
        else:
            pass

        try:
            forwarded_msg = await message.forward(Config.DB_CHANNEL)
            file_er_id = str(forwarded_msg.message_id)
            share_link = f"https://t.me/{Config.BOT_USERNAME}?start=dasqin_{str_to_b64(file_er_id)}"
            CH_edit = await bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                              "Paylaşım linki", url=share_link)]]))
            if message.chat.username:
                await forwarded_msg.reply_text(
                    f"#Kanal_düyməsi:\n\n[{message.chat.title}](https://t.me/{message.chat.username}/{CH_edit.message_id}) Kanalda Yayımlanan Fayllara Düymə Əlavə edildi!")
            else:
                private_ch = str(message.chat.id)[4:]
                await forwarded_msg.reply_text(
                    f"#Kanal_düyməsi:\n\n[{message.chat.title}](https://t.me/c/{private_ch}/{CH_edit.message_id}) Kanalda Yayımlanan Fayllara Düymə Əlavə edildi!")
        except FloodWait as sl:
            await asyncio.sleep(sl.x)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\n`{str(sl.x)}s` burda --> `{str(message.chat.id)}` Flood edir !!",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as err:
            await bot.leave_chat(message.chat.id)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#Xəta_geri_izləməsi:\n`{str(message.chat.id)}` burda xəta var !!\n\n**Geri izləmə:** `{err}`",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )


@Bot.on_message(filters.private & filters.command("toplumesaj") & filters.user(Config.BOT_OWNER) & filters.reply)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)


@Bot.on_message(filters.private & filters.command("vezyet") & filters.user(Config.BOT_OWNER))
async def sts(_, m: Message):
    total_users = await db.total_users_count()
    await m.reply_text(text=f"**DB-dəki ümumi istifadəçi sayı:** `{total_users}`", parse_mode="Markdown", quote=True)


@Bot.on_message(filters.private & filters.command("blok") & filters.user(Config.BOT_OWNER))
async def ban(c: Client, m: Message):
    
    if len(m.command) == 1:
        await m.reply_text(
            f"Hər hansı bir istifadəçini blok etmək üçün bu komandadan istifadə et.\n\n"
            f"İstifadə:\n\n"
            f"`/blok user_id blok_müddəti blok_səbəbi`\n\n"
            f"Məsələn: `/blok 1234567 28 xoşuma gəlmədin.`\n"
            f"Siz bu istifadəçini `1234567` , `28` günlük blok etdiniz. blok etmə səbəbi `Xoşuma gəlmədin`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Bu istifadəçi {user_id} blok edildi. blok müddəti {ban_duration} gün səbəbi {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"Sən **{ban_duration}** günlük blok edildin ({ban_duration} gün botu işlədə bilməyəcəksən) **Səbəbi:** __{ban_reason}__ \n\n"
                f"**Admindən Mesaj**"
            )
            ban_log_text += '\n\nİstifadəçiyə bildiriş göndərildi!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nİstifadəçiyə bildiriş göndərilmədi! \n\n`{traceback.format_exc()}`"

        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Xəta baş verdi! Geri izləmə aşağıda verilib\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("blokac") & filters.user(Config.BOT_OWNER))
async def unban(c: Client, m: Message):

    if len(m.command) == 1:
        await m.reply_text(
            f"İstifadəçini blokdan çıxarmaq üçün bu komandanı istifadə et.\n\n"
            f"İstifadə:\n\n`/blokac user_id`\n\n"
            f"Məsələn: `/blokac 1234567`\n"
            f"Bu istifadəçi `1234567` blokdan çıxacaq.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"İstifadəçi blokdan çıxarılır {user_id}"
        try:
            await c.send_message(
                user_id,
                f"Blokdan çıxarıldın!"
            )
            unban_log_text += '\n\nİstifadəçiyə bildiriş göndərildi!'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\nİstifadəçiyə bildiriş göndərilmədi! \n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Xəta baş verdi! Geri izləmə aşağıda verilib\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("bloklu") & filters.user(Config.BOT_OWNER))
async def _banned_users(_, m: Message):
    
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ''

    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Blok müddəti**: `{ban_duration}`, " \
                f"**Blok edilib**: `{banned_on}`, **Blok səbəbi**: `{ban_reason}`\n\n"
    reply_text = f"Ümumi bloklanmış istifadəçilər: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('bloklu-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('bloklu-users.txt')
        return
    await m.reply_text(reply_text, True)


@Bot.on_message(filters.private & filters.command("tsil"))
async def clear_user_batch(bot: Client, m: Message):
    MediaList[f"{str(m.from_user.id)}"] = []
    await m.reply_text("Toplu fayllarınız uğurla silindi!")


@Bot.on_callback_query()
async def button(bot: Client, cmd: CallbackQuery):

    cb_data = cmd.data
    if "aboutbot" in cb_data:
        await cmd.message.edit(
            Config.ABOUT_BOT_TEXT,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Instagram",
                                             url="https://instagram.com/dasqinnagiyev")
                    ],
                    [
                        InlineKeyboardButton("Geriyə qayıt", callback_data="gotohome"),
                        InlineKeyboardButton("Gəlişdirici haqqında", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif "aboutdevs" in cb_data:
        await cmd.message.edit(
            Config.ABOUT_DEV_TEXT,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Instagram",
                                             url="https://instagram.com/dasqinnagiyev")
                    ],
                    [
                        InlineKeyboardButton("Bot haqqında", callback_data="aboutbot"),
                        InlineKeyboardButton("Geriyə qayıt", callback_data="gotohome")
                    ]
                ]
            )
        )

    elif "gotohome" in cb_data:
        await cmd.message.edit(
            Config.HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Dəstək grupu", url="https://t.me/dasqing"),
                        InlineKeyboardButton("DAQO MODS", url="https://t.me/daqomods")
                    ],
                    [
                        InlineKeyboardButton("Bot Haqqında", callback_data="aboutbot"),
                        InlineKeyboardButton("Gəlişdirici Haqqında", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif "refreshForceSub" in cb_data:
        if Config.UPDATES_CHANNEL:
            try:
                user = await bot.get_chat_member(int(Config.UPDATES_CHANNEL), cmd.message.chat.id)
                if user.status == "kicked":
                    await cmd.message.edit(
                        text="Bağışla dosdum, sən ban oldun. Əlaqəyə keç [Dəstək grupu](https://t.me/dasqing).",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                invite_link = await bot.create_chat_invite_link(int(Config.UPDATES_CHANNEL))
                await cmd.message.edit(
                    text="**Kanalıma abunə deyilsən ☹️, Botu işlədə bilmək üçün birinci kanalıma qatıl!**\n\n"
                         "Həddindən artıq yüklənmə səbəbindən Botdan yalnız Kanal Abunəçiləri istifadə edə bilər!",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("💫Kanala qatıl", url=invite_link.invite_link)
                            ],
                            [
                                InlineKeyboardButton("🔄 Qatıldım", callback_data="refreshmeh")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await cmd.message.edit(
                    text="Bir şeylər tərs getdi. Əlaqəyə keç [Dəstək grupu](https://t.me/dasqing).",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        await cmd.message.edit(
            text=Config.HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Dəstək Grupu", url="https://t.me/dasqing"),
                        InlineKeyboardButton("DAQO MODS", url="https://t.me/daqomods")
                    ],
                    [
                        InlineKeyboardButton("Bot Haqqında", callback_data="aboutbot"),
                        InlineKeyboardButton("Gəlişdirici Haqqında", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif cb_data.startswith("ban_user_"):
        user_id = cb_data.split("_", 2)[-1]
        if Config.UPDATES_CHANNEL is None:
            await cmd.answer("Siz heç bir Yeniləmə Kanalı qurmamısınız!", show_alert=True)
            return
        if not int(cmd.from_user.id) == Config.BOT_OWNER:
            await cmd.answer("Bunu etməyə icazəniz yoxdur!!", show_alert=True)
            return
        try:
            await bot.kick_chat_member(chat_id=int(Config.UPDATES_CHANNEL), user_id=int(user_id))
            await cmd.answer("İstifadəçi Yeniləmə Kanalından Blok Edildi!", show_alert=True)
        except Exception as e:
            await cmd.answer(f"Onu blok etmək olmur!\n\nXəta: {e}", show_alert=True)

    elif "addToBatchTrue" in cb_data:
        if MediaList.get(f"{str(cmd.from_user.id)}", None) is None:
            MediaList[f"{str(cmd.from_user.id)}"] = []
        file_id = cmd.message.reply_to_message.message_id
        MediaList[f"{str(cmd.from_user.id)}"].append(file_id)
        await cmd.message.edit("Fayl Toplu halda saxlandı!\n\n"
                               "Toplu linki əldə etmək üçün aşağıdakı düyməni basın.",
                               reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton("Toplu linki ver", callback_data="getBatchLink")],
                                   [InlineKeyboardButton("Mesajı bağla", callback_data="closeMessage")]
                               ]))

    elif "addToBatchFalse" in cb_data:
        await SaveMediaInChannel(bot, editable=cmd.message, message=cmd.message.reply_to_message)

    elif "getBatchLink" in cb_data:
        message_ids = MediaList.get(f"{str(cmd.from_user.id)}", None)
        if message_ids is None:
            await cmd.answer("Toplu siyahı boşdur!", show_alert=True)
            return
        await cmd.message.edit("Gözləyin, toplu link yaradılır...")
        await SaveBatchMediaInChannel(bot=bot, editable=cmd.message, message_ids=message_ids)
        MediaList[f"{str(cmd.from_user.id)}"] = []

    elif "closeMessage" in cb_data:
        await cmd.message.delete(True)

    try:
        await cmd.answer()
    except QueryIdInvalid:
        pass

Bot.run()
