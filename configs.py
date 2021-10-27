# (c) @dasqinnagiyev

import os


class Config(object):
	API_ID = int(os.environ.get("API_ID"))
	API_HASH = os.environ.get("API_HASH")
	BOT_TOKEN = os.environ.get("BOT_TOKEN")
	BOT_USERNAME = os.environ.get("BOT_USERNAME")
	DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
	BOT_OWNER = int(os.environ.get("BOT_OWNER"))
	DATABASE_URL = os.environ.get("DATABASE_URL")
	UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL")
	LOG_CHANNEL = os.environ.get("LOG_CHANNEL", None)
	BANNED_USERS = set(int(x) for x in os.environ.get("BANNED_USERS", "1234567890").split())
	FORWARD_AS_COPY = bool(os.environ.get("FORWARD_AS_COPY", True))
	BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", False))
	BANNED_CHAT_IDS = list(set(int(x) for x in os.environ.get("BANNED_CHAT_IDS", "-10001020304050").split()))
	OTHER_USERS_CAN_SAVE_FILE = bool(os.environ.get("OTHER_USERS_CAN_SAVE_FILE", True))
	ABOUT_BOT_TEXT = f"""
**Bu fayllarınızı linklərə çevirən bir botdur!**
İstənilən faylı mənə göndərin, onu bazamda saxlayacağam.\n**Bot Kanal üçün də işləyir.**\nRedaktə İcazəsi ilə məni Admin olaraq kanala əlavə edin, Yüklənmiş Faylı Kanalda Saxlayaraq Paylaş Düyməsi əlavə edəcəm.\n
🤖 **Mənim Adım:** [NDFilebot](https://t.me/{BOT_USERNAME})

📝 **Dil:** [Python3](https://www.python.org)

🧑🏻‍💻 **Gəlişdirici:** @dasqinnagiyev

👥 **Dəstək Grupu:** [Qatılmaq üçün toxun](https://t.me/dasqing)

📢 **Kanal:** [DAQO MODS](https://t.me/daqomods)
"""
	ABOUT_DEV_TEXT = f"""
🧑🏻‍💻 **Gəlişdirici:** @dasqinnagiyev

Həmçinin unutmayın ki, tərtibatçı +18 Məzmunu bazadan siləcək. Belə şeyləri göndərməyin.
"""
	HOME_TEXT = """
Salam, [{}](tg://user?id={})\n\nBu bir **Fayl paylaşım Botudur**.

İstənilən faylı mənə göndərin, mən sizə daimi Paylaşıla bilən Link verəcəm. Mən sizə kanaldada kömək edə bilərəm! **Bot haqqında** düyməsinə toxun."""
