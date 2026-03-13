import requests
from main import bot

@bot.message_handler(commands=['info'])
def fb_info_v2(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(
                message,
                "⚠️ Vui lòng nhập UID Facebook!\n\nVí dụ:\n/info 61582725702918"
            )
            return

        uid = parts[1]
        url = f"https://dungkon.lol/facebook/getinfov2?uid={uid}&apikey=apikeysumi"

        bot.reply_to(message, "🔍 Đang lấy thông tin người dùng...")

        res = requests.get(url)
        data = res.json()

        # ===== KIỂM TRA DỮ LIỆU =====
        if "name" not in data:
            bot.send_message(message.chat.id, "❌ Không tìm thấy thông tin người dùng!")
            return

        # ===== LẤY THÔNG TIN =====
        name = data.get("name", "Không rõ")
        fb_id = data.get("id", uid)
        link = data.get("link", "Không có")
        first_name = data.get("first_name", "Không rõ")
        locale = data.get("locale", "Không rõ")

        is_verified = "✅ Đã xác minh" if data.get("is_verified") else "❌ Chưa xác minh"

        created = data.get("created_time", "Không rõ")
        updated = data.get("updated_time", "Không rõ")

        followers = data.get("subscribers", {}).get("summary", {}).get("total_count", 0)

        # ===== TẠO NỘI DUNG =====
        caption = f"""
👤 <b>THÔNG TIN FACEBOOK</b>
━━━━━━━━━━━━━━━━━━
🆔 <b>UID:</b> <code>{fb_id}</code>
👨‍💼 <b>Họ tên:</b> {name}
🏷️ <b>Tên riêng:</b> {first_name}
🌐 <b>Ngôn ngữ:</b> {locale}

☑️ <b>Trạng thái xác minh:</b> {is_verified}

👥 <b>Người theo dõi:</b> {followers:,}

📅 <b>Ngày tạo tài khoản:</b>
└ {created}

🛠️ <b>Cập nhật lần cuối:</b>
└ {updated}

🔗 <b>Link Facebook:</b>
<a href="{link}">{link}</a>
━━━━━━━━━━━━━━━━━━
"""

        bot.send_message(
            message.chat.id,
            caption,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {e}")
