import requests
from main import bot

@bot.message_handler(commands=['tiktok_user'])
def tiktok_user_info(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập username TikTok!\n\nVí dụ: /tt offvnx", parse_mode="Markdown")
            return

        username = parts[1]
        url = f"https://api.zeidteam.xyz/tiktok/user-info?username={username}"

        bot.reply_to(message, f"🔍 Đang lấy thông tin TikTok của `{username}` ...", parse_mode="Markdown")

        response = requests.get(url)
        data = response.json()

        if not data.get("status"):
            bot.send_message(message.chat.id, f"❌ Không tìm thấy `{username}`.", parse_mode="Markdown")
            return

        user = data["data"]["user"]
        stats = data["data"]["stats"]

        info = (
            f"👤 *Thông tin TikTok*\n"
            f"────────────────────\n"
            f"🆔 ID: `{user['id']}`\n"
            f"🔖 Username: @{user['uniqueId']}\n"
            f"🏷️ Nickname: {user['nickname']}\n"
            f"📜 Bio: {user['signature'] or 'Không có'}\n"
            f"────────────────────\n"
            f"📹 Video: {stats['videoCount']}\n"
            f"❤️ Tim: {stats['heartCount']}\n"
            f"👥 Follower: {stats['followerCount']}\n"
            f"👤 Following: {stats['followingCount']}\n"
            f"────────────────────\n"
            f"🔗 https://www.tiktok.com/@{user['uniqueId']}"
        )

        bot.send_photo(
            chat_id=message.chat.id,
            photo=user["avatarLarger"],
            caption=info,
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {e}")
