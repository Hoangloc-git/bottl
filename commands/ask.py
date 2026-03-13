import requests
from telebot.types import Message
from main import bot

@bot.message_handler(commands=['ask'])
def ask_gpt(message: Message):
    text = message.text.replace("/ask", "").strip()
    if text == "":
        bot.reply_to(message, "⚠️ Vui lòng nhập câu hỏi!\nVí dụ: /ask bạn là ai?")
        return

    api_url = f"https://api.zeidteam.xyz/ai/chatgpt4?prompt={text}"

    bot.reply_to(message, "⏳ Đang suy nghĩ...")

    res = requests.get(api_url).json()

    reply = res.get("response", "❌ API lỗi")

    bot.send_message(message.chat.id, f"🤖 **GPT trả lời:**\n{reply}", parse_mode="Markdown")
