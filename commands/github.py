import requests
from main import bot

@bot.message_handler(commands=['github'])
def github_info(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(
                message,
                "⚠️ Vui lòng nhập username GitHub!\n\n"
                "Ví dụ:\n/github dungkon2002"
            )
            return

        username = parts[1]
        api = f"https://dungkon.lol/github/info?username={username}"

        bot.reply_to(message, f"🔍 Đang lấy thông tin GitHub của `{username}` ...", parse_mode="Markdown")

        res = requests.get(api).json()

        if "login" not in res:
            bot.send_message(message.chat.id, "❌ Không tìm thấy người dùng GitHub này!")
            return

        login = res.get("login")
        name = res.get("name", "Không có")
        bio = res.get("bio", "Không có")
        location = res.get("location", "Không rõ")
        avatar = res.get("avatar_url")
        html_url = res.get("html_url")
        repos = res.get("public_repos", 0)
        followers = res.get("followers", 0)
        following = res.get("following", 0)
        ngay_tao = res.get("ngay_tao", "Không rõ")
        gio_tao = res.get("gio_tao", "")
        author = res.get("author", "Không rõ")

        caption = f"""
🐱 <b>THÔNG TIN GITHUB</b>
━━━━━━━━━━━━━━━━━━
👤 <b>Tên đầy đủ:</b> {name}
🆔 <b>Username:</b> <code>{login}</code>
🌍 <b>Vị trí:</b> {location}

📦 <b>Repo công khai:</b> {repos}
👥 <b>Theo dõi:</b> {followers}
➡️ <b>Đang theo dõi:</b> {following}

📅 <b>Ngày tạo:</b> {ngay_tao}
⏰ <b>Giờ tạo:</b> {gio_tao}

💬 <b>Bio:</b> {bio}
🔗 <b>Link GitHub:</b> <a href="{html_url}">{html_url}</a>

✍️ <b>Dữ liệu bởi:</b> {author}
━━━━━━━━━━━━━━━━━━
"""

        bot.send_photo(
            chat_id=message.chat.id,
            photo=avatar,
            caption=caption,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {e}")
