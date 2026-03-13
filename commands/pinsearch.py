from main import bot
import requests
from telebot.types import InputMediaPhoto

@bot.message_handler(commands=["pinsearch"])
def pinsearch_cmd(message):
    try:
        parts = message.text.split(" ", 1)

        # Nếu thiếu nội dung
        if len(parts) < 2:
            bot.reply_to(
                message,
                "🔎 <b>TÌM KIẾM ẢNH PINTEREST</b>\n"
                "━━━━━━━━━━━━━━\n"
                "📌 Dùng lệnh:\n"
                "<code>/pinsearch nội_dung</code>\n\n"
                "Ví dụ:\n"
                "<code>/pinsearch ảnh đẹp</code>",
                parse_mode="HTML"
            )
            return

        search = parts[1].strip()
        api = f"https://dungkon.lol/pinterest?search={search}"
        res = requests.get(api).json()

        # Không có dữ liệu
        if "data" not in res or len(res["data"]) == 0:
            bot.reply_to(message, f"❌ Không tìm thấy ảnh với từ khóa <b>{search}</b>", parse_mode="HTML")
            return

        images = res["data"]
        total = res.get("count", len(images))

        # Thông báo trước khi gửi album
        bot.reply_to(
            message,
            f"📸 <b>KẾT QUẢ PINTEREST</b>\n"
            f"🔎 Từ khóa: <b>{search}</b>\n"
            f"📁 Tổng ảnh: <b>{total}</b>\n"
            f"⏳ Đang gửi toàn bộ ảnh...",
            parse_mode="HTML"
        )

        # Pinterest trả rất nhiều ảnh nên phải chia từng nhóm 10
        CHUNK = 10
        for i in range(0, len(images), CHUNK):
            chunk = images[i:i + CHUNK]

            media_group = []
            for img in chunk:
                media_group.append(InputMediaPhoto(img))

            bot.send_media_group(message.chat.id, media_group)

        # Thông báo hoàn tất
        bot.send_message(
            message.chat.id,
            f"✅ <b>Hoàn tất! Đã gửi toàn bộ {total} ảnh.</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")
