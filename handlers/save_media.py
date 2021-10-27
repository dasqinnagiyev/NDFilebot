# (c) @dasqinnagiyev

import asyncio
from configs import Config
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64


async def ForwardToChannel(bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.forward(Config.DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.x > 45:
            await asyncio.sleep(sl.x)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\n`{str(sl.x)}s` burda --> `{str(editable.chat.id)}` Flood edir!!",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("İstifadəçini blokla", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        return await ForwardToChannel(bot, message, editable)


async def SaveBatchMediaInChannel(bot: Client, editable: Message, message_ids: list):
    try:
        message_ids_str = ""
        for message in (await bot.get_messages(chat_id=editable.chat.id, message_ids=message_ids)):
            sent_message = await ForwardToChannel(bot, message, editable)
            if sent_message is None:
                continue
            message_ids_str += f"{str(sent_message.message_id)} "
            await asyncio.sleep(2)
        SaveMessage = await bot.send_message(
            chat_id=Config.DB_CHANNEL,
            text=message_ids_str,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Toplunu sil", callback_data="closeMessage")
            ]])
        )
        share_link = f"https://t.me/{Config.BOT_USERNAME}?start=dasqin_{str_to_b64(str(SaveMessage.message_id))}"
        await editable.edit(
            f"**Toplu Faylları bazamda saxladım!!**\n\nFayllarınızın Daimi Linki budur: {share_link} \n\n"
            f"Fayllarınızı əldə etmək üçün sadəcə linkə klikləyin!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Linki aç", url=share_link)],
                 [InlineKeyboardButton("DAQO MODS", url="https://t.me/daqomods"),
                  InlineKeyboardButton("Dəstək Grupu", url="https://t.me/dasqing")]]
            ),
            disable_web_page_preview=True
        )
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#Toplu_saxla:\n\n[{editable.reply_to_message.from_user.first_name}](tg://user?id={editable.reply_to_message.from_user.id}) Toplu linkə get!",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Linki aç", url=share_link)]])
        )
    except Exception as err:
        await editable.edit(f"Birşeylər tərs getdi!\n\n**Xəta:** `{err}`")
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#XƏTA_geri_izləmə:\nBurda xəta baş verdi `{str(editable.chat.id)}` !!\n\n**Geri izləmə:** `{err}`",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("İstifadəçini blokla", callback_data=f"ban_user_{str(editable.chat.id)}")]
                ]
            )
        )


async def SaveMediaInChannel(bot: Client, editable: Message, message: Message):
    try:
        forwarded_msg = await message.forward(Config.DB_CHANNEL)
        file_er_id = str(forwarded_msg.message_id)
        await forwarded_msg.reply_text(
            f"#Səxşi_Fayl:\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) Fayl linkinə get!",
            parse_mode="Markdown", disable_web_page_preview=True)
        share_link = f"https://t.me/{Config.BOT_USERNAME}?start=dasqin_{str_to_b64(file_er_id)}"
        await editable.edit(
            f"**Faylı bazamda saxladım!**\n\nFaylının daimi linki budur: {share_link} \n\n"
            f"Fayllarınızı əldə etmək üçün sadəcə linkə klikləyin!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Linki aç", url=share_link)],
                 [InlineKeyboardButton("DAQO MODS", url="https://t.me/daqomods"),
                  InlineKeyboardButton("Dəstək Grupu", url="https://t.me/dasqing")]]
            ),
            disable_web_page_preview=True
        )
    except FloodWait as sl:
        if sl.x > 45:
            await asyncio.sleep(sl.x)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\nBu `{str(sl.x)}s` burada `{str(editable.chat.id)}` Flood edir!!",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("İstifadəçini blokla", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        await SaveMediaInChannel(bot, editable, message)
    except Exception as err:
        await editable.edit(f"Bir şeylər tərs getdi!\n\n**Xəta:** `{err}`")
        await bot.send_message(
            chat_id=int(Config.LOG_CHANNEL),
            text=f"#Xəta_geri_izləmə:\nBurada xəta baş verdi `{str(editable.chat.id)}` !!\n\n**Geri izləmə:** `{err}`",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("İstifadəçini blokla", callback_data=f"ban_user_{str(editable.chat.id)}")]
                ]
            )
        )
