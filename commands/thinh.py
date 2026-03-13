from main import bot
import requests

@bot.message_handler(commands=["thinh"])
def thinh_cmd(message):
    try:
        api = "https://dungkon.lol/text/thinh"
        res = requests.get(api).json()

        thinh = res.get("data", None)

        if not thinh:
            bot.reply_to(
                message,
                "❌ Không lấy được câu thính!",
                parse_mode="HTML"
            )
            return

        # Trang trí câu thính
        msg = f"""
💘 <b>THÍNH NGẪU NHIÊN</b>
━━━━━━━━━━━━━━
✨ {thinh}
━━━━━━━━━━━━━━
💗 Gõ <b>/thinh</b> để lấy thêm câu mới
"""

        bot.reply_to(message, msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")
