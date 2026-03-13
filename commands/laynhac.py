import requests
from main import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import io

# Lưu data tạm
user_data = {}

@bot.message_handler(commands=['laynhac'])
def laynhac_handler(message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        bot.reply_to(message,
            "⚠️ Dùng:\n"
            "/laynhac <tên bài hát>\n\n"
            "Ví dụ:\n"
            "/laynhac trình"
        )
        return
    
    query = args[1]
    show_music_list(message.chat.id, query, 0)

def show_music_list(chat_id, query, page):
    try:
        msg = bot.send_message(chat_id, "⏳")
        
        # Gọi API
        api = f"https://dungkon.lol/scl/search?q={query}"
        data = requests.get(api, timeout=20).json()
        
        if data.get('status') != 'success' or not data.get('results'):
            bot.edit_message_text("❌ Không tìm thấy!", chat_id, msg.message_id)
            return
        
        results = data['results']
        start = page * 5
        end = start + 5
        page_results = results[start:end]
        
        # Lưu data
        user_data[chat_id] = {
            'query': query,
            'results': results,
            'page': page
        }
        
        # Text
        text = f"🎵 <b>{query}</b> ({data['count']} bài)\n\n"
        for i, track in enumerate(page_results, start=1):
            text += f"{i}. <b>{track['title']}</b>\n   👤 {track['author']['name']} • ⏱ {track['duration']}\n\n"
        
        text += f"📄 Trang {page + 1}"
        
        # Keyboard
        keyboard = InlineKeyboardMarkup(row_width=5)
        buttons = [InlineKeyboardButton(str(i), callback_data=f"m_{start + i - 1}") for i in range(1, len(page_results) + 1)]
        keyboard.row(*buttons)
        
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️", callback_data=f"p_{page - 1}"))
        if end < len(results):
            nav.append(InlineKeyboardButton("➡️", callback_data=f"p_{page + 1}"))
        if nav:
            keyboard.row(*nav)
        
        bot.delete_message(chat_id, msg.message_id)
        bot.send_photo(chat_id, page_results[0]['author']['avatar'], caption=text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('m_'))
def music_callback(call):
    msg = None
    try:
        idx = int(call.data.split('_')[1])
        chat_id = call.message.chat.id
        
        if chat_id not in user_data:
            bot.answer_callback_query(call.id, "⚠️ Hết hạn!")
            return
        
        track = user_data[chat_id]['results'][idx]
        bot.answer_callback_query(call.id)
        
        # Gửi link
        msg = bot.send_message(chat_id, f"🔗 {track['url']}\n\n⏳ Đang tải...")
        
        # Gọi API download
        dl_api = f"https://dungkon.lol/scl/download?url={track['url']}"
        dl_data = requests.get(dl_api, timeout=20).json()
        
        if dl_data.get('status') == 'success':
            audio_url = dl_data['data']['download_url']
            
            # Tải audio
            audio = requests.get(audio_url, timeout=60).content
            
            # Gửi audio
            bot.send_audio(
                chat_id,
                audio,
                title=track['title'],
                performer=track['author']['name']
            )
            
            # Xóa msg
            bot.delete_message(chat_id, msg.message_id)
        else:
            bot.edit_message_text("❌ Không tải được!", chat_id, msg.message_id)
        
    except Exception as e:
        if msg:
            bot.edit_message_text(f"❌ {str(e)}", chat_id, msg.message_id)
        else:
            bot.send_message(call.message.chat.id, f"❌ {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def page_callback(call):
    try:
        page = int(call.data.split('_')[1])
        chat_id = call.message.chat.id
        
        if chat_id not in user_data:
            bot.answer_callback_query(call.id, "⚠️ Hết hạn!")
            return
        
        query = user_data[chat_id]['query']
        bot.delete_message(chat_id, call.message.message_id)
        show_music_list(chat_id, query, page)
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ {str(e)}")