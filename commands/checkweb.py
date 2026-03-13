# commands/checkweb.py
import requests
import time
from telebot import types
from main import bot

@bot.message_handler(commands=['checkweb'])
def check_website(message):
    try:
        # Tách lấy URL từ tin nhắn
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập URL cần kiểm tra!\n\n👉 Ví dụ: /checkweb https://google.com")
            return

        url = parts[1].strip()
        
        # Thêm http:// nếu URL không có scheme
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        # Gửi thông báo đang xử lý
        processing_msg = bot.reply_to(message, "🔄 Đang kiểm tra website...\nVui lòng chờ 5-10 giây.")

        results = []
        status_messages = {
            200: "✅ 200 OK - Live",
            301: "🔄 301 Moved Permanently",
            302: "🔄 302 Found (Temporary Redirect)",
            403: "🚫 403 Forbidden - Bị chặn",
            404: "❌ 404 Not Found",
            500: "💥 500 Internal Server Error",
            502: "🔧 502 Bad Gateway",
            503: "⚠️ 503 Service Unavailable",
            504: "⏱️ 504 Gateway Timeout"
        }

        # Kiểm tra 5 lần
        for i in range(1, 6):
            try:
                start_time = time.time()
                response = requests.get(
                    url, 
                    timeout=10,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)  # ms
                
                status_code = response.status_code
                status_text = status_messages.get(status_code, f"❓ {status_code} Unknown Status")
                
                result = f"Lần {i}: {status_text}\n   ⏱️ Thời gian: {response_time}ms"
                results.append(result)
                
            except requests.exceptions.Timeout:
                results.append(f"Lần {i}: ⏱️ Timeout - Mất kết nối")
            except requests.exceptions.ConnectionError:
                results.append(f"Lần {i}: 🔌 Connection Error - Không thể kết nối")
            except requests.exceptions.TooManyRedirects:
                results.append(f"Lần {i}: 🔄 Too Many Redirects")
            except requests.exceptions.RequestException as e:
                results.append(f"Lần {i}: ❌ Lỗi: {str(e)[:50]}")
            except Exception as e:
                results.append(f"Lần {i}: ⚠️ Lỗi không xác định: {str(e)[:50]}")
            
            # Chờ 1 giây giữa các lần kiểm tra
            if i < 5:
                time.sleep(1)

        # Đếm kết quả
        live_count = sum(1 for r in results if "200 OK" in r)
        blocked_count = sum(1 for r in results if "403" in r or "Bị chặn" in r)
        timeout_count = sum(1 for r in results if "Timeout" in r)
        error_count = sum(1 for r in results if "Lỗi" in r or "Error" in r or "Không thể" in r)

        # Tạo kết luận
        if live_count >= 3:
            conclusion = "✅ WEBSITE LIVE - Hoạt động tốt"
        elif blocked_count >= 3:
            conclusion = "🚫 WEBSITE BỊ CHẶN - Không truy cập được"
        elif timeout_count >= 3:
            conclusion = "⏱️ WEBSITE TIMEOUT - Phản hồi chậm"
        elif error_count >= 3:
            conclusion = "❌ WEBSITE ERROR - Có vấn đề kết nối"
        else:
            conclusion = "⚠️ WEBSITE KHÔNG ỔN ĐỊNH - Kết quả hỗn hợp"

        # Tạo báo cáo
        report = (
            f"🌐 <b>KIỂM TRA WEBSITE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 URL: <code>{url}</code>\n"
            f"🔄 Số lần test: 5 lần\n"
            f"⏳ Thời gian test: {time.strftime('%H:%M:%S')}\n\n"
            f"📊 <b>KẾT QUả CHI TIẾT:</b>\n"
        )
        
        for result in results:
            report += f"• {result}\n"

        report += (
            f"\n📈 <b>THỐNG KÊ:</b>\n"
            f"✅ Live: {live_count}/5 lần\n"
            f"🚫 Bị chặn: {blocked_count}/5 lần\n"
            f"⏱️ Timeout: {timeout_count}/5 lần\n"
            f"❌ Lỗi: {error_count}/5 lần\n\n"
            f"🏁 <b>KẾT LUẬN:</b> {conclusion}\n\n"
            f"📝 <i>Bot kiểm tra tự động - Kết quả có thể thay đổi</i>"
        )

        # Xoá thông báo đang xử lý
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass

        # Gửi kết quả
        bot.reply_to(message, report, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi hệ thống: {str(e)}")

# Thêm handler cho command checkweb với alias
@bot.message_handler(commands=['webcheck', 'kiemtraweb'])
def check_website_alias(message):
    check_website(message)