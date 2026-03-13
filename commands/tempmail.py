# commands/tempemail.py
import requests
import random
import string
import time
import json
from datetime import datetime, timedelta
from telebot import types
from main import bot
import threading

# Lưu trữ email tạm thời của users
temp_emails = {}
email_check_threads = {}

@bot.message_handler(commands=['tempemail', 'tempmail', 'taoemail'])
def create_temp_email(message):
    """
    Tạo email tạm thời có thể nhận mail
    """
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Hiệu ứng loading
        loading_msg = bot.reply_to(message, "📧 Đang tạo email tạm thời...")
        
        # Các dịch vụ email tạm thời API
        services = [
            {
                'name': 'Temp-Mail.org',
                'api_url': 'https://www.1secmail.com/api/v1/',
                'domain': '1secmail.com'
            },
            {
                'name': 'Guerrilla Mail',
                'api_url': 'https://api.guerrillamail.com/ajax.php',
                'domain': 'guerrillamail.com'
            },
            {
                'name': '10MinuteMail',
                'api_url': 'https://www.10minutemail.com/10MinuteMail/resources/',
                'domain': '10minutemail.com'
            }
        ]
        
        selected_service = random.choice(services)
        
        if selected_service['name'] == 'Temp-Mail.org':
            # Sử dụng 1secmail API
            email_address = create_1secmail_email(selected_service['domain'])
            if not email_address:
                raise Exception("Không thể tạo email")
                
            # Lưu thông tin email
            temp_emails[user_id] = {
                'email': email_address,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=1),
                'service': '1secmail',
                'login': email_address.split('@')[0],
                'domain': email_address.split('@')[1],
                'messages': [],
                'last_check': datetime.now()
            }
            
            # Bắt đầu thread kiểm tra email mới
            start_email_checker(user_id, chat_id, loading_msg.message_id)
            
        elif selected_service['name'] == 'Guerrilla Mail':
            # Sử dụng Guerrilla Mail API
            email_address = create_guerrilla_email()
            if not email_address:
                raise Exception("Không thể tạo email")
                
            temp_emails[user_id] = {
                'email': email_address,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=1),
                'service': 'guerrilla',
                'sid_token': None,  # Sẽ được lấy sau
                'messages': [],
                'last_check': datetime.now()
            }
            
            # Lấy sid token
            sid_token = get_guerrilla_sid_token(email_address)
            if sid_token:
                temp_emails[user_id]['sid_token'] = sid_token
                start_guerrilla_checker(user_id, chat_id, loading_msg.message_id, sid_token)
        
        else:
            # 10MinuteMail (fallback)
            email_address = create_10minutemail()
            if not email_address:
                raise Exception("Không thể tạo email")
                
            temp_emails[user_id] = {
                'email': email_address,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(minutes=10),
                'service': '10minutemail',
                'messages': [],
                'last_check': datetime.now()
            }
            
            start_10minute_checker(user_id, chat_id, loading_msg.message_id, email_address)
        
        # Tạo message response
        response = f"""
📧 <b>EMAIL TẠM THỜI ĐÃ TẠO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Email của bạn:</b>
<code>{temp_emails[user_id]['email']}</code>

⏱️ <b>Thời gian hiệu lực:</b>
{temp_emails[user_id]['expires_at'].strftime('%H:%M:%S %d/%m/%Y')}
(≈ {get_time_remaining(temp_emails[user_id]['expires_at'])})

🔗 <b>Dịch vụ:</b> {selected_service['name']}
📝 <b>ID:</b> <code>{user_id}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Cách sử dụng:</b>
1. Dùng email này đăng ký dịch vụ
2. Bot sẽ tự động check mail mới
3. Xem mail với: <code>/checkmail</code>
4. Xoá email: <code>/deletemail</code>

⚠️ <b>Lưu ý:</b>
• Email chỉ tồn tại tạm thời
• Không dùng cho thông tin quan trọng
• Tự động xoá sau khi hết hạn
        """
        
        # Tạo inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📨 Check Mail", callback_data=f"checkmail_{user_id}")
        btn2 = types.InlineKeyboardButton("🔄 Refresh", callback_data=f"refreshmail_{user_id}")
        btn3 = types.InlineKeyboardButton("🗑️ Delete", callback_data=f"deletemail_{user_id}")
        btn4 = types.InlineKeyboardButton("📋 Copy Email", callback_data=f"copyemail_{user_id}")
        
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
        
        # Gửi thông báo riêng về cách test
        test_info = """
🧪 <b>TEST NHẬN MAIL NGAY:</b>
━━━━━━━━━━━━━━━━━━━━
Bạn có thể test email này bằng cách:

1. <b>Gửi test email:</b>
   • Tới: <code>{email}</code>
   • Tiêu đề: Test Email
   • Nội dung: Hello from test

2. <b>Dùng test service:</b>
   • Temp-Mail Tester
   • Email Test Generator

3. <b>Đăng ký test:</b>
   • Temp services
   • Demo websites

📌 <i>Bot sẽ tự động thông báo khi có mail mới!</i>
        """.format(email=temp_emails[user_id]['email'])
        
        bot.send_message(chat_id, test_info, parse_mode="HTML")
        
    except Exception as e:
        if 'loading_msg' in locals():
            try:
                bot.delete_message(message.chat.id, loading_msg.message_id)
            except:
                pass
        bot.reply_to(message, f"⚠️ Lỗi tạo email: {str(e)}")

def create_1secmail_email(domain):
    """Tạo email với 1secmail API"""
    try:
        # Tạo username ngẫu nhiên
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{username}@{domain}"
        
        # Kiểm tra email có tồn tại không
        check_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        response = requests.get(check_url, timeout=5)
        
        if response.status_code == 200:
            return email
        else:
            # Thử domain khác
            domains = ['1secmail.com', '1secmail.org', '1secmail.net', 'wwjmp.com', 'esiix.com']
            for dom in domains:
                email = f"{username}@{dom}"
                check_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={dom.split('.')[0]}"
                try:
                    requests.get(check_url, timeout=3)
                    return email
                except:
                    continue
                    
        return None
    except:
        return None

def create_guerrilla_email():
    """Tạo email với Guerrilla Mail API"""
    try:
        # Tạo email address ngẫu nhiên
        response = requests.get(
            "https://api.guerrillamail.com/ajax.php?f=get_email_address",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('email_addr'):
                return data['email_addr']
                
        return None
    except:
        return None

def create_10minutemail():
    """Tạo email với 10MinuteMail"""
    try:
        # Tạo username ngẫu nhiên
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email = f"{username}@10minutemail.com"
        return email
    except:
        return None

def get_guerrilla_sid_token(email):
    """Lấy SID token cho Guerrilla Mail"""
    try:
        response = requests.get(
            f"https://api.guerrillamail.com/ajax.php?f=get_email_address&email={email}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('sid_token')
            
        return None
    except:
        return None

def start_email_checker(user_id, chat_id, loading_msg_id):
    """Bắt đầu thread kiểm tra email cho 1secmail"""
    if user_id in email_check_threads:
        return
    
    def check_email():
        while user_id in temp_emails and user_id in email_check_threads:
            try:
                email_info = temp_emails[user_id]
                if email_info['service'] != '1secmail':
                    break
                    
                # Kiểm tra đã hết hạn chưa
                if datetime.now() > email_info['expires_at']:
                    bot.send_message(chat_id, "⏰ Email đã hết hạn và bị xoá!")
                    if user_id in temp_emails:
                        del temp_emails[user_id]
                    break
                
                # Lấy danh sách mail
                login, domain = email_info['login'], email_info['domain']
                url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    # Kiểm tra mail mới
                    if messages:
                        new_messages = []
                        for msg in messages:
                            msg_id = msg['id']
                            # Kiểm tra xem đã có trong history chưa
                            if not any(m.get('id') == msg_id for m in email_info['messages']):
                                new_messages.append(msg)
                        
                        # Xử lý mail mới
                        for msg in new_messages:
                            # Lấy chi tiết mail
                            detail_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg['id']}"
                            detail_resp = requests.get(detail_url, timeout=10)
                            
                            if detail_resp.status_code == 200:
                                detail = detail_resp.json()
                                
                                # Thêm vào history
                                temp_emails[user_id]['messages'].append({
                                    'id': msg['id'],
                                    'from': detail.get('from', 'Unknown'),
                                    'subject': detail.get('subject', 'No Subject'),
                                    'date': detail.get('date', ''),
                                    'body': detail.get('textBody', ''),
                                    'html': detail.get('htmlBody', '')
                                })
                                
                                # Thông báo mail mới
                                notify_new_email(chat_id, email_info['email'], detail)
            
            except Exception as e:
                print(f"Error checking email: {e}")
            
            # Chờ 30 giây trước khi check lại
            time.sleep(30)
        
        # Dọn dẹp thread
        if user_id in email_check_threads:
            del email_check_threads[user_id]
    
    # Tạo và start thread
    thread = threading.Thread(target=check_email, daemon=True)
    email_check_threads[user_id] = thread
    thread.start()

def start_guerrilla_checker(user_id, chat_id, loading_msg_id, sid_token):
    """Bắt đầu thread kiểm tra cho Guerrilla Mail"""
    def check_guerrilla():
        while user_id in temp_emails:
            try:
                email_info = temp_emails[user_id]
                if email_info['service'] != 'guerrilla' or not email_info.get('sid_token'):
                    break
                
                # Check inbox
                url = f"https://api.guerrillamail.com/ajax.php?f=get_email_list&sid_token={sid_token}&offset=0"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('list'):
                        messages = data['list']
                        
                        # Kiểm tra mail mới
                        for msg in messages:
                            msg_id = msg['mail_id']
                            if not any(m.get('id') == msg_id for m in email_info['messages']):
                                # Thêm vào history
                                temp_emails[user_id]['messages'].append({
                                    'id': msg_id,
                                    'from': msg.get('mail_from', 'Unknown'),
                                    'subject': msg.get('mail_subject', 'No Subject'),
                                    'date': msg.get('mail_timestamp', ''),
                                    'excerpt': msg.get('mail_excerpt', '')
                                })
                                
                                # Thông báo
                                bot.send_message(
                                    chat_id,
                                    f"📨 <b>CÓ MAIL MỚI!</b>\n\n"
                                    f"📧 <b>Từ:</b> {msg.get('mail_from', 'Unknown')}\n"
                                    f"📝 <b>Tiêu đề:</b> {msg.get('mail_subject', 'No Subject')}\n"
                                    f"⏰ <b>Thời gian:</b> {msg.get('mail_timestamp', '')}\n\n"
                                    f"💡 <i>Dùng /checkmail để xem chi tiết</i>",
                                    parse_mode="HTML"
                                )
            
            except Exception as e:
                print(f"Error checking guerrilla mail: {e}")
            
            time.sleep(30)
    
    thread = threading.Thread(target=check_guerrilla, daemon=True)
    email_check_threads[user_id] = thread
    thread.start()

def start_10minute_checker(user_id, chat_id, loading_msg_id, email_address):
    """Bắt đầu thread kiểm tra cho 10MinuteMail"""
    def check_10minute():
        # 10MinuteMail không có API công khai, chỉ thông báo generic
        bot.send_message(
            chat_id,
            "📧 <b>10MinuteMail Email Created</b>\n\n"
            "⚠️ <i>Lưu ý: 10MinuteMail không có API công khai. "
            "Bạn cần tự check mail tại website của họ.</i>\n\n"
            "🔗 <b>Check mail tại:</b> https://10minutemail.com",
            parse_mode="HTML"
        )
    
    thread = threading.Thread(target=check_10minute, daemon=True)
    email_check_threads[user_id] = thread
    thread.start()

def notify_new_email(chat_id, email_address, email_detail):
    """Thông báo khi có mail mới"""
    try:
        # Rút gọn nội dung nếu quá dài
        body_preview = email_detail.get('textBody', '')[:200]
        if len(email_detail.get('textBody', '')) > 200:
            body_preview += "..."
        
        message = f"""
📨 <b>📬 BẠN CÓ MAIL MỚI!</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email nhận:</b> <code>{email_address}</code>

👤 <b>Người gửi:</b> {email_detail.get('from', 'Unknown')}
📝 <b>Tiêu đề:</b> {email_detail.get('subject', 'No Subject')}
⏰ <b>Thời gian:</b> {email_detail.get('date', '')}

📄 <b>Nội dung (xem trước):</b>
{body_preview}

━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Lệnh:</b>
<code>/checkmail</code> - Xem tất cả mail
<code>/deletemail</code> - Xoá email này
        """
        
        bot.send_message(chat_id, message, parse_mode="HTML")
        
        # Kiểm tra nếu có mã xác thực (OTP, verification code)
        if 'textBody' in email_detail:
            text_body = email_detail['textBody']
            # Tìm các mã xác thực phổ biến
            import re
            
            # Pattern cho mã OTP 6 số
            otp_patterns = [
                r'\b\d{6}\b',  # 6 số
                r'\b\d{4}\b',  # 4 số
                r'code[:\s]*(\d{4,6})',
                r'verification[:\s]*(\d{4,6})',
                r'OTP[:\s]*(\d{4,6})',
                r'password[:\s]*(\d{4,6})',
                r'PIN[:\s]*(\d{4,6})'
            ]
            
            for pattern in otp_patterns:
                matches = re.findall(pattern, text_body, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if match.isdigit() and 4 <= len(match) <= 8:
                            bot.send_message(
                                chat_id,
                                f"🔐 <b>PHÁT HIỆN MÃ XÁC THỰC!</b>\n\n"
                                f"✅ <b>Mã:</b> <code>{match}</code>\n"
                                f"📧 <b>Từ email:</b> {email_detail.get('from', 'Unknown')}\n\n"
                                f"💡 <i>Đây có thể là mã OTP/verification code</i>",
                                parse_mode="HTML"
                            )
                            break
        
    except Exception as e:
        print(f"Error notifying email: {e}")

def get_time_remaining(expiry_time):
    """Tính thời gian còn lại"""
    now = datetime.now()
    if expiry_time > now:
        diff = expiry_time - now
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"{hours} giờ {minutes} phút"
    return "Đã hết hạn"

@bot.message_handler(commands=['checkmail', 'xemmail'])
def check_mail_command(message):
    """Kiểm tra mail đã nhận"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_emails:
            bot.reply_to(message, "❌ Bạn chưa có email tạm thời nào!\n\nDùng <code>/tempemail</code> để tạo email mới.", parse_mode="HTML")
            return
        
        email_info = temp_emails[user_id]
        
        if not email_info['messages']:
            bot.reply_to(message, "📭 Hộp thư trống!\n\nChưa có mail nào gửi đến email này.", parse_mode="HTML")
            return
        
        # Hiển thị danh sách mail
        response = f"""
📬 <b>DANH SÁCH MAIL NHẬN ĐƯỢC</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email:</b> <code>{email_info['email']}</code>
📊 <b>Tổng số mail:</b> {len(email_info['messages'])}
⏰ <b>Còn hiệu lực:</b> {get_time_remaining(email_info['expires_at'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Hiển thị 5 mail gần nhất
        for i, msg in enumerate(email_info['messages'][-5:], 1):
            msg_from = msg.get('from', 'Unknown')[:30]
            msg_subject = msg.get('subject', 'No Subject')[:40]
            msg_date = msg.get('date', '')[:20]
            
            response += f"""
{i}. <b>Từ:</b> {msg_from}
   <b>Tiêu đề:</b> {msg_subject}
   <b>Thời gian:</b> {msg_date}
   ─────────────────────
"""
        
        response += """
━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Lệnh:</b>
<code>/viewmail <số></code> - Xem chi tiết mail
<code>/deletemail</code> - Xoá email
"""
        
        # Tạo inline keyboard cho từng mail
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        for i, msg in enumerate(email_info['messages'][-5:], 1):
            btn_text = f"📧 Mail {i}"
            callback_data = f"viewmail_{user_id}_{msg.get('id', i)}"
            buttons.append(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
        
        # Thêm button refresh và delete
        buttons.append(types.InlineKeyboardButton("🔄 Refresh", callback_data=f"refreshmail_{user_id}"))
        buttons.append(types.InlineKeyboardButton("🗑️ Delete All", callback_data=f"deletemail_{user_id}"))
        
        # Chia thành 2 cột
        for i in range(0, len(buttons), 2):
            if i+1 < len(buttons):
                markup.add(buttons[i], buttons[i+1])
            else:
                markup.add(buttons[i])
        
        bot.reply_to(message, response, parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['viewmail', 'xemchitietmail'])
def view_mail_detail(message):
    """Xem chi tiết một mail cụ thể"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng chỉ định số mail!\n\nVí dụ: <code>/viewmail 1</code>", parse_mode="HTML")
            return
        
        user_id = message.from_user.id
        
        if user_id not in temp_emails:
            bot.reply_to(message, "❌ Bạn chưa có email tạm thời nào!")
            return
        
        try:
            mail_index = int(parts[1]) - 1
        except:
            bot.reply_to(message, "⚠️ Số mail không hợp lệ!")
            return
        
        email_info = temp_emails[user_id]
        
        if mail_index < 0 or mail_index >= len(email_info['messages']):
            bot.reply_to(message, f"⚠️ Chỉ có {len(email_info['messages'])} mail, không có mail số {mail_index + 1}!")
            return
        
        msg = email_info['messages'][mail_index]
        
        response = f"""
📄 <b>CHI TIẾT MAIL #{mail_index + 1}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email nhận:</b> <code>{email_info['email']}</code>

👤 <b>Người gửi:</b> {msg.get('from', 'Unknown')}
📝 <b>Tiêu đề:</b> {msg.get('subject', 'No Subject')}
⏰ <b>Thời gian:</b> {msg.get('date', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 <b>NỘI DUNG:</b>
"""
        
        # Hiển thị nội dung mail
        if msg.get('body'):
            body = msg['body']
            if len(body) > 1500:
                body = body[:1500] + "\n\n... [ĐÃ CẮT BỚT DO QUÁ DÀI] ..."
            response += f"\n{body}"
        elif msg.get('html'):
            response += "\n[HTML content - use /viewhtml to see]"
        elif msg.get('excerpt'):
            response += f"\n{msg['excerpt']}"
        else:
            response += "\nKhông có nội dung"
        
        response += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Tìm và highlight mã xác thực
        if msg.get('body'):
            import re
            codes = re.findall(r'\b\d{4,6}\b', msg['body'])
            if codes:
                response += f"\n🔐 <b>Mã xác thực tìm thấy:</b>\n"
                for code in set(codes[:5]):  # Hiển thị tối đa 5 mã unique
                    response += f"• <code>{code}</code>\n"
        
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['deletemail', 'xoamail'])
def delete_email_command(message):
    """Xoá email tạm thời"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_emails:
            bot.reply_to(message, "❌ Bạn không có email nào để xoá!")
            return
        
        email_address = temp_emails[user_id]['email']
        
        # Dọn dẹp thread
        if user_id in email_check_threads:
            del email_check_threads[user_id]
        
        # Xoá email
        del temp_emails[user_id]
        
        bot.reply_to(message, f"✅ Đã xoá email: <code>{email_address}</code>", parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

@bot.message_handler(commands=['mailstats', 'thongkeemail'])
def mail_stats_command(message):
    """Thống kê email"""
    try:
        user_id = message.from_user.id
        
        if user_id not in temp_emails:
            bot.reply_to(message, "❌ Bạn chưa có email tạm thời nào!")
            return
        
        email_info = temp_emails[user_id]
        now = datetime.now()
        
        response = f"""
📊 <b>THỐNG KÊ EMAIL</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 <b>Email:</b> <code>{email_info['email']}</code>
🔧 <b>Dịch vụ:</b> {email_info['service']}
📅 <b>Tạo lúc:</b> {email_info['created_at'].strftime('%H:%M:%S %d/%m/%Y')}
⏰ <b>Hết hạn:</b> {email_info['expires_at'].strftime('%H:%M:%S %d/%m/%Y')}
⏳ <b>Còn lại:</b> {get_time_remaining(email_info['expires_at'])}

📬 <b>Số mail nhận:</b> {len(email_info['messages'])}
🔄 <b>Lần check cuối:</b> {email_info['last_check'].strftime('%H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 <b>Lịch sử gần đây:</b>
"""
        
        if email_info['messages']:
            for i, msg in enumerate(email_info['messages'][-3:], 1):
                sender = msg.get('from', 'Unknown')[:25]
                subject = msg.get('subject', 'No Subject')[:30]
                response += f"\n{i}. <b>{sender}</b> - {subject}"
        else:
            response += "\n📭 Chưa có mail nào"
        
        response += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

# ========== CALLBACK HANDLERS ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith('checkmail_'))
def callback_check_mail(call):
    """Callback cho nút check mail"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Đây không phải email của bạn!")
            return
        
        if user_id not in temp_emails:
            bot.answer_callback_query(call.id, "❌ Email không tồn tại!")
            return
        
        # Gửi lệnh check mail
        fake_message = type('obj', (object,), {
            'from_user': type('obj', (object,), {'id': user_id}),
            'chat': type('obj', (object,), {'id': call.message.chat.id})
        })()
        
        check_mail_command(fake_message)
        bot.answer_callback_query(call.id, "✅ Đang kiểm tra mail...")
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('refreshmail_'))
def callback_refresh_mail(call):
    """Callback cho nút refresh mail"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể refresh!")
            return
        
        if user_id not in temp_emails:
            bot.answer_callback_query(call.id, "❌ Email không tồn tại!")
            return
        
        # Update last check time
        temp_emails[user_id]['last_check'] = datetime.now()
        
        bot.answer_callback_query(call.id, "🔄 Đang refresh mail...")
        
        # Gửi thông báo đã refresh
        bot.send_message(
            call.message.chat.id,
            f"🔄 <b>Đã refresh mail cho:</b>\n<code>{temp_emails[user_id]['email']}</code>\n\n"
            f"⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S')}",
            parse_mode="HTML"
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('deletemail_'))
def callback_delete_mail(call):
    """Callback cho nút delete mail"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể xoá email của người khác!")
            return
        
        if user_id not in temp_emails:
            bot.answer_callback_query(call.id, "❌ Email không tồn tại!")
            return
        
        email_address = temp_emails[user_id]['email']
        
        # Dọn dẹp
        if user_id in email_check_threads:
            del email_check_threads[user_id]
        del temp_emails[user_id]
        
        bot.answer_callback_query(call.id, "✅ Đã xoá email!")
        
        # Edit message để hiển thị đã xoá
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🗑️ <b>EMAIL ĐÃ ĐƯỢC XOÁ</b>\n\n"
                 f"📧 <b>Email:</b> <code>{email_address}</code>\n"
                 f"⏰ <b>Thời gian xoá:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                 f"✅ <i>Email đã được xoá thành công!</i>",
            parse_mode="HTML"
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('copyemail_'))
def callback_copy_email(call):
    """Callback cho nút copy email"""
    try:
        user_id = int(call.data.split('_')[1])
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể copy!")
            return
        
        if user_id not in temp_emails:
            bot.answer_callback_query(call.id, "❌ Email không tồn tại!")
            return
        
        email_address = temp_emails[user_id]['email']
        
        # Trả về email để user copy
        bot.answer_callback_query(
            call.id, 
            f"📋 Email: {email_address}\n\nĐã copy vào clipboard!",
            show_alert=True
        )
        
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('viewmail_'))
def callback_view_mail(call):
    """Callback cho nút xem chi tiết mail"""
    try:
        data_parts = call.data.split('_')
        user_id = int(data_parts[1])
        mail_id = data_parts[2] if len(data_parts) > 2 else None
        
        if user_id != call.from_user.id:
            bot.answer_callback_query(call.id, "❌ Không thể xem!")
            return
        
        if user_id not in temp_emails:
            bot.answer_callback_query(call.id, "❌ Email không tồn tại!")
            return
        
        if not mail_id:
            bot.answer_callback_query(call.id, "❌ Mail không tồn tại!")
            return
        
        # Tìm mail theo ID
        email_info = temp_emails[user_id]
        target_mail = None
        mail_index = -1
        
        for i, msg in enumerate(email_info['messages']):
            if str(msg.get('id')) == str(mail_id) or str(i + 1) == str(mail_id):
                target_mail = msg
                mail_index = i
                break
        
        if not target_mail:
            bot.answer_callback_query(call.id, "❌ Không tìm thấy mail!")
            return
        
        # Hiển thị chi tiết mail
        response = f"""
📧 <b>MAIL #{mail_index + 1}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>👤 Người gửi:</b> {target_mail.get('from', 'Unknown')}
<b>📝 Tiêu đề:</b> {target_mail.get('subject', 'No Subject')}
<b>⏰ Thời gian:</b> {target_mail.get('date', '')}

<b>📄 Nội dung:</b>
"""
        
        if target_mail.get('body'):
            body = target_mail['body']
            if len(body) > 1000:
                body = body[:1000] + "..."
            response += f"\n{body}"
        else:
            response += "\n[Không có nội dung văn bản]"
        
        bot.answer_callback_query(call.id, f"📧 Mail từ: {target_mail.get('from', 'Unknown')}")
        
        # Gửi message riêng để tránh làm hỏng layout
        bot.send_message(
            call.message.chat.id,
            response,
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)[:50]}")

# ========== CLEANUP THREAD ==========

def cleanup_expired_emails():
    """Dọn dẹp email đã hết hạn"""
    while True:
        try:
            now = datetime.now()
            expired_users = []
            
            for user_id, email_info in list(temp_emails.items()):
                if now > email_info['expires_at']:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                if user_id in email_check_threads:
                    del email_check_threads[user_id]
                if user_id in temp_emails:
                    del temp_emails[user_id]
            
            time.sleep(60)  # Check mỗi phút
        except:
            time.sleep(60)

# Khởi động cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired_emails, daemon=True)
cleanup_thread.start()