import os
import time
import random
from main import bot
from telebot import types

GIF_URL = "https://www.icegif.com/wp-content/uploads/2024/08/anime-icegif-7.gif"
SUPPORT_URL = "https://facebook.com/mekedoi"

def number_to_word(text):
    """Chuyển số thành chữ: 2fa -> twofa"""
    replacements = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
        '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
    }
    result = ""
    for char in text:
        result += replacements.get(char, char)
    return result

def load_command_descriptions():
    """Đọc mô tả từ config.py"""
    config_path = "/home/container/config.py"
    descriptions = {}
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#') and not line.startswith('TOKEN'):
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().strip('"').strip("'")
                            descriptions[key] = value
    except Exception as e:
        print(f"⚠️ Lỗi đọc config.py: {e}")
    
    return descriptions

def get_all_commands():
    """Lấy tất cả file .py từ /home/container/commands"""
    commands_dir = "/home/container/commands"
    commands_list = []
    
    if not os.path.exists(commands_dir):
        return []
    
    for file in os.listdir(commands_dir):
        if file.endswith(".py") and file not in ["__init__.py", "start.py"]:
            cmd_name = file.replace(".py", "")
            commands_list.append(cmd_name)
    
    return sorted(commands_list)

def get_description(cmd_name, descriptions):
    """Lấy mô tả cho lệnh"""
    if cmd_name in descriptions:
        return descriptions[cmd_name]
    
    word_name = number_to_word(cmd_name)
    if word_name in descriptions:
        return descriptions[word_name]
    
    return "❌ Chưa định nghĩa"

JAPANESE_EMOJIS = ["🌸", "⛩️", "🎎", "🗾", "🎌", "🎏", "🎑", "🍁", "🍵", "🎴"]

def create_perfect_table(commands, descriptions):
    """Tạo bảng hiển thị TOÀN BỘ lệnh"""
    if not commands:
        return ""
    
    # Độ rộng CỐ ĐỊNH
    CMD_WIDTH = 18 
    DESC_WIDTH = 28 
    
    table_lines = []
    top_border = "┌" + "─" * (CMD_WIDTH + 2) + "┬" + "─" * (DESC_WIDTH + 2) + "┐"
    header_sep = "├" + "─" * (CMD_WIDTH + 2) + "┼" + "─" * (DESC_WIDTH + 2) + "┤"
    bottom_border = "└" + "─" * (CMD_WIDTH + 2) + "┴" + "─" * (DESC_WIDTH + 2) + "┘"
    
    table_lines.append(top_border)
    table_lines.append(f"│ {'LỆNH':^{CMD_WIDTH}} │ {'MÔ TẢ':^{DESC_WIDTH}} │")
    table_lines.append(header_sep)
    
    for cmd in commands:
        emoji = random.choice(JAPANESE_EMOJIS)
        desc = get_description(cmd, descriptions)
        
        cmd_display = f"{emoji} /{cmd}".ljust(CMD_WIDTH)
        desc_display = desc[:DESC_WIDTH-3] + "..." if len(desc) > DESC_WIDTH else desc.ljust(DESC_WIDTH)
        
        if "❌" in desc:
            table_lines.append(f"│ <b>{cmd_display}</b> │ <i>{desc_display}</i> │")
        else:
            table_lines.append(f"│ <b>{cmd_display}</b> │ <code>{desc_display}</code> │")
    
    table_lines.append(bottom_border)
    return "<pre>" + "\n".join(table_lines) + "</pre>"

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    commands = get_all_commands()
    if not commands:
        bot.reply_to(message, "🌸 <b>Không tìm thấy lệnh nào!</b>", parse_mode="HTML")
        return
    
    descs = load_command_descriptions()
    
    # Gửi GIF chào mừng
    bot.send_animation(
        message.chat.id,
        GIF_URL,
        caption="<b>🎌 <i>Konnichiwa! Hệ thống đã sẵn sàng.</i></b>",
        parse_mode="HTML"
    )
    
    table = create_perfect_table(commands, descs)
    
    message_text = f"""
<b>⛩️━💢 HOANG DZ 💗━⛩️</b>

{table}

📋 <b>TRẠNG THÁI: HIỂN THỊ TẤT CẢ</b>
• Tổng cộng: <code>{len(commands)}</code> lệnh

<b>💫 CÁCH DÙNG</b>
<code>/lệnh [tham_số]</code>

<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>
<b>🌸 <i>Arigatou gozaimasu!</i></b>
"""
    
    # Chỉ giữ lại nút Hỗ trợ
    markup = types.InlineKeyboardMarkup()
    btn_help = types.InlineKeyboardButton("❓ Hỗ trợ", url=SUPPORT_URL)
    markup.add(btn_help)
    
    bot.send_message(
        message.chat.id,
        message_text,
        parse_mode="HTML",
        reply_markup=markup,
        disable_web_page_preview=True
    )

# Xóa bỏ các handler callback và các lệnh list/ping/help cũ để tối giản code