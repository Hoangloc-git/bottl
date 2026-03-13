import requests
from main import bot

@bot.message_handler(commands=['taixiu_game'])
def taixiu_game(message):
    try:
        api = "https://dungkon.lol/game/taixiu"
        data = requests.get(api).json()

        total = data.get("total")
        result = data.get("result", "").lower()
        images = data.get("images", [])
        author = data.get("author", "Không rõ")

        # Emojis theo kết quả
        emoji = "🔥🎲" if result == "tài" else "❄️🎲"
        vn_result = "TÀI" if result == "tài" else "XỈU"

        # Nội dung hiển thị
        caption = f"""
🎮 <b>GAME TÀI XỈU – ONLINE</b>
━━━━━━━━━━━━━━━━━━
🎲 <b>Kết quả:</b> {emoji} <b>{vn_result}</b>
🔢 <b>Tổng điểm:</b> <code>{total}</code>

🖼️ <b>Kết quả xúc xắc:</b> (3 ảnh phía dưới)

✍️ <b>Tác giả API:</b> {author}
━━━━━━━━━━━━━━━━━━
"""

        # Gửi caption trước
        bot.send_message(message.chat.id, caption, parse_mode="HTML")

        # Gửi 3 ảnh xúc xắc
        media_group = []
        import telebot
        from telebot import types

        media = []
        for img in images:
            media.append(types.InputMediaPhoto(media=img))

        bot.send_media_group(message.chat.id, media)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {e}")
