# commands/trasdt.py
import requests
from main import bot

API_KEY = "152e07dd25714577817b384a5ea485cb"
API_URL = "https://phoneintelligence.abstractapi.com/v1/"

@bot.message_handler(commands=["trasdt"])
def tra_sdt(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message,
            "⚠️ Sai cú pháp!\n"
            "Dùng: /trasdt <số điện thoại>\n"
            "Ví dụ: /trasdt 84355348342 dùng mã quốc gia ví dụ +84 355348396 bỏ dấu + và cách"
        )
        return

    phone = args[1]

    try:
        url = f"{API_URL}?api_key={API_KEY}&phone={phone}"
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            bot.reply_to(message, f"❌ API lỗi: HTTP {res.status_code}")
            return

        data = res.json()

        num = data.get("phone_number", "Không rõ")
        fmt_int = data.get("phone_format", {}).get("international", "Không rõ")
        fmt_nat = data.get("phone_format", {}).get("national", "Không rõ")

        carrier = data.get("phone_carrier", {})
        carrier_name = carrier.get("name", "Không rõ")
        line_type = carrier.get("line_type", "Không rõ")

        loc = data.get("phone_location", {})
        country = loc.get("country_name", "Không rõ")
        region = loc.get("region", "Không rõ")
        city = loc.get("city", "Không rõ")
        timezone = loc.get("timezone", "Không rõ")

        msg = data.get("phone_messaging", {})
        sms_domain = msg.get("sms_domain", "Không rõ")
        sms_email = msg.get("sms_email", "Không rõ")

        val = data.get("phone_validation", {})
        is_valid = val.get("is_valid", False)
        line_status = val.get("line_status", "Không rõ")
        is_voip = val.get("is_voip", False)

        risk = data.get("phone_risk", {})
        risk_level = risk.get("risk_level", "Không rõ")
        disposable = risk.get("is_disposable", False)

        breaches = data.get("phone_breaches", {})
        total_breaches = breaches.get("total_breaches", "Không rõ")

        bot.send_message(
            message.chat.id,
            (
                "🔎 <b>TRA CỨU SỐ ĐIỆN THOẠI</b>\n\n"
                f"📱 Số gốc: <code>{num}</code>\n"
                f"🌐 International: {fmt_int}\n"
                f"🏠 National: {fmt_nat}\n\n"

                f"📡 <b>Nhà mạng:</b>\n"
                f"• Tên: {carrier_name}\n"
                f"• Loại: {line_type}\n\n"

                f"🌍 <b>Vị trí:</b>\n"
                f"• Quốc gia: {country}\n"
                f"• Thành phố: {city}\n"
                f"• Khu vực: {region}\n"
                f"• Múi giờ: {timezone}\n\n"

                f"💬 <b>SMS:</b>\n"
                f"• Domain: {sms_domain}\n"
                f"• Email SMS: {sms_email}\n\n"

                f"✔ <b>Xác thực:</b>\n"
                f"• Hợp lệ: {is_valid}\n"
                f"• Trạng thái: {line_status}\n"
                f"• VOIP: {is_voip}\n\n"

                f"⚠ <b>Rủi ro:</b>\n"
                f"• Risk level: {risk_level}\n"
                f"• Disposable: {disposable}\n\n"

                f"🔐 <b>Bị lộ dữ liệu:</b>\n"
                f"• Số lần breach: {total_breaches}\n"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
