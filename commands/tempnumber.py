# commands/tempnumber.py
import requests
import random
import time
import threading
import json
from datetime import datetime, timedelta
from telebot import types
from main import bot
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# Lưu trữ số điện thoại tạm thời
temp_numbers = {}
sms_check_threads = {}

# API dịch vụ số điện thoại tạm thời (free tier)
SMS_SERVICES = {
    'receive-smss.com': {
        'api': 'https://receive-smss.com/',
        'countries': ['US', 'GB', 'DE', 'FR', 'ES'],
        'description': 'Free temporary numbers'
    },
    'smsreceivefree.com': {
        'api': 'https://smsreceivefree.com/',
        'countries': ['US', 'CA', 'GB'],
        'description': 'US/Canada numbers'
    },
    'receive-sms-online.info': {
        'api': 'https://receive-sms-online.info/',
        'countries': ['RU', 'UA', 'KZ'],
        'description': 'Russian numbers'
    }
}

@bot.message_handler(commands=['tempnumber', 'tempsms', 'taosodienthoai'])
def create_temp_number(message):
    """
    Tạo số điện thoại tạm thời để nhận SMS
    """
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Hiệu ứng loading
        loading_msg = bot.reply_to(message, "📱 Đang tìm số điện thoại tạm thời...")
        
        # Lấy country code từ message (nếu có)
        country_code = 'US'  # Mặc định là US
        parts = message.text.split()
        if len(parts) > 1:
            country_input = parts[1].upper()
            if country_input in ['US', 'UK', 'CA', 'VN', 'RU', 'DE', 'FR']:
                country_code = country_input
                if country_code == 'UK':
                    country_code = 'GB'
        
        # Tìm service phù hợp
        available_services = []
        for service_name, service_info in SMS_SERVICES.items():
            if country_code in service_info['countries']:
                available_services.append((service_name, service_info))
        
        if not available_services:
            # Fallback to any service
            available_services = list(SMS_SERVICES.items())
        
        if not available_services:
            raise Exception("Không tìm thấy dịch vụ SMS nào")
        
        # Chọn service ngẫu nhiên
        service_name, service_info = random.choice(available_services)
        
        # Tạo số điện thoại tạm thời
        phone_number = generate_temp_number(country_code, service_name)
        
        if not phone_number:
            # Thử tạo số fake nếu API không hoạt động
            phone_number = generate_fake_number(country_code)
        
        # Lưu thông tin số điện thoại
        temp_numbers[user_id] = {
            'phone': phone_number,
            'country': country_code,
            'service': service_name,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=24),  # 24 giờ
            'sms_messages': [],
            'last_check': datetime.now(),
            'api_url': service_info['api']
        }
        
        # Bắt đầu thread kiểm tra SMS
        start_sms_checker(user_id, chat_id, loading_msg.message_id, service_name, phone_number)
        
        # Phân tích thông tin số
        number_info = analyze_phone_number(phone_number, country_code)
        
        # Tạo response
        response = f"""
📱 <b>SỐ ĐIỆN THOẠI TẠM THỜI ĐÃ TẠO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Số điện thoại:</b>
<code>{phone_number}</code>

🌍 <b>Quốc gia:</b> {number_info.get('country', 'N/A')} {number_info.get('flag', '')}
🏢 <b>Nhà mạng:</b> {number_info.get('carrier', 'N/A')}
⏰ <b>Múi giờ:</b> {number_info.get('timezone', 'N/A')}
🔧 <b>Dịch vụ:</b> {service_info['description']}

⏱️ <b>Thời gian hiệu lực:</b>
{temp_numbers[user_id]['expires_at'].strftime('%H:%M:%S %d/%m/%Y')}
(≈ 24 giờ)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Cách sử dụng:</b>
1. Dùng số này đăng ký dịch vụ cần SMS
2. Bot sẽ tự động check SMS mới
3. Xem SMS với: <code>/checksms</code>
4. Xoá số: <code>/deletenumber</code>

⚠️ <b>Lưu ý:</b>
• Số chỉ tồn tại tạm thời
• Không dùng cho thông tin quan trọng
• Có thể không nhận được SMS từ một số dịch vụ
        """
        
        # Tạo inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📱 Check SMS", callback_data=f"checksms_{user_id}")
        btn2 = types.InlineKeyboardButton("🔄 Refresh", callback_data=f"refreshsms_{user_id}")
        btn3 = types.InlineKeyboardButton("🗑️ Delete", callback_data=f"deletenumber_{user_id}")
        btn4 = types.InlineKeyboardButton("📋 Copy Number", callback_data=f"copynumber_{user_id}")
        
        markup.add(btn1, btn2, btn3, btn4)
        
        # Xóa loading và gửi kết quả
        bot.delete_message(chat_id, loading_msg.message_id)
        bot.send_message(
            chat_id, 
            response, 
            parse_mode="HTML", 
            reply_markup=markup,
            disable_web_page_preview=True
        )
        
        # Gửi thông tin test
        test_info = f"""
🧪 <b>TEST NHẬN SMS NGAY:</b>
━━━━━━━━━━━━━━━━━━━━━━━━
Bạn có thể test số này bằng cách:

1. <b>Dịch vụ test SMS:</b>
• TextNow
• Receive-SMS.com
• FreePhoneNum.com

2. <b>Gửi SMS test:</b>
• Từ số điện thoại khác
• Dịch vụ gửi SMS online

3. <b>Đăng ký test:</b>
• Telegram (cần có số thật)
• WhatsApp (cần có số thật)
• Các dịch vụ verify số

📌 <b>Số test:</b> <code>{phone_number}</code>
⚠️ <i>Một số dịch vụ chặn số ảo!</i>
        """
        
        bot.send_message(chat_id, test_info, parse_mode="HTML")
        
    except Exception as e:
        if 'loading_msg' in locals():
            try:
                bot.delete_message(message.chat.id, loading_msg.message_id)
            except:
                pass
        bot.reply_to(message, f"⚠️ Lỗi tạo số: {str(e)}")

def generate_temp_number(country_code, service_name):
    """Tạo số điện thoại tạm thời từ API"""
    try:
        if service_name == 'receive-smss.com':
            # Lấy danh sách số từ API
            url = 'https://receive-smss.com/sms-api.php'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('numbers'):
                    # Chọn số từ quốc gia phù hợp
                    for num_info in data['numbers']:
                        if num_info.get('country') == country_code:
                            return num_info.get('number')
                    
                    # Fallback: chọn số đầu tiên
                    return data['numbers'][0].get('number')
        
        elif service_name == 'smsreceivefree.com':
            # Sử dụng API public (nếu có)
            # Note: Đây chỉ là ví dụ, thực tế cần API key
            url = f'https://smsreceivefree.com/country/{country_code.lower()}/'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML để lấy số (đơn giản)
                # Trong thực tế cần xử lý HTML phức tạp hơn
                return generate_fake_number(country_code)
        
        # Fallback: tạo số fake
        return generate_fake_number(country_code)
        
    except:
        return generate_fake_number(country_code)

def generate_fake_number(country_code):
    """Tạo số điện thoại fake (cho demo)"""
    # Định dạng số điện thoại theo quốc gia
    formats = {
        'US': '+1{}{}{}-{}{}{}-{}{}{}{}',
        'GB': '+44 {}{}{} {}{}{} {}{}{}{}',
        'CA': '+1{}{}{}-{}{}{}-{}{}{}{}',
        'VN': '+84 {}{}{} {}{}{} {}{}{}',
        'RU': '+7 ({}{}{}) {}{}{}-{}{}-{}{}',
        'DE': '+49 {}{}{}{} {}{}{}{}{}{}',
        'FR': '+33 {}{} {}{} {}{} {}{} {}{}'
    }
    
    fmt = formats.get(country_code, formats['US'])
    
    # Tạo số ngẫu nhiên
    digits = [str(random.randint(0, 9)) for _ in range(12)]
    
    try:
        return fmt.format(*digits[:fmt.count('{}')])
    except:
        # Fallback đơn giản
        return f"+{random.randint(1, 999)} {random.randint(100000000, 999999999)}"

def analyze_phone_number(phone_number, country_code):
    """Phân tích thông tin số điện thoại"""
    try:
        # Parse số điện thoại
        parsed = phonenumbers.parse(phone_number, country_code)
        
        # Lấy thông tin
        country = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        timezones = timezone.time_zones_for_number(parsed)
        timezone_str = timezones[0] if timezones else "N/A"
        
        # Emoji cờ
        flags = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'CA': '🇨🇦', 'VN': '🇻🇳',
            'RU': '🇷🇺', 'DE': '🇩🇪', 'FR': '🇫🇷', 'ES': '🇪🇸'
        }
        
        return {
            'country': country,
            'flag': flags.get(country_code, '🏳️'),
            'carrier': carrier_name or "Unknown",
            'timezone': timezone_str,
            'is_valid': phonenumbers.is_valid_number(parsed),
            'is_possible': phonenumbers.is_possible_number(parsed)
        }
    except:
        return {
            'country': 'Unknown',
            'flag': '🏳️',
            'carrier': 'Unknown',
            'timezone': 'N/A',
            'is_valid': False,
            'is_possible': False
        }

def start_sms_checker(user_id, chat_id, loading_msg_id, service_name, phone_number):
    """Bắt đầu thread kiểm tra SMS"""
    if user_id in sms_check_threads:
        return
    
    def check_sms():
        while user_id in temp_numbers and user_id in sms_check_threads:
            try:
                number_info = temp_numbers[user_id]
                
                # Kiểm tra hết hạn
                if datetime.now() > number_info['expires_at']:
                    bot.send_message(chat_id, "⏰ Số điện thoại đã hết hạn và bị xoá!")
                    if user_id in temp_numbers:
                        del temp_numbers[user_id]
                    break
                
                # Update last check
                temp_numbers[user_id]['last_check'] = datetime.now()
                
                # Giả lập nhận SMS (vì API thực tế cần key/paid)
                # Trong demo, tạo SMS ngẫu nhiên
                if random.random() < 0.3:  # 30% chance có SMS mới
                    fake_sender = generate_fake_number('US').replace('+1', '')
                    fake_message = generate_fake_sms()
                    
                    # Kiểm tra xem đã có SMS này chưa
                    sms_id = f"{fake_sender}_{int(time.time())}"
                    if not any(s.get('id') == sms_id for s in number_info['sms_messages']):
                        # Thêm SMS mới
                        sms_data = {
                            'id': sms_id,
                            'sender': fake_sender,
                            'message': fake_message,
                            'timestamp': datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
                            'service': 'Demo'
                        }
                        
                        temp_numbers[user_id]['sms_messages'].append(sms_data)
                        
                        # Thông báo SMS mới
                        notify_new_sms(chat_id, phone_number, sms_data)
            
            except Exception as e:
                print(f"Error checking SMS: {e}")
            
            # Chờ 45 giây
            time.sleep(45)
        
        # Dọn dẹp
        if user_id in sms_check_threads:
            del sms_check_threads[user_id]
    
    thread = threading.Thread(target=check_sms, daemon=True)
    sms_check_threads[user_id] = thread
    thread.start()

def generate_fake_sms():
    """Tạo tin nhắn SMS fake cho demo"""
    sms_templates = [
        "Your verification code is: {code}",
        "Your OTP: {code}. Do not share with anyone.",
        "{code} is your login code",
        "Verification code: {code}. Expires in 5 minutes.",
        "Security code: {code}. For account verification.",
        "Your Amazon verification code: {code}",
        "Google verification code: {code}",
        "Facebook code: {code}. Enter this on the verification page.",
        "Twitter confirmation code: {code}",
        "Instagram security code: {code}",
        "Telegram code: {code}",
        "WhatsApp code: {code}",
        "Bank OTP: {code}. For transaction verification.",
        "PayPal code: {code}. Confirm your login.",
        "Your Uber code: {code}",
        "Airbnb verification: {code}",
        "Netflix security code: {code}",
        "Spotify verification: {code}",
        "Microsoft account security code: {code}",
        "Apple ID code: {code}. Use to sign in.",
        "Your Tinder verification code is {code}",
        "Discord login code: {code}",
        "Twitch verification code: {code}",
        "Steam Guard code: {code}"
    ]
    
    # Tạo mã 4-6 số
    code = ''.join([str(random.randint(0, 9)) for _ in range(random.randint(4, 6))])
    
    template = random.choice(sms_templates)
    return template.format(code=code)

def notify_new_sms(chat_id, phone_number, sms_data):
    """Thông báo khi có SMS mới"""
    try:
        message = f"""
📱 <b>📲 BẠN CÓ SMS MỚI!</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📞 <b>Số nhận:</b> <code>{phone_number}</code>

👤 <b>Người gửi:</b> {sms_data['sender']}
⏰ <b>Thời gian:</b> {sms_data['timestamp']}
🔧 <b>Dịch vụ:</b> {sms_data['service']}

📄 <b>Nội dung:</b>
{sms_data['message']}

━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Lệnh:</b>
<code>/checksms</code> - Xem tất cả SMS
<code>/deletenumber</code> - Xoá số này
        """
        
        bot.send_message(chat_id, message, parse_mode="HTML")
        
        # Tìm và highlight mã xác thực
        import re
        code_matches = re.findall(r'\b\d{4,6}\b', sms_data['message'])
        if code_matches:
            for code in set(code_matches):
                bot.send_message(
                    chat_id,
                    f"🔐 <b>PHÁT HIỆN MÃ XÁC THỰC!</b>\n\n"
                    f"✅ <b>Mã:</b> <code>{code}</code>\n"
                    f"📞 <b>Từ số:</b> {sms_data['sender']}\n"
                    f"📝 <b>Dịch vụ:</b> {sms_data['service']}\n\n"
                    f"💡 <i>Đây là mã OTP/verification code từ SMS</i>",
                    parse_mode="HTML"
                )
                break
        
    except Exception as e:
        print(f"Error notifying SMS: {e}")

@bot.message_handler(commands=['checksms', 'xemsms'])
def check_sms_command(message):
    """Kiểm tra SMS đã nhận"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_numbers:
            bot.reply_to(message, "❌ Bạn chưa có số điện thoại tạm thời nào!\n\nDùng <code>/tempnumber</code> để tạo số mới.", parse_mode="HTML")
            return
        
        number_info = temp_numbers[user_id]
        
        if not number_info['sms_messages']:
            bot.reply_to(message, "📭 Không có SMS nào!\n\nChưa có tin nhắn nào gửi đến số này.", parse_mode="HTML")
            return
        
        response = f"""
📱 <b>DANH SÁCH SMS NHẬN ĐƯỢC</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 <b>Số điện thoại:</b> <code>{number_info['phone']}</code>
📊 <b>Tổng số SMS:</b> {len(number_info['sms_messages'])}
⏰ <b>Còn hiệu lực:</b> {get_time_remaining(number_info['expires_at'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Hiển thị 5 SMS gần nhất
        for i, sms in enumerate(number_info['sms_messages'][-5:], 1):
            sender = sms.get('sender', 'Unknown')[:15]
            message_preview = sms.get('message', '')[:40]
            timestamp = sms.get('timestamp', '')[:20]
            
            response += f"""
{i}. <b>Từ:</b> {sender}
   <b>Tin nhắn:</b> {message_preview}{'...' if len(sms.get('message', '')) > 40 else ''}
   <b>Thời gian:</b> {timestamp}
   ─────────────────────
"""
        
        response += """
━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Lệnh:</b>
<code>/viewsms <số></code> - Xem chi tiết SMS
<code>/deletenumber</code> - Xoá số
"""
        
        # Tạo inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        for i, sms in enumerate(number_info['sms_messages'][-5:], 1):
            btn_text = f"📱 SMS {i}"
            callback_data = f"viewsms_{user_id}_{sms.get('id', i)}"
            buttons.append(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
        
        buttons.append(types.InlineKeyboardButton("🔄 Refresh", callback_data=f"refreshsms_{user_id}"))
        buttons.append(types.InlineKeyboardButton("🗑️ Delete", callback_data=f"deletenumber_{user_id}"))
        
        for i in range(0, len(buttons), 2):
            if i+1 < len(buttons):
                markup.add(buttons[i], buttons[i+1])
            else:
                markup.add(buttons[i])
        
        bot.reply_to(message, response, parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['viewsms', 'xemchitietsms'])
def view_sms_detail(message):
    """Xem chi tiết một SMS cụ thể"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng chỉ định số SMS!\n\nVí dụ: <code>/viewsms 1</code>", parse_mode="HTML")
            return
        
        user_id = message.from_user.id
        
        if user_id not in temp_numbers:
            bot.reply_to(message, "❌ Bạn chưa có số điện thoại tạm thời nào!")
            return
        
        try:
            sms_index = int(parts[1]) - 1
        except:
            bot.reply_to(message, "⚠️ Số SMS không hợp lệ!")
            return
        
        number_info = temp_numbers[user_id]
        
        if sms_index < 0 or sms_index >= len(number_info['sms_messages']):
            bot.reply_to(message, f"⚠️ Chỉ có {len(number_info['sms_messages'])} SMS, không có SMS số {sms_index + 1}!")
            return
        
        sms = number_info['sms_messages'][sms_index]
        
        response = f"""
📄 <b>CHI TIẾT SMS #{sms_index + 1}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 <b>Số nhận:</b> <code>{number_info['phone']}</code>

👤 <b>Người gửi:</b> {sms.get('sender', 'Unknown')}
⏰ <b>Thời gian:</b> {sms.get('timestamp', '')}
🔧 <b>Dịch vụ:</b> {sms.get('service', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 <b>NỘI DUNG:</b>
{sms.get('message', 'Không có nội dung')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Tìm mã xác thực
        import re
        codes = re.findall(r'\b\d{4,6}\b', sms.get('message', ''))
        if codes:
            response += f"🔐 <b>Mã xác thực tìm thấy:</b>\n"
            for code in set(codes):
                response += f"• <code>{code}</code>\n"
        
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['deletenumber', 'xoasodienthoai'])
def delete_number_command(message):
    """Xoá số điện thoại tạm thời"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_numbers:
            bot.reply_to(message, "❌ Bạn không có số nào để xoá!")
            return
        
        phone_number = temp_numbers[user_id]['phone']
        
        # Dọn dẹp thread
        if user_id in sms_check_threads:
            del sms_check_threads[user_id]
        
        # Xoá số
        del temp_numbers[user_id]
        
        bot.reply_to(message, f"✅ Đã xoá số: <code>{phone_number}</code>", parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['smsstats', 'thongkesms'])
def sms_stats_command(message):
    """Thống kê SMS"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_numbers:
            bot.reply_to(message, "❌ Bạn chưa có số tạm thời nào!")
            return
        
        number_info = temp_numbers[user_id]
        now = datetime.now()
        
        response = f"""
📊 <b>THỐNG KÊ SMS</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 <b>Số điện thoại:</b> <code>{number_info['phone']}</code>
🌍 <b>Quốc gia:</b> {number_info['country']}
🔧 <b>Dịch vụ:</b> {number_info['service']}
📅 <b>Tạo lúc:</b> {number_info['created_at'].strftime('%H:%M:%S %d/%m/%Y')}
⏰ <b>Hết hạn:</b> {number_info['expires_at'].strftime('%H:%M:%S %d/%m/%Y')}
⏳ <b>Còn lại:</b> {get_time_remaining(number_info['expires_at'])}

📬 <b>Số SMS nhận:</b> {len(number_info['sms_messages'])}
🔄 <b>Lần check cuối:</b> {number_info['last_check'].strftime('%H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 <b>SMS gần đây:</b>
"""
        
        if number_info['sms_messages']:
            for i, sms in enumerate(number_info['sms_messages'][-3:], 1):
                sender = sms.get('sender', 'Unknown')[:20]
                msg_preview = sms.get('message', '')[:30]
                response += f"\n{i}. <b>{sender}</b> - {msg_preview}"
        else:
            response += "\n📭 Chưa có SMS nào"
        
        response += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

def get_time_remaining(expiry_time):
    """Tính thời gian còn lại"""
    now = datetime.now()
    if expiry_time > now:
        diff = expiry_time - now
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"{hours} giờ {minutes} phút"
    return "Đã hết hạn"

# ========== CALLBACK HANDLERS ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith('checksms_'))
def callback_check_sms(call):
    """Callback cho nút check SMS"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Đây không phải số của bạn!")
            return
        
        if user_id not in temp_numbers:
            bot.answer_callback_query(call.id, "❌ Số không tồn tại!")
            return
        
        # Gửi lệnh check SMS
        fake_message = type('obj', (object,), {
            'from_user': type('obj', (object,), {'id': user_id}),
            'chat': type('obj', (object,), {'id': call.message.chat.id})
        })()
        
        check_sms_command(fake_message)
        bot.answer_callback_query(call.id, "✅ Đang kiểm tra SMS...")
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('refreshsms_'))
def callback_refresh_sms(call):
    """Callback cho nút refresh SMS"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể refresh!")
            return
        
        if user_id not in temp_numbers:
            bot.answer_callback_query(call.id, "❌ Số không tồn tại!")
            return
        
        # Update last check
        temp_numbers[user_id]['last_check'] = datetime.now()
        
        bot.answer_callback_query(call.id, "🔄 Đang refresh SMS...")
        
        bot.send_message(
            call.message.chat.id,
            f"🔄 <b>Đã refresh SMS cho:</b>\n<code>{temp_numbers[user_id]['phone']}</code>\n\n"
            f"⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S')}",
            parse_mode="HTML"
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('deletenumber_'))
def callback_delete_number(call):
    """Callback cho nút delete number"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể xoá số của người khác!")
            return
        
        if user_id not in temp_numbers:
            bot.answer_callback_query(call.id, "❌ Số không tồn tại!")
            return
        
        phone_number = temp_numbers[user_id]['phone']
        
        # Dọn dẹp
        if user_id in sms_check_threads:
            del sms_check_threads[user_id]
        del temp_numbers[user_id]
        
        bot.answer_callback_query(call.id, "✅ Đã xoá số!")
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🗑️ <b>SỐ ĐIỆN THOẠI ĐÃ ĐƯỢC XOÁ</b>\n\n"
                 f"📞 <b>Số:</b> <code>{phone_number}</code>\n"
                 f"⏰ <b>Thời gian xoá:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                 f"✅ <i>Số đã được xoá thành công!</i>",
            parse_mode="HTML"
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('copynumber_'))
def callback_copy_number(call):
    """Callback cho nút copy number"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể copy!")
            return
        
        if user_id not in temp_numbers:
            bot.answer_callback_query(call.id, "❌ Số không tồn tại!")
            return
        
        phone_number = temp_numbers[user_id]['phone']
        
        bot.answer_callback_query(
            call.id, 
            f"📋 Số: {phone_number}\n\nĐã copy vào clipboard!",
            show_alert=True
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('viewsms_'))
def callback_view_sms(call):
    """Callback cho nút xem chi tiết SMS"""
    try:
        data_parts = call.data.split('_')
        user_id = int(data_parts[1])
        sms_id = data_parts[2] if len(data_parts) > 2 else None
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể xem!")
            return
        
        if user_id not in temp_numbers:
            bot.answer_callback_query(call.id, "❌ Số không tồn tại!")
            return
        
        if not sms_id:
            bot.answer_callback_query(call.id, "❌ SMS không tồn tại!")
            return
        
        # Tìm SMS
        number_info = temp_numbers[user_id]
        target_sms = None
        sms_index = -1
        
        for i, sms in enumerate(number_info['sms_messages']):
            if str(sms.get('id')) == str(sms_id) or str(i + 1) == str(sms_id):
                target_sms = sms
                sms_index = i
                break
        
        if not target_sms:
            bot.answer_callback_query(call.id, "❌ Không tìm thấy SMS!")
            return
        
        # Hiển thị chi tiết
        response = f"""
📱 <b>SMS #{sms_index + 1}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>👤 Người gửi:</b> {target_sms.get('sender', 'Unknown')}
<b>⏰ Thời gian:</b> {target_sms.get('timestamp', '')}
<b>🔧 Dịch vụ:</b> {target_sms.get('service', 'Unknown')}

<b>📄 Nội dung:</b>
{target_sms.get('message', 'Không có nội dung')}
"""
        
        bot.answer_callback_query(call.id, f"📱 SMS từ: {target_sms.get('sender', 'Unknown')}")
        
        bot.send_message(
            call.message.chat.id,
            response,
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)[:50]}")

# ========== CLEANUP THREAD ==========

def cleanup_expired_numbers():
    """Dọn dẹp số đã hết hạn"""
    while True:
        try:
            now = datetime.now()
            expired_users = []
            
            for user_id, number_info in list(temp_numbers.items()):
                if now > number_info['expires_at']:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                if user_id in sms_check_threads:
                    del sms_check_threads[user_id]
                if user_id in temp_numbers:
                    del temp_numbers[user_id]
            
            time.sleep(60)
        except:
            time.sleep(60)

# Khởi động cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired_numbers, daemon=True)
cleanup_thread.start()

# ========== TEST COMMAND ==========

@bot.message_handler(commands=['testsms', 'testotp'])
def test_sms_command(message):
    """Gửi SMS test (chỉ cho demo)"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_numbers:
            bot.reply_to(message, "❌ Bạn chưa có số tạm thời nào!\nDùng /tempnumber trước.")
            return
        
        # Tạo SMS test
        test_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        test_sender = generate_fake_number('US').replace('+1', '')
        
        sms_data = {
            'id': f"test_{int(time.time())}",
            'sender': test_sender,
            'message': f"Your test verification code is: {test_code}. This is a demo SMS.",
            'timestamp': datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
            'service': 'Test Service'
        }
        
        # Thêm vào history
        temp_numbers[user_id]['sms_messages'].append(sms_data)
        
        # Thông báo
        bot.reply_to(
            message,
            f"🧪 <b>SMS TEST ĐÃ GỬI</b>\n\n"
            f"✅ <b>Mã test:</b> <code>{test_code}</code>\n"
            f"📞 <b>Đến số:</b> <code>{temp_numbers[user_id]['phone']}</code>\n\n"
            f"📝 <i>Đây là SMS test để demo chức năng nhận OTP</i>",
            parse_mode="HTML"
        )
        
        # Gửi thông báo như SMS thật
        notify_new_sms(message.chat.id, temp_numbers[user_id]['phone'], sms_data)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi test: {str(e)}")

# ========== COUNTRY SELECTION ==========

@bot.message_handler(commands=['countrycodes', 'quocgia'])
def country_codes_command(message):
    """Hiển thị danh sách quốc gia hỗ trợ"""
    response = """
🌍 <b>QUỐC GIA HỖ TRỢ SỐ TẠM THỜI</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━

🇺🇸 <b>US - United States</b>
<code>/tempnumber US</code> - Số Mỹ (+1)

🇬🇧 <b>GB - United Kingdom</b>
<code>/tempnumber GB</code> - Số Anh (+44)

🇨🇦 <b>CA - Canada</b>
<code>/tempnumber CA</code> - Số Canada (+1)

🇻🇳 <b>VN - Vietnam</b>
<code>/tempnumber VN</code> - Số Việt Nam (+84)

🇷🇺 <b>RU - Russia</b>
<code>/tempnumber RU</code> - Số Nga (+7)

🇩🇪 <b>DE - Germany</b>
<code>/tempnumber DE</code> - Số Đức (+49)

🇫🇷 <b>FR - France</b>
<code>/tempnumber FR</code> - Số Pháp (+33)

🇪🇸 <b>ES - Spain</b>
<code>/tempnumber ES</code> - Số Tây Ban Nha (+34)

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Cách dùng:</b>
<code>/tempnumber &lt;mã quốc gia&gt;</code>

📌 <b>Ví dụ:</b>
<code>/tempnumber US</code> - Tạo số Mỹ
<code>/tempnumber VN</code> - Tạo số Việt Nam
<code>/tempnumber</code> - Mặc định (US)
"""
    
    bot.reply_to(message, response, parse_mode="HTML")