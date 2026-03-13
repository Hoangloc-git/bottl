import requests
import json
import urllib.parse
from main import bot
import time

# =============== FACEBOOK DOWNLOAD HANDLER ===============
def get_fb_download_data(url):
    """Lấy dữ liệu từ API Facebook Download"""
    try:
        # Encode URL để truyền an toàn
        encoded_url = urllib.parse.quote(url, safe='')
        api_url = f"https://dungkon.lol/facebook/video?url={encoded_url}"
        
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

# =============== TELEGRAM COMMAND HANDLERS ===============
@bot.message_handler(commands=['fbdownloads'])
def handle_fbdownloads(message):
    """Xử lý lệnh /fbdownloads <url> - CHỈ GỬI EMOJI VÀ VIDEO"""
    parts = message.text.split(' ', 1)
    
    if len(parts) < 2:
        # Chỉ gửi emoji nếu không có URL
        bot.reply_to(message, "💖")
        return
    
    url = parts[1].strip()
    
    # Gửi emoji trái tim ngay lập tức
    bot.reply_to(message, "💖")
    
    # Lấy dữ liệu từ API
    data = get_fb_download_data(url)
    
    if data:
        # Lấy link video (ưu tiên HD)
        video_url_hd = data.get('hd')
        video_url_sd = data.get('sd')
        video_url = video_url_hd if video_url_hd else video_url_sd
        
        if video_url:
            # Chờ 0.5 giây để tạo hiệu ứng
            time.sleep(0.5)
            
            # Gửi video không caption
            try:
                bot.send_video(
                    chat_id=message.chat.id,
                    video=video_url,
                    supports_streaming=True
                )
            except:
                # Nếu không gửi được video, gửi link không message
                pass
    
    # Không gửi bất kỳ message lỗi nào