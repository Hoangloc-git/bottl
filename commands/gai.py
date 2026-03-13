import requests
from telebot.types import Message
from main import bot

@bot.message_handler(commands=['gai'])
def video_gai(message: Message):

    api = "https://api.zeidteam.xyz/videos/gai"
    data = requests.get(api).json()

    if not data.get("status"):
        bot.reply_to(message, "❌ API lỗi")
        return

    video_url = data.get("data")

    bot.send_video(message.chat.id, video_url, caption="🔥 Video gái nè 😘")
