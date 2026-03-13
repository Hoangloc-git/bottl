import requests
from main import bot

@bot.message_handler(commands=['tiktokdownload'])
def tiktok_handler(message):
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message,
            "⚠️ Dùng:\n"
            "/tiktokdownload <link_tiktok>\n\n"
            "Ví dụ:\n"
            "/tiktokdownload https://www.tiktok.com/@hoaa.hanassii/video/7309063227046989057"
        )
        return
    
    url = args[1]
    
    if "tiktok.com" not in url:
        bot.reply_to(message, "❌ Link TikTok không hợp lệ!")
        return
    
    # Tạo keyboard để chọn loại tải
    from telebot import types
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_video = types.InlineKeyboardButton("🎬 Tải Video", callback_data=f"video_{url}")
    btn_music = types.InlineKeyboardButton("🎵 Tải Nhạc", callback_data=f"music_{url}")
    markup.add(btn_video, btn_music)
    
    bot.send_message(message.chat.id, "🔽 Chọn định dạng tải xuống:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('video_', 'music_')))
def handle_download_choice(call):
    # Phân loại
    download_type = call.data.split('_')[0]
    url = call.data.split('_', 1)[1]
    
    # Hiệu ứng emoji clown (chú hề)
    clown_frames = ["🤡", "🃏", "🎭", "👺"]
    clown_msg = None
    
    try:
        # Gửi hiệu ứng chú hề
        current_frame = 0
        clown_msg = bot.send_message(call.message.chat.id, clown_frames[current_frame])
        
        # Animation chú hề
        for i in range(1, 8):  # 8 lần đổi frame
            current_frame = i % len(clown_frames)
            bot.edit_message_text(clown_frames[current_frame], 
                                call.message.chat.id, 
                                clown_msg.message_id)
            import time
            time.sleep(0.3)
        
        # Gọi API
        api = f"https://dungkon.lol/tiktok?type=download&url={url}"
        response = requests.get(api, timeout=15)
        data = response.json()
        
        # Xóa hiệu ứng chú hề
        bot.delete_message(call.message.chat.id, clown_msg.message_id)
        
        if data.get('code') == 0:
            if download_type == 'video':
                # Tải video
                video_url = data['data']['hdplay']  # HD video
                title = data['data']['title']
                author = data['data']['author']['nickname']
                
                # Gửi video với caption
                bot.send_video(
                    call.message.chat.id, 
                    video_url,
                    caption=f"🎬 <b>{title}</b>\n👤 {author}\n\n⬇️ Tải xuống thành công!",
                    parse_mode="HTML",
                    reply_to_message_id=call.message.message_id
                )
                
            elif download_type == 'music':
                # Tải nhạc
                music_url = data['data']['music']
                music_title = data['data']['music_info']['title']
                music_author = data['data']['music_info']['author']
                
                # Gửi audio
                bot.send_audio(
                    call.message.chat.id,
                    music_url,
                    title=music_title,
                    performer=music_author,
                    caption=f"🎵 <b>{music_title}</b>\n🎤 {music_author}\n\n⬇️ Tải xuống thành công!",
                    parse_mode="HTML",
                    reply_to_message_id=call.message.message_id
                )
            
            # Xóa message chọn định dạng
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
        else:
            bot.send_message(call.message.chat.id, 
                           "❌ Không tải được nội dung từ TikTok!", 
                           reply_to_message_id=call.message.message_id)
    
    except requests.exceptions.Timeout:
        if clown_msg:
            bot.delete_message(call.message.chat.id, clown_msg.message_id)
        bot.send_message(call.message.chat.id, 
                       "⏰ Timeout! Vui lòng thử lại sau.", 
                       reply_to_message_id=call.message.message_id)
    
    except requests.exceptions.RequestException as e:
        if clown_msg:
            bot.delete_message(call.message.chat.id, clown_msg.message_id)
        bot.send_message(call.message.chat.id, 
                       f"🌐 Lỗi kết nối: {str(e)}", 
                       reply_to_message_id=call.message.message_id)
    
    except KeyError as e:
        if clown_msg:
            bot.delete_message(call.message.chat.id, clown_msg.message_id)
        bot.send_message(call.message.chat.id, 
                       f"📊 Lỗi dữ liệu API: Thiếu trường {str(e)}", 
                       reply_to_message_id=call.message.message_id)
    
    except Exception as e:
        if clown_msg:
            bot.delete_message(call.message.chat.id, clown_msg.message_id)
        bot.send_message(call.message.chat.id, 
                       f"❌ Lỗi không xác định: {str(e)}", 
                       reply_to_message_id=call.message.message_id)