import requests
from main import bot

@bot.message_handler(commands=['xvideo'])
def xvideo_handler(message):
    msg = None
    try:
        msg = bot.send_message(message.chat.id, "⏳")
        
        # Lấy link
        api = "https://dungkon.lol/xvideos/download?url=https://www.xvideos.com/video.iubvvlf3f13/gai"
        data = requests.get(api, timeout=10).json()
        url = data['data']['videoUrls']['low']  # Dùng low cho nhanh
        
        # Xóa thông báo
        bot.delete_message(message.chat.id, msg.message_id)
        
        # Gửi link video luôn, không tải
        bot.send_message(message.chat.id, f"🎬 Video:\n{url}")
        
    except:
        if msg:
            bot.edit_message_text("❌", message.chat.id, msg.message_id)
        else:
            bot.reply_to(message, "❌")