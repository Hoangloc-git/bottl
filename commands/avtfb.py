import requests
import os
from telebot.types import Message, InputFile
from main import bot

@bot.message_handler(commands=['avtfb'])
def avtfb_cmd(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            help_text = (
                "📷 <b>LẤY AVATAR FACEBOOK</b>\n"
                "━━━━━━━━━━━━━━━━\n"
                "<b>Cách dùng:</b>\n"
                "<code>/avtfb UID</code> - Lấy avatar theo UID\n"
                "<code>/avtfb @username</code> - Lấy avatar theo username\n\n"
                "<b>Ví dụ:</b>\n"
                "<code>/avtfb 4</code> - Avatar của Mark Zuckerberg\n"
                "<code>/avtfb zuck</code> - Avatar username zuck"
            )
            bot.reply_to(message, help_text, parse_mode="HTML")
            return
        
        target = parts[1].strip()
        
        # Kiểm tra nếu là UID (chỉ số)
        if target.isdigit():
            uid = target
            # URL lấy avatar từ Facebook Graph API
            avatar_url = f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
            display_text = f"🆔 UID: {uid}"
        else:
            # Nếu là username (bỏ @ nếu có)
            username = target.lstrip('@')
            # Thử lấy UID từ username trước
            try:
                # Graph API để lấy thông tin user
                url = f"https://graph.facebook.com/{username}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'id' in data:
                        uid = data['id']
                        avatar_url = f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
                        display_text = f"👤 Username: {username}\n🆔 UID: {uid}"
                    else:
                        # Nếu không có id, thử trực tiếp với username
                        uid = username
                        avatar_url = f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
                        display_text = f"👤 Username: {username}"
                else:
                    uid = username
                    avatar_url = f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
                    display_text = f"👤 Username: {username}"
            except:
                uid = username
                avatar_url = f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
                display_text = f"👤 Username: {username}"
        
        bot.reply_to(message, f"🔍 Đang lấy avatar cho {target}...")
        
        # Tạo thư mục cache nếu chưa có
        cache_dir = "/home/container/cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Tải avatar
        response = requests.get(avatar_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            # Lưu ảnh tạm
            image_path = os.path.join(cache_dir, f"avatar_{uid}.jpg")
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Gửi ảnh
            with open(image_path, 'rb') as photo:
                caption = (
                    f"📸 <b>AVATAR FACEBOOK</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"{display_text}\n"
                    f"🔗 <b>Link:</b> fb.com/{uid}\n"
                    f"📏 <b>Kích thước:</b> 1080x1080\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"💡 Avatar được lấy từ Facebook Graph API"
                )
                
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=caption,
                    parse_mode="HTML"
                )
            
            # Xóa file cache
            try:
                os.remove(image_path)
            except:
                pass
            
        else:
            bot.reply_to(message, f"❌ Không thể lấy avatar!\n📌 Status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Timeout! Thử lại sau.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# Command lấy avatar với kích thước tùy chỉnh
@bot.message_handler(commands=['avatar'])
def avatar_custom_cmd(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            help_text = (
                "🖼️ <b>AVATAR CUSTOM SIZE</b>\n"
                "━━━━━━━━━━━━━━━━\n"
                "<code>/avatar UID size</code>\n\n"
                "<b>Ví dụ:</b>\n"
                "<code>/avatar 4 500</code> - Avatar 500x500\n"
                "<code>/avatar 4 720</code> - Avatar 720x720\n"
                "<code>/avatar 4 1080</code> - Avatar 1080x1080"
            )
            bot.reply_to(message, help_text, parse_mode="HTML")
            return
        
        uid = parts[1].strip()
        
        # Kiểm tra size
        size = 720  # Mặc định
        if len(parts) >= 3:
            try:
                size = int(parts[2])
                if size < 100:
                    size = 100
                elif size > 2000:
                    size = 2000
            except:
                pass
        
        if not uid.isdigit():
            bot.reply_to(message, "❌ UID phải là số!")
            return
        
        bot.reply_to(message, f"📐 Đang lấy avatar {size}x{size}...")
        
        # URL với size tùy chỉnh
        avatar_url = f"https://graph.facebook.com/{uid}/picture?width={size}&height={size}&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
        
        # Tải avatar
        response = requests.get(avatar_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            cache_dir = "/home/container/cache"
            os.makedirs(cache_dir, exist_ok=True)
            
            image_path = os.path.join(cache_dir, f"avatar_{uid}_{size}.jpg")
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Gửi ảnh
            with open(image_path, 'rb') as photo:
                caption = f"📸 Avatar {size}x{size} của UID {uid}"
                bot.send_photo(message.chat.id, photo, caption=caption)
            
            # Xóa cache
            try:
                os.remove(image_path)
            except:
                pass
        else:
            bot.reply_to(message, f"❌ Không tìm thấy avatar cho UID {uid}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# Command lấy avatar HD (chất lượng cao)
@bot.message_handler(commands=['avthd'])
def avatar_hd_cmd(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ Thiếu UID! Dùng: /avthd <UID>")
            return
        
        uid = parts[1].strip()
        
        if not uid.isdigit():
            bot.reply_to(message, "❌ UID phải là số!")
            return
        
        bot.reply_to(message, f"🎨 Đang lấy avatar HD cho UID {uid}...")
        
        # Thử nhiều URL khác nhau để lấy ảnh chất lượng cao nhất
        urls = [
            f"https://graph.facebook.com/{uid}/picture?width=2000&height=2000&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662",
            f"https://graph.facebook.com/{uid}/picture?type=large&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662",
            f"https://graph.facebook.com/{uid}/picture?width=1080&height=1080&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"
        ]
        
        success = False
        for url in urls:
            try:
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    cache_dir = "/home/container/cache"
                    os.makedirs(cache_dir, exist_ok=True)
                    
                    image_path = os.path.join(cache_dir, f"avatar_hd_{uid}.jpg")
                    with open(image_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    
                    # Gửi ảnh
                    with open(image_path, 'rb') as photo:
                        caption = f"🎨 Avatar HD của UID {uid}"
                        bot.send_photo(message.chat.id, photo, caption=caption)
                    
                    # Xóa cache
                    try:
                        os.remove(image_path)
                    except:
                        pass
                    
                    success = True
                    break
                    
            except:
                continue
        
        if not success:
            bot.reply_to(message, f"❌ Không thể lấy avatar HD cho UID {uid}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")