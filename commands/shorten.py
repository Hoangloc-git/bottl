import requests
from main import bot

@bot.message_handler(commands=['shorten'])
def shorten_handler(message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        bot.reply_to(message,
            "⚠️ Dùng:\n"
            "/shorten <link>\n\n"
            "Ví dụ:\n"
            "/shorten https://www.google.com/search?q=verylongurl"
        )
        return
    
    url = args[1]
    
    # Kiểm tra URL hợp lệ
    if not url.startswith(('http://', 'https://')):
        bot.reply_to(message, "❌ Link phải bắt đầu bằng http:// hoặc https://")
        return
    
    msg = bot.send_message(message.chat.id, "⏳")
    
    try:
        # Dùng API is.gd (miễn phí, không cần key)
        api = f"https://is.gd/create.php?format=json&url={url}"
        response = requests.get(api, timeout=10).json()
        
        if 'shorturl' in response:
            short_url = response['shorturl']
            
            bot.edit_message_text(
                f"✅ <b>Rút gọn thành công!</b>\n\n"
                f"🔗 Link gốc:\n<code>{url}</code>\n\n"
                f"✂️ Link rút gọn:\n<code>{short_url}</code>",
                message.chat.id,
                msg.message_id,
                parse_mode="HTML"
            )
        else:
            error = response.get('errormessage', 'Không rõ lỗi')
            bot.edit_message_text(f"❌ Lỗi: {error}", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi: {str(e)}", message.chat.id, msg.message_id)