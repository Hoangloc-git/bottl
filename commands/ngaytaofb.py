from main import bot
import requests

API_KEY = "apikeysumi"

@bot.message_handler(commands=['ngaytaofb'])
def ngaytao_cmd(message):
    try:
        parts = message.text.split(" ", 1)

        # Nếu không nhập UID → hướng dẫn
        if len(parts) < 2:
            bot.reply_to(
                message,
                "📅 <b>TRA NGÀY TẠO TÀI KHOẢN FACEBOOK</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "📌 Cách dùng:\n"
                "<code>/ngaytao UID</code>\n\n"
                "Ví dụ:\n"
                "<code>/ngaytao 4</code>",
                parse_mode="HTML"
            )
            return
        
        uid = parts[1].strip()
        url = f"https://adidaphat.site/facebook/timejoine?uid={uid}&apikey={API_KEY}"

        data = requests.get(url).json()

        # Không có UID trong response → API fail
        if "uid" not in data:
            bot.reply_to(
                message,
                f"❌ UID <b>{uid}</b> không tồn tại hoặc API lỗi!",
                parse_mode="HTML"
            )
            return

        # LẤY ĐÚNG NHỮNG TRƯỜNG API TRẢ VỀ
        uid = data.get("uid", "Không rõ")
        name = data.get("name", "Không rõ")
        day = data.get("day", "Không rõ")
        time = data.get("time", "Không rõ")
        author = data.get("author", "Không rõ")

        # UI NÂNG CẤP NHƯNG KHÔNG THAY ĐỔI TRƯỜNG
        msg = f"""
📅 <b>THÔNG TIN NGÀY TẠO FACEBOOK</b>
━━━━━━━━━━━━━━━━━━
🆔 <b>UID:</b> {uid}
👤 <b>Tên:</b> {name}

📆 <b>Ngày tạo:</b> {day}
⏰ <b>Giờ tạo:</b> {time}

👑 <b>Tác giả API:</b> {author}
━━━━━━━━━━━━━━━━━━
"""

        bot.reply_to(message, msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")
