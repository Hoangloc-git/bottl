import requests
import json
from telebot import types
from main import bot

@bot.message_handler(commands=['fb'])
def get_facebook_info(message):
    try:
        parts = message.text.split(" ")
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập UID Facebook!\n\n👉 Ví dụ: /fb 4")
            return

        uid = parts[1]
        api_url = f"https://dungkon.lol/facebook/getinfo?uid={uid}&apikey=apikeysumi"
        res = requests.get(api_url)

        data = res.json()
        if isinstance(data, str):
            data = json.loads(data)

        if not isinstance(data, dict) or "name" not in data:
            bot.reply_to(message, "❌ Không tìm thấy thông tin người dùng này!")
            return

        name = data.get("name", "Không rõ")
        username = data.get("username", "Không có")
        link = data.get("link_profile", "Không rõ")
        gender = data.get("gender", "Không rõ")
        location = data.get("location", "Không rõ")
        follower = data.get("follower", 0)
        birthday = data.get("birthday", "Không rõ")
        relationship = data.get("relationship_status", "Không rõ")
        love = data.get("love", {}).get("name", "Không có") if isinstance(data.get("love"), dict) else "Không có"
        created = data.get("created_time", "Không rõ")
        quotes = data.get("quotes", "Không có")
        tichxanh = "✅ Có" if data.get("tichxanh") else "❌ Không"
        avatar_url = data.get("avatar")

        caption = (
            f"👤 <b>Thông tin Facebook</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🧩 Họ tên: <b>{name}</b>\n"
            f"🔗 Username: @{username}\n"
            f"🆔 UID: <code>{uid}</code>\n"
            f"🌐 <a href='{link}'>Trang cá nhân</a>\n"
            f"🎂 Sinh nhật: {birthday}\n"
            f"💑 Tình trạng: {relationship}\n"
            f"❤️ Người yêu: {love}\n"
            f"👫 Giới tính: {gender}\n"
            f"📍 Nơi ở: {location}\n"
            f"👥 Theo dõi: {follower:,}\n"
            f"☑️ Tích xanh: {tichxanh}\n"
            f"💬 Quotes: {quotes}"
        )

        bot.send_photo(message.chat.id, avatar_url, caption=caption, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")
