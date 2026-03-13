from main import bot
import requests
from telebot.types import InputMediaPhoto

API_KEY = "apikeysumi"

@bot.message_handler(commands=["postid"])
def postid_cmd(message):
    try:
        parts = message.text.split(" ", 1)

        # Nếu chưa nhập UID
        if len(parts) < 2:
            bot.reply_to(
                message,
                "📰 <b>TRA DANH SÁCH BÀI ĐĂNG FACEBOOK</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "📌 Dùng lệnh:\n"
                "<code>/postid UID</code>\n\n"
                "Ví dụ:\n"
                "<code>/postid 100090710100501</code>",
                parse_mode="HTML"
            )
            return
        
        uid = parts[1].strip()
        url = f"https://dungkon.lol/facebook/posts?uid={uid}&apikey={API_KEY}"

        res = requests.get(url).json()

        if "posts" not in res:
            bot.reply_to(
                message,
                f"❌ <b>Không lấy được bài đăng của UID:</b> {uid}",
                parse_mode="HTML"
            )
            return

        posts = res["posts"]["data"]

        # Không có bài đăng
        if len(posts) == 0:
            bot.reply_to(
                message,
                f"ℹ️ UID <b>{uid}</b> không có bài đăng nào!",
                parse_mode="HTML"
            )
            return

        # Gửi thông tin
        bot.reply_to(
            message,
            f"📰 <b>DANH SÁCH BÀI ĐĂNG</b>\n"
            f"👤 UID: <b>{uid}</b>\n"
            f"📌 Tổng bài: <b>{len(posts)}</b>\n"
            f"⏳ Đang gửi bài đăng...",
            parse_mode="HTML"
        )

        # Gửi từng bài
        for post in posts:

            created = post.get("created_time", "Không rõ")
            story = post.get("story", "")
            message_text = post.get("message", "")
            link = post.get("link", "")
            picture = post.get("picture", "")
            post_id = post.get("id", "")

            text = f"""
📰 <b>BÀI ĐĂNG FACEBOOK</b>
━━━━━━━━━━━━━━━━━━
🆔 <b>ID bài:</b> {post_id}
📅 <b>Ngày đăng:</b> {created}

📝 <b>Nội dung:</b>
{message_text if message_text else "— Không có nội dung —"}

📖 <b>Story:</b>
{story if story else "— Không có story —"}

🔗 <b>Link bài đăng:</b>
{link}
━━━━━━━━━━━━━━━━━━
            """

            # Nếu có hình → gửi kèm
            if picture:
                bot.send_photo(
                    message.chat.id,
                    picture,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                bot.send_message(message.chat.id, text, parse_mode="HTML")

        bot.send_message(
            message.chat.id,
            f"✅ <b>Đã gửi toàn bộ {len(posts)} bài đăng!</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")
