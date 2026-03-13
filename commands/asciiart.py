# commands/asciiart.py
import pyfiglet
from datetime import datetime
from telebot import types
from main import bot

ASCII_FONTS = [
    'standard', 'slant', '3-d', '3x5', '5lineoblique', 'alphabet',
    'banner3-D', 'doh', 'isometric1', 'letters', 'alligator',
    'dotmatrix', 'bubble', 'bulbhead', 'digital', 'ivrit',
    'larry3d', 'ogre', 'rectangles', 'script', 'shadow',
    'speed', 'starwars', 'stop', 'thin', 'trek'
]

@bot.message_handler(commands=['asciiart', 'ascii', 'textart'])
def ascii_art_command(message):
    try:
        parts = message.text.split(" ", 2)
        
        if len(parts) < 2:
            help_text = """
🎨 <b>LỆNH TẠO ASCII ART</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>/asciiart &lt;text&gt;</code> - Tạo ASCII art mặc định
<code>/asciiart &lt;font&gt; &lt;text&gt;</code> - Với font chỉ định
<code>/asciiart fonts</code> - Xem tất cả font

🎯 <b>Ví dụ:</b>
<code>/asciiart Hello World</code>
<code>/asciiart slant Telegram Bot</code>
<code>/asciiart bubble ASCII ART</code>

🔤 <b>Font phổ biến:</b>
• standard • slant • shadow • bubble
• digital • starwars • block • script
            """
            bot.reply_to(message, help_text, parse_mode="HTML")
            return
        
        if len(parts) == 2:
            text = parts[1]
            font = 'standard'
        else:
            text = parts[2]
            font = parts[1].lower()
        
        if len(text) > 30:
            bot.reply_to(message, "⚠️ Text quá dài! Tối đa 30 ký tự.")
            return
        
        if font not in ASCII_FONTS:
            similar = [f for f in ASCII_FONTS if font in f]
            if similar:
                font = similar[0]
            else:
                font = 'standard'
        
        bot.send_chat_action(message.chat.id, 'typing')
        loading_msg = bot.reply_to(message, "🎨 Đang tạo ASCII art...")
        
        try:
            ascii_result = pyfiglet.figlet_format(text, font=font)
            if not ascii_result or len(ascii_result.strip()) == 0:
                ascii_result = pyfiglet.figlet_format(text, font='standard')
        except:
            ascii_result = f"  {text}  \n" + "-" * (len(text) + 4)
        
        response = f"""
🎨 <b>ASCII ART GENERATOR</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 <b>Text:</b> {text}
🔤 <b>Font:</b> {font.upper()}
📏 <b>Độ dài:</b> {len(text)} ký tự
⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S')}

<code>{ascii_result}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Thử font khác:</b>
<code>/asciiart slant {text}</code>
<code>/asciiart bubble {text}</code>
        """
        
        markup = types.InlineKeyboardMarkup(row_width=3)
        popular_fonts = ['standard', 'slant', 'bubble', 'shadow', 'block', 'digital']
        buttons = []
        
        for f in popular_fonts:
            if f != font:
                buttons.append(types.InlineKeyboardButton(
                    f.upper(), 
                    callback_data=f"ascii_{text[:20].replace(' ', '_')}_{f}"
                ))
        
        for i in range(0, len(buttons), 3):
            markup.add(*buttons[i:i+3])
        
        bot.delete_message(message.chat.id, loading_msg.message_id)
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['asciifonts', 'fonts'])
def list_fonts(message):
    try:
        response = """
🔤 <b>DANH SÁCH FONT ASCII ART</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Tổng số:</b> 25 font

"""
        for i in range(0, len(ASCII_FONTS), 5):
            fonts_line = ASCII_FONTS[i:i+5]
            response += " • ".join([f"<code>{f}</code>" for f in fonts_line]) + "\n"
        
        response += """
━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Cách dùng:</b>
<code>/asciiart &lt;font&gt; &lt;text&gt;</code>

🎯 <b>Ví dụ:</b>
<code>/asciiart starwars HELLO</code>
<code>/asciiart digital WORLD</code>
        """
        
        bot.reply_to(message, response, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ascii_'))
def ascii_callback(call):
    try:
        data = call.data.split('_')
        text = data[1].replace('_', ' ')
        font = data[2]
        
        try:
            ascii_result = pyfiglet.figlet_format(text, font=font)
            if not ascii_result:
                ascii_result = pyfiglet.figlet_format(text, font='standard')
        except:
            ascii_result = f"  {text}  \n" + "-" * (len(text) + 4)
        
        response = f"""
🔄 <b>Font {font.upper()}:</b>
<code>{ascii_result}</code>
        """
        
        bot.edit_message_text(
            response,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, f"✅ Đổi sang font {font}")
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)[:50]}")