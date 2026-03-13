# commands/traemail.py
import requests
from main import bot

API_KEY = "c4c46a2adf8f46448b5982863b47b566"
API_URL = "https://emailreputation.abstractapi.com/v1/"

@bot.message_handler(commands=["traemail"])
def tra_email(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "⚠️ Sai cú pháp!\n"
            "Dùng: /traemail <email>\n"
            "Ví dụ: /traemail test@gmail.com"
        )
        return

    email = args[1]

    try:
        url = f"{API_URL}?api_key={API_KEY}&email={email}"
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            bot.reply_to(message, f"❌ API lỗi: HTTP {res.status_code}")
            return

        data = res.json()

        # KHỐI 1: email_address
        email_addr = data.get("email_address", "Không rõ")

        # KHỐI 2: deliverability
        deli = data.get("email_deliverability", {})
        status = deli.get("status", "Không rõ")
        detail = deli.get("status_detail", "Không rõ")
        mx_records = deli.get("mx_records", [])
        is_format_valid = deli.get("is_format_valid", False)
        is_smtp_valid = deli.get("is_smtp_valid", False)
        is_mx_valid = deli.get("is_mx_valid", False)

        # KHỐI 3: sender info
        sender = data.get("email_sender", {})
        fname = sender.get("first_name", "Không rõ")
        lname = sender.get("last_name", "Không rõ")
        provider = sender.get("email_provider_name", "Không rõ")
        org = sender.get("organization_name", "Không rõ")
        org_type = sender.get("organization_type", "Không rõ")

        # KHỐI 4: domain info
        domain = data.get("email_domain", {})
        dom_name = domain.get("domain", "Không rõ")
        dom_age = domain.get("domain_age", "Không rõ")
        registrar = domain.get("registrar", "Không rõ")
        live_site = domain.get("is_live_site", False)
        risky_tld = domain.get("is_risky_tld", False)
        reg_date = domain.get("date_registered", "Không rõ")
        renew_date = domain.get("date_last_renewed", "Không rõ")
        exp_date = domain.get("date_expires", "Không rõ")

        # KHỐI 5: quality
        quality = data.get("email_quality", {})
        score = quality.get("score", 0)
        is_free = quality.get("is_free_email", False)
        suspicious = quality.get("is_username_suspicious", False)
        disposable = quality.get("is_disposable", False)

        # KHỐI 6: breaches
        breaches = data.get("email_breaches", {})
        total_breach = breaches.get("total_breaches", 0)

        bot.send_message(
            message.chat.id,
            (
                "📧 <b>TRA CỨU EMAIL</b>\n\n"
                f"✉️ Email: <code>{email_addr}</code>\n"
                "----------------------------------\n"
                f"📬 <b>Deliverability</b>\n"
                f"• Trạng thái: {status}\n"
                f"• Chi tiết: {detail}\n"
                f"• Format hợp lệ: {is_format_valid}\n"
                f"• SMTP hợp lệ: {is_smtp_valid}\n"
                f"• MX hợp lệ: {is_mx_valid}\n"
                f"• MX Records:\n   - " + "\n   - ".join(mx_records) + "\n"
                "----------------------------------\n"
                f"🧑 <b>Người gửi</b>\n"
                f"• Tên: {fname} {lname}\n"
                f"• Nhà cung cấp: {provider}\n"
                f"• Tổ chức: {org}\n"
                f"• Loại tổ chức: {org_type}\n"
                "----------------------------------\n"
                f"🌐 <b>Domain</b>\n"
                f"• Domain: {dom_name}\n"
                f"• Tuổi domain: {dom_age} ngày\n"
                f"• Registrar: {registrar}\n"
                f"• Live site: {live_site}\n"
                f"• Risky TLD: {risky_tld}\n"
                f"• Ngày đăng ký: {reg_date}\n"
                f"• Gia hạn: {renew_date}\n"
                f"• Hết hạn: {exp_date}\n"
                "----------------------------------\n"
                f"⭐ <b>Quality</b>\n"
                f"• Score: {score}\n"
                f"• Free email: {is_free}\n"
                f"• Username đáng ngờ: {suspicious}\n"
                f"• Disposable: {disposable}\n"
                "----------------------------------\n"
                f"🔐 <b>Rò rỉ dữ liệu</b>\n"
                f"• Tổng số leaks: {total_breach}\n"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
