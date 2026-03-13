# commands/checksdt.py
import requests
from main import bot

API_KEY = "5BD0AF0B9BEF4315BD849246FCFAE38E"
API_URL = "https://api.veriphone.io/v2/verify"


@bot.message_handler(commands=["checksdt"])
def check_sdt(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "⚠️ Sai cú pháp!\n"
            "Dùng: /checksdt <số_điện_thoại>\n"
            "Ví dụ: /checksdt 0355348336"
        )
        return

    sdt = args[1]

    # Nếu người dùng nhập 10 số → tự động thêm +84
    if sdt.startswith("0"):
        sdt = "+84" + sdt[1:]
    elif not sdt.startswith("+"):
        sdt = "+" + sdt

    try:
        url = f"{API_URL}?phone={sdt}&key={API_KEY}"
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            bot.reply_to(message, f"❌ API lỗi: HTTP {res.status_code}")
            return

        data = res.json()

        status = data.get("phone_valid", False)
        phone_type = data.get("phone_type", "Không rõ")
        region = data.get("phone_region", "Không rõ")
        country = data.get("country", "Không rõ")
        country_code = data.get("country_code", "Không rõ")
        prefix = data.get("country_prefix", "")
        intl_number = data.get("international_number", "")
        local_number = data.get("local_number", "")
        e164 = data.get("e164", "")
        carrier = data.get("carrier", "Không rõ")

        bot.send_message(
            message.chat.id,
            (
                "📞 <b>TRA CỨU SỐ ĐIỆN THOẠI</b>\n\n"
                f"🔢 Số nhập: <code>{sdt}</code>\n"
                f"✔ Hợp lệ: <b>{status}</b>\n"
                f"📱 Loại số: {phone_type}\n"
                f"🌍 Khu vực: {region}\n"
                f"🇨🇳 Quốc gia: {country} ({country_code})\n"
                f"➕ Mã vùng: {prefix}\n"
                f"📞 Quốc tế: {intl_number}\n"
                f"🏠 Nội địa: {local_number}\n"
                f"🔗 E164: {e164}\n"
                "----------------------------------\n"
                f"📡 Nhà mạng: <b>{carrier}</b>\n"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
