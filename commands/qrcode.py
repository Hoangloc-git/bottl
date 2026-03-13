import requests
from telebot.types import Message
from main import bot

@bot.message_handler(commands=['qrcode'])
def qrcode_heart(message: Message):
    parts = message.text.split(" ", 2)

    if len(parts) < 3:
        bot.reply_to(
            message,
            "⚠️ Dùng sai!\n\nVí dụ:\n/qrcode (nộidung1:ưu tiên url web) (caption2) bỏ ()"
        )
        return

    text = parts[1]
    caption = parts[2]

    api = f"https://api.zeidteam.xyz/image-generator/qrcode-heart?text={text}&caption={caption}"

    img = requests.get(api).content

    bot.send_photo(message.chat.id, img, caption="❤️ QR Trái Tim Của Bạn")
