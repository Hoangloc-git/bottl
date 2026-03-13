import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from main import bot     # QUAN TRỌNG: lấy bot từ main

EMAIL = "loc804756@gmail.com"
PASSWORD = "Hoangloc@113"

def send_email(to_email, subject, message):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, to_email, msg.as_string())
    server.quit()

@bot.message_handler(commands=["spmgmail"])
def spam_gmail(message):
    try:
        args = message.text.split()

        if len(args) < 5:
            bot.reply_to(message,
                "⚠ Dùng:\n"
                "/spmgmail <email_nhận> <số_lần> <delay> <tiêu_đề> <nội_dung...>"
            )
            return

        email_nhan = args[1]
        solan = int(args[2])
        delay = float(args[3])

        subject = args[4]
        contents = args[5:]

        bot.send_message(message.chat.id,
            f"📧 Gửi Gmail...\n"
            f"• Email nhận: {email_nhan}\n"
            f"• Số lần: {solan}\n"
            f"• Delay: {delay}s\n"
            f"• Tiêu đề: {subject}"
        )

        for i in range(solan):
            content = contents[i % len(contents)]
            send_email(email_nhan, subject, content)
            time.sleep(delay)

        bot.send_message(message.chat.id, "✅ Hoàn tất gửi mail!")

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
