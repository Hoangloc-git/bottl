import requests
import time
from datetime import datetime
from main import bot

@bot.message_handler(commands=['2fa'])
def twofa_handler(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message,
            "🔐 *LẤY MÃ 2FA QUA API*\n\n"
            "*Cách dùng:*\n"
            "`/2fa <mã_2fa_base32>`\n\n"
            "*Ví dụ:*\n"
            "`/2fa AGJ4EVA3VN7VGCBBTUMWZR5NH6HGCX`\n\n"
            "*Lưu ý:*\n"
            "• Mã 2FA phải là chuỗi Base32 hợp lệ\n"
            "• API: https://twofa.co/api/\n"
            "• Token có hiệu lực trong 30 giây",
            parse_mode="Markdown"
        )
        return

    secret = args[1].strip().upper()
    
    # Kiểm tra mã có hợp lệ không (chỉ chứa A-Z2-7)
    import re
    if not re.match(r'^[A-Z2-7]+$', secret):
        bot.reply_to(message,
            "❌ *MÃ 2FA KHÔNG HỢP LỆ*\n\n"
            "Mã Base32 chỉ chứa:\n"
            "• Chữ cái in hoa A-Z\n"
            "• Số 2-7\n"
            "• Không có số 0, 1, 8, 9\n\n"
            "Ví dụ: `AGJ4EVA3VN7VGCBBTUMWZR5NH6HGCX`",
            parse_mode="Markdown"
        )
        return

    try:
        # Gửi yêu cầu đến API
        api_url = f"https://twofa.co/api/{secret}"
        
        # Thông báo đang xử lý
        processing_msg = bot.reply_to(message,
            "⏳ *ĐANG LẤY MÃ 2FA...*\n"
            f"🔗 API: `{api_url}`\n"
            "🔄 Đang kết nối đến twofa.co...",
            parse_mode="Markdown"
        )
        
        # Gọi API
        response = requests.get(api_url, timeout=10)
        
        # Kiểm tra kết quả
        if response.status_code == 200:
            data = response.json()
            
            # Kiểm tra cấu trúc JSON
            if 'token' in data and 'secret' in data:
                token = data['token']
                secret_returned = data['secret']
                
                # Thời gian hiện tại
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Tính thời gian còn lại
                current_seconds = int(time.time())
                remaining = 30 - (current_seconds % 30)
                
                # Tạo tin nhắn đẹp
                result_message = f"""
🎯 *THÀNH CÔNG - MÃ 2FA ĐÃ ĐƯỢC LẤY*

┌─🔐 *MÃ BÍ MẬT (SECRET):*
│ `{secret_returned}`
├─
├─🔢 *MÃ 2FA HIỆN TẠI:*
│ ╰─ 🏷️ `{token}`
├─
├─⏱️ *THỜI GIAN CÒN LẠI:*
│ ╰─ ⏳ {remaining} giây
├─
├─🕐 *THỜI ĐIỂM LẤY MÃ:*
│ ╰─ 🕒 {current_time}
└─
📡 *API ĐƯỢC SỬ DỤNG:*
https://twofa.co/api/

💡 *Lưu ý:* Mã sẽ thay đổi sau {remaining} giây nữa
                """
                
                # Xóa tin nhắn đang xử lý và gửi kết quả
                bot.delete_message(message.chat.id, processing_msg.message_id)
                bot.send_message(message.chat.id, result_message, parse_mode="Markdown")
                
            else:
                bot.edit_message_text(
                    f"❌ *API TRẢ VỀ DỮ LIỆU KHÔNG ĐÚNG*\n\n"
                    f"Dữ liệu nhận được:\n```json\n{data}\n```\n"
                    f"⚠️ Thiếu trường 'token' hoặc 'secret'",
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode="Markdown"
                )
                
        elif response.status_code == 400:
            bot.edit_message_text(
                "❌ *LỖI 400 - MÃ 2FA KHÔNG HỢP LỆ*\n\n"
                "Nguyên nhân có thể:\n"
                "• Mã Base32 không đúng định dạng\n"
                "• Mã quá ngắn hoặc quá dài\n"
                "• Chứa ký tự không hợp lệ\n\n"
                f"🔍 *Mã bạn nhập:* `{secret}`",
                message.chat.id,
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            
        elif response.status_code == 404:
            bot.edit_message_text(
                "❌ *LỖI 404 - KHÔNG TÌM THẤY API*\n\n"
                "API endpoint không tồn tại\n"
                "Vui lòng kiểm tra lại:\n"
                f"🔗 `{api_url}`",
                message.chat.id,
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            
        elif response.status_code == 500:
            bot.edit_message_text(
                "❌ *LỖI 500 - MÁY CHỦ GẶP SỰ CỐ*\n\n"
                "API twofa.co đang bảo trì hoặc gặp lỗi\n"
                "Vui lòng thử lại sau ít phút",
                message.chat.id,
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            
        else:
            bot.edit_message_text(
                f"❌ *LỖI {response.status_code}*\n\n"
                f"Không thể lấy mã 2FA\n"
                f"Trạng thái: {response.status_code}\n"
                f"Phản hồi: {response.text[:100]}...",
                message.chat.id,
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            
    except requests.exceptions.Timeout:
        bot.edit_message_text(
            "❌ *HẾT THỜI GIAN CHỜ*\n\n"
            "Không nhận được phản hồi từ API\n"
            "• Kiểm tra kết nối internet\n"
            "• API có thể đang quá tải\n"
            "• Thử lại sau ít phút",
            message.chat.id,
            processing_msg.message_id,
            parse_mode="Markdown"
        )
        
    except requests.exceptions.ConnectionError:
        bot.edit_message_text(
            "❌ *LỖI KẾT NỐI*\n\n"
            "Không thể kết nối đến twofa.co\n"
            "Nguyên nhân có thể:\n"
            "• Mất kết nối internet\n"
            "• API không khả dụng\n"
            "• Firewall chặn kết nối",
            message.chat.id,
            processing_msg.message_id,
            parse_mode="Markdown"
        )
        
    except requests.exceptions.RequestException as e:
        bot.edit_message_text(
            f"❌ *LỖI YÊU CẦU HTTP*\n\n"
            f"Chi tiết lỗi:\n"
            f"```\n{str(e)}\n```\n"
            f"Vui lòng thử lại sau",
            message.chat.id,
            processing_msg.message_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ *LỖI KHÔNG XÁC ĐỊNH*\n\n"
            f"Đã xảy ra lỗi:\n"
            f"```python\n{str(e)}\n```\n"
            f"Vui lòng báo cho quản trị viên",
            message.chat.id,
            processing_msg.message_id,
            parse_mode="Markdown"
        )


# Thêm lệnh /2fahelp để hướng dẫn chi tiết
@bot.message_handler(commands=['2fahelp'])
def twofa_help_handler(message):
    help_text = """
🔐 *HƯỚNG DẪN SỬ DỤNG 2FA*

*1. Lệnh cơ bản:*
`/2fa <mã_base32>`
Ví dụ: `/2fa AGJ4EVA3VN7VGCBBTUMWZR5NH6HGCX`

*2. API được sử dụng:*
• URL: `https://twofa.co/api/<mã_base32>`
• Phương thức: GET
• Định dạng trả về: JSON
• Thời gian chờ: 10 giây

*3. Định dạng mã Base32:*
• Chỉ chứa: A-Z và 2-7
• Không chứa: 0, 1, 8, 9
• Thường có 16, 26 hoặc 32 ký tự
• Ví dụ hợp lệ: `JBSWY3DPEHPK3PXP`

*4. Mã trả về:*
• `token`: Mã 2FA 6 chữ số
• `secret`: Mã bí mật bạn đã nhập
• Mã có hiệu lực trong 30 giây

*5. Lỗi thường gặp:*
• 400: Mã không hợp lệ
• 404: API không tồn tại
• 500: Lỗi máy chủ
• Timeout: Quá thời gian chờ

*6. Lệnh khác:*
`/2fahelp` - Xem hướng dẫn này
    """
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")