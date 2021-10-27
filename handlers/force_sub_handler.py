# (c) @dasqinnagiyev

import asyncio
from configs import Config
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


async def handle_force_sub(bot: Client, cmd: Message):
    try:
        user = await bot.get_chat_member(chat_id=(int(Config.UPDATES_CHANNEL) if Config.UPDATES_CHANNEL.startswith("-100") else Config.UPDATES_CHANNEL), user_id=cmd.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text="Sən ban oldun. Əlaqəyə keç [Dəstək Grupu](https://t.me/dasqing).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return 400
    except UserNotParticipant:
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=(int(Config.UPDATES_CHANNEL) if Config.UPDATES_CHANNEL.startswith("-100") else Config.UPDATES_CHANNEL))
        except FloodWait as e:
            await asyncio.sleep(e.x)
            invite_link = await bot.create_chat_invite_link(chat_id=(int(Config.UPDATES_CHANNEL) if Config.UPDATES_CHANNEL.startswith("-100") else Config.UPDATES_CHANNEL))
        except Exception as err:
            print(f"Bu kanala {Config.UPDATES_CHANNEL} abunə olmaq mümkün deyil\n\nXəta: {err}")
            return 200
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**Botu işlədə bilmək üçün kanalıma qatıl!**\n\n"
                 "Həddindən artıq yüklənmə səbəbindən Botdan yalnız Kanal Abunəçiləri istifadə edə bilər!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("💫 Kanala qatıl", url=invite_link.invite_link)
                    ],
                    [
                        InlineKeyboardButton("🔄 Qatıldım", callback_data="refreshForceSub")
                    ]
                ]
            ),
            parse_mode="markdown"
        )
        return 400
    except Exception:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="Bir şeylər tərs getdi. Əlaqəyə keç [Dəstək Grupu](https://t.me/dasqing).",
            parse_mode="markdown",
            disable_web_page_preview=True
        )
        return 400
    return 200
