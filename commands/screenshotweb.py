# commands/screenshotweb.py
import requests
import io
import base64
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telebot import types
from main import bot
import threading

@bot.message_handler(commands=['screenshotweb', 'screenshot', 'chupanhweb'])
def screenshot_command(message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            help_text = """
📸 <b>CHỤP ẢNH WEBSITE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<code>/screenshotweb &lt;url&gt;</code>
→ Chụp ảnh website

💡 <b>Ví dụ:</b>
<code>/screenshotweb https://google.com</code>
<code>/screenshotweb facebook.com</code>

⏱️ <b>Thời gian:</b> 5-10 giây
⚠️ <b>Lưu ý:</b> Một số website chặn screenshot
            """
            bot.reply_to(message, help_text, parse_mode="HTML")
            return
        
        url = parts[1].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        loading_msg = bot.reply_to(message, "📸 Đang chụp ảnh website...\n⏳ Vui lòng chờ 5-10 giây")
        
        def take_screenshot():
            try:
                screenshot_data = None
                
                # Thử các API screenshot khác nhau
                apis_to_try = [
                    lambda: screenshot_api_1(url),
                    lambda: screenshot_api_2(url),
                    lambda: screenshot_api_3(url),
                ]
                
                for api in apis_to_try:
                    try:
                        screenshot_data = api()
                        if screenshot_data and len(screenshot_data) > 1000:
                            break
                    except:
                        continue
                
                if not screenshot_data:
                    raise Exception("Không thể chụp ảnh")
                
                # Xử lý ảnh
                image = Image.open(io.BytesIO(screenshot_data))
                
                # Thêm watermark
                try:
                    draw = ImageDraw.Draw(image)
                    try:
                        font = ImageFont.truetype("arial.ttf", 16)
                    except:
                        font = ImageFont.load_default()
                    
                    watermark = f"Screenshot @ {datetime.now().strftime('%H:%M:%S')}"
                    text_bbox = draw.textbbox((0, 0), watermark, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    position = (image.width - text_width - 10, image.height - text_height - 10)
                    draw.text(position, watermark, fill=(255, 255, 255, 200), font=font)
                except:
                    pass
                
                # Chuyển về bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG', optimize=True)
                img_bytes.seek(0)
                
                # Tạo caption
                caption = f"""
📸 <b>ẢNH CHỤP WEBSITE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 <b>URL:</b> <code>{url}</code>
📅 <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}
📏 <b>Kích thước:</b> {image.width} x {image.height} px
💾 <b>Dung lượng:</b> {len(img_bytes.getvalue()):,} bytes

✅ <b>Chụp ảnh thành công!</b>
                """
                
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.send_photo(
                    message.chat.id,
                    img_bytes.getvalue(),
                    caption=caption,
                    parse_mode="HTML"
                )
                
            except Exception as e:
                bot.delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Không thể chụp ảnh website này!\n\nLỗi: {str(e)[:100]}")
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=take_screenshot)
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

def screenshot_api_1(url):
    """API 1: Sử dụng screenshotapi.net (free demo)"""
    try:
        response = requests.get(
            'https://screenshotapi.net/api/v1/screenshot',
            params={
                'url': url,
                'token': 'DEMO',  # Free demo token
                'width': 1280,
                'height': 720,
                'output': 'image',
                'ttl': 0
            },
            timeout=30
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            return response.content
    except:
        pass
    return None

def screenshot_api_2(url):
    """API 2: Sử dụng Google PageSpeed Insights"""
    try:
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {'url': url, 'screenshot': 'true'}
        
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            screenshot_data = data['lighthouseResult']['audits']['final-screenshot']['details']['data']
            
            if ',' in screenshot_data:
                screenshot_data = screenshot_data.split(',', 1)[1]
            
            return base64.b64decode(screenshot_data)
    except:
        pass
    return None

def screenshot_api_3(url):
    """API 3: Sử dụng web screenshot service"""
    try:
        response = requests.get(
            f'https://image.thum.io/get/width/1200/crop/900/{url}',
            timeout=30
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            return response.content
    except:
        pass
    return None

@bot.message_handler(commands=['webshot', 'webcapture', 'chupanh'])
def screenshot_alias(message):
    screenshot_command(message)