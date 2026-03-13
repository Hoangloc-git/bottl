# commands/checkweb.py
import requests
import time
import socket
import ssl
import whois
import base64
from datetime import datetime
from bs4 import BeautifulSoup
from telebot import types
from main import bot
import json

@bot.message_handler(commands=['checkthongtinweb'])
def check_website_info(message):
    try:
        # Tách lấy URL từ tin nhắn
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập URL cần kiểm tra!\n\n👉 Ví dụ: /checkthongtinweb https://google.com")
            return

        url = parts[1].strip()
        original_url = url
        
        # Thêm http:// nếu URL không có scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Gửi thông báo đang xử lý với hiệu ứng loading
        loading_icons = ["🌐", "🔄", "🌀", "💫", "⚡", "✨", "🌟"]
        loading_msg = None
        start_time = time.time()
        
        # Hiệu ứng loading
        def update_loading(stage, details=""):
            nonlocal loading_msg
            elapsed = time.time() - start_time
            icon = loading_icons[int(elapsed) % len(loading_icons)]
            
            loading_text = f"""
{icon} <b>ĐANG PHÂN TÍCH THÔNG TIN WEBSITE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 <b>URL:</b> <code>{original_url}</code>
⏳ <b>Thời gian:</b> {elapsed:.1f}s
📊 <b>Giai đoạn:</b> {stage}
{details}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Đang xử lý, vui lòng chờ...
            """
            
            if loading_msg:
                try:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=loading_msg.message_id,
                        text=loading_text,
                        parse_mode="HTML"
                    )
                except:
                    pass
            else:
                loading_msg = bot.reply_to(message, loading_text, parse_mode="HTML")

        # Gửi action typing
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Bước 1: Kiểm tra kết nối cơ bản
        update_loading("🔍 Kiểm tra kết nối...")
        connection_results = []
        response_times = []
        
        # Kiểm tra 3 lần
        for i in range(3):
            try:
                test_start = time.time()
                response = requests.get(
                    url, 
                    timeout=5,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    },
                    allow_redirects=True
                )
                test_end = time.time()
                
                response_time = round((test_end - test_start) * 1000, 2)
                response_times.append(response_time)
                
                status_emoji = "✅" if response.status_code == 200 else "⚠️"
                status_text = f"{status_emoji} Lần {i+1}: HTTP {response.status_code} - {response_time}ms"
                if len(response.history) > 0:
                    status_text += f" (Redirect {len(response.history)} lần)"
                
                connection_results.append(status_text)
                
            except Exception as e:
                connection_results.append(f"❌ Lần {i+1}: Lỗi - {str(e)[:30]}")
                time.sleep(1)
        
        # Bước 2: Lấy thông tin IP và DNS
        update_loading("🌍 Phân tích DNS & IP...", "🔍 Đang truy vấn thông tin máy chủ")
        
        domain_info = extract_domain_info(url)
        ip_info = get_ip_info(domain_info['domain'])
        
        # Bước 3: Lấy thông tin SSL
        update_loading("🔒 Kiểm tra SSL/TLS...", "📜 Đang phân tích chứng chỉ bảo mật")
        ssl_info = get_ssl_info(domain_info['domain'])
        
        # Bước 4: Lấy thông tin WHOIS
        update_loading("📋 Truy vấn WHOIS...", "🏢 Đang tìm thông tin đăng ký tên miền")
        whois_info = get_whois_info(domain_info['domain'])
        
        # Bước 5: Phân tích HTML
        update_loading("📄 Phân tích mã nguồn...", "🖥️ Đang đọc và phân tích HTML")
        html_info = analyze_html(url)
        
        # Bước 6: Kiểm tra server headers
        update_loading("📊 Phân tích headers...", "🔧 Đang kiểm tra cấu hình server")
        headers_info = get_server_headers(url)
        
        # Bước 7: Tạo link xem source code
        update_loading("🔗 Tạo link source code...", "📝 Đang chuẩn bị link xem mã nguồn")
        source_links = create_source_links(url)
        
        # Tính toán kết quả tổng quan
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        success_count = sum(1 for r in connection_results if "✅" in r)
        success_rate = (success_count / 3) * 100
        
        # Tạo báo cáo chi tiết
        report = f"""
🏁 <b>BÁO CÁO THÔNG TIN WEBSITE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 <b>URL đích:</b> <code>{url}</code>
⏰ <b>Thời gian phân tích:</b> {time.time()-start_time:.1f} giây
📅 <b>Ngày giờ:</b> {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}

📊 <b>KẾT QUẢ KIỂM TRA KẾT NỐI:</b>
{chr(10).join(connection_results)}
📈 <b>Trung bình:</b> {avg_response:.2f}ms | 📉 <b>Tỉ lệ thành công:</b> {success_rate:.1f}%

🌐 <b>THÔNG TIN DOMAIN & IP:</b>
├ 🏷️ <b>Domain:</b> {domain_info['domain']}
├ 📍 <b>IP Address:</b> {ip_info.get('ip', 'N/A')}
├ 🏙️ <b>Thành phố:</b> {ip_info.get('city', 'N/A')}
├ 🌍 <b>Quốc gia:</b> {ip_info.get('country', 'N/A')} {ip_info.get('country_flag', '')}
├ 🏢 <b>Nhà cung cấp:</b> {ip_info.get('isp', 'N/A')}
└ 📡 <b>Tổ chức:</b> {ip_info.get('org', 'N/A')}

🔒 <b>THÔNG TIN SSL/TLS:</b>
├ 🔐 <b>Trạng thái:</b> {ssl_info['status']}
├ 📅 <b>Có hiệu lực từ:</b> {ssl_info['valid_from']}
├ ⏳ <b>Hết hạn:</b> {ssl_info['valid_until']}
├ ⏱️ <b>Còn lại:</b> {ssl_info['days_left']} ngày
└ 🏢 <b>Nhà phát hành:</b> {ssl_info['issuer']}

📋 <b>THÔNG TIN WHOIS:</b>
├ 🏢 <b>Đăng ký bởi:</b> {whois_info.get('registrar', 'N/A')}
├ 📧 <b>Email:</b> {whois_info.get('email', 'N/A')}
├ 📞 <b>Điện thoại:</b> {whois_info.get('phone', 'N/A')}
├ 📍 <b>Quốc gia:</b> {whois_info.get('country', 'N/A')}
├ 🗓️ <b>Ngày tạo:</b> {whois_info.get('creation_date', 'N/A')}
└ 🗓️ <b>Ngày hết hạn:</b> {whois_info.get('expiration_date', 'N/A')}

🖥️ <b>THÔNG TIN WEBSITE:</b>
├ 📄 <b>Tiêu đề:</b> {html_info.get('title', 'N/A')}
├ 🔤 <b>Mã hóa:</b> {html_info.get('encoding', 'N/A')}
├ 📝 <b>Meta Description:</b> {html_info.get('description', 'N/A')[:80]}...
├ 🔑 <b>Meta Keywords:</b> {html_info.get('keywords', 'N/A')[:60]}...
├ 🔗 <b>Số liên kết:</b> {html_info.get('links_count', 0)}
├ 📏 <b>Kích thước HTML:</b> {html_info.get('html_size', 0):,} bytes
└ 🏷️ <b>Thẻ meta:</b> {html_info.get('meta_count', 0)} thẻ

📊 <b>THÔNG TIN SERVER:</b>
├ 🖥️ <b>Server Software:</b> {headers_info.get('server', 'N/A')}
├ ⚡ <b>X-Powered-By:</b> {headers_info.get('x-powered-by', 'N/A')}
├ 🍪 <b>Cookies:</b> {headers_info.get('cookies', 'Không có')}
├ 📍 <b>Content-Type:</b> {headers_info.get('content-type', 'N/A')}
└ 🔐 <b>Security Headers:</b> {headers_info.get('security', '0')} headers

🔗 <b>LINK XEM SOURCE CODE:</b>
├ 📄 <b>ViewSource.Online:</b> <a href="https://view-source.online/#{url}">Xem ngay</a>
├ 👁️ <b>View Page Source:</b> <a href="https://view-page-source.com/?url={url}">Xem ngay</a>
├ 🔍 <b>CodeBeautify:</b> <a href="https://codebeautify.org/source-code-viewer#url={url}">Xem ngay</a>
└ 📝 <b>Local HTML File:</b> <code>/getsource {original_url}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 <b>ĐÁNH GIÁ TỔNG QUAN:</b>
{get_overall_assessment(success_rate, avg_response, ssl_info, whois_info)}

💡 <i>Bot phân tích thông tin website tự động</i>
🔍 <i>Công cụ: Website Inspector v2.0</i>
        """
        
        # Xóa thông báo loading
        try:
            bot.delete_message(message.chat.id, loading_msg.message_id)
        except:
            pass
        
        # Gửi báo cáo với nút xem source code
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn1 = types.InlineKeyboardButton("📄 ViewSource.Online", url=f"https://view-source.online/#{url}")
        btn2 = types.InlineKeyboardButton("👁️ View Page Source", url=f"https://view-page-source.com/?url={url}")
        btn3 = types.InlineKeyboardButton("🔍 CodeBeautify", url=f"https://codebeautify.org/source-code-viewer#url={url}")
        btn4 = types.InlineKeyboardButton("📥 Tải HTML", callback_data=f"download_html:{url}")
        
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.send_message(
            message.chat.id, 
            report, 
            parse_mode="HTML", 
            disable_web_page_preview=True,
            reply_markup=markup
        )

    except Exception as e:
        if 'loading_msg' in locals() and loading_msg:
            try:
                bot.delete_message(message.chat.id, loading_msg.message_id)
            except:
                pass
        bot.reply_to(message, f"⚠️ Lỗi hệ thống: {str(e)}")

# ========== CÁC HÀM HỖ TRỢ ==========

def extract_domain_info(url):
    """Trích xuất thông tin domain từ URL"""
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    domain = parsed.netloc
    if ':' in domain:
        domain = domain.split(':')[0]
    
    return {
        'domain': domain,
        'scheme': parsed.scheme,
        'path': parsed.path
    }

def get_ip_info(domain):
    """Lấy thông tin IP và địa lý"""
    try:
        # Lấy IP
        ip = socket.gethostbyname(domain)
        
        # Lấy thông tin địa lý từ ip-api.com
        try:
            geo_response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
            geo_data = geo_response.json()
            
            # Emoji cờ quốc gia
            country_flags = {
                'VN': '🇻🇳', 'US': '🇺🇸', 'GB': '🇬🇧', 'JP': '🇯🇵', 
                'KR': '🇰🇷', 'CN': '🇨🇳', 'SG': '🇸🇬', 'TH': '🇹🇭',
                'FR': '🇫🇷', 'DE': '🇩🇪', 'RU': '🇷🇺', 'IN': '🇮🇳',
                'AU': '🇦🇺', 'CA': '🇨🇦', 'BR': '🇧🇷', 'ID': '🇮🇩'
            }
            
            country_code = geo_data.get('countryCode', '')
            country_flag = country_flags.get(country_code, '🏳️')
            
            return {
                'ip': ip,
                'city': geo_data.get('city', 'N/A'),
                'region': geo_data.get('regionName', 'N/A'),
                'country': geo_data.get('country', 'N/A'),
                'country_flag': country_flag,
                'isp': geo_data.get('isp', 'N/A'),
                'org': geo_data.get('org', 'N/A')
            }
        except:
            return {'ip': ip}
            
    except:
        return {'ip': 'Không xác định'}

def get_ssl_info(domain):
    """Lấy thông tin SSL/TLS"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        # Parse thông tin cert
        issuer = dict(x[0] for x in cert['issuer'])
        subject = dict(x[0] for x in cert['subject'])
        
        # Tính ngày hết hạn
        from datetime import datetime
        not_after = cert['notAfter']
        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
        days_left = (expiry_date - datetime.now()).days
        
        status_emoji = "✅" if days_left > 0 else "⚠️"
        status_text = f"{status_emoji} {'Hợp lệ' if days_left > 0 else 'Hết hạn'}"
        
        return {
            'status': status_text,
            'valid_from': cert['notBefore'],
            'valid_until': not_after,
            'days_left': days_left,
            'issuer': issuer.get('organizationName', 'Unknown'),
            'subject': subject.get('commonName', 'Unknown')
        }
    except:
        return {
            'status': '❌ Không có SSL/TLS',
            'valid_from': 'N/A',
            'valid_until': 'N/A',
            'days_left': 0,
            'issuer': 'N/A',
            'subject': 'N/A'
        }

def get_whois_info(domain):
    """Lấy thông tin WHOIS"""
    try:
        w = whois.whois(domain)
        
        return {
            'registrar': w.registrar if w.registrar else 'Không công khai',
            'email': w.emails[0] if w.emails else 'Ẩn',
            'phone': w.phone if w.phone else 'Ẩn',
            'country': w.country if w.country else 'N/A',
            'creation_date': str(w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date),
            'expiration_date': str(w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date)
        }
    except:
        return {
            'registrar': 'Không thể truy vấn',
            'email': 'N/A',
            'phone': 'N/A',
            'country': 'N/A',
            'creation_date': 'N/A',
            'expiration_date': 'N/A'
        }

def analyze_html(url):
    """Phân tích HTML của website"""
    try:
        response = requests.get(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lấy tiêu đề
        title = soup.title.string.strip() if soup.title else 'Không có tiêu đề'
        
        # Lấy meta description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag else 'Không có'
        
        # Lấy meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag['content'].strip() if keywords_tag else 'Không có'
        
        # Đếm liên kết và meta tags
        links = soup.find_all('a')
        meta_tags = soup.find_all('meta')
        
        # Encoding
        encoding = response.encoding
        
        return {
            'title': title[:100],
            'description': description[:200],
            'keywords': keywords[:150],
            'links_count': len(links),
            'meta_count': len(meta_tags),
            'encoding': encoding,
            'html_size': len(response.content)
        }
    except:
        return {
            'title': 'Không thể truy cập',
            'description': 'N/A',
            'keywords': 'N/A',
            'links_count': 0,
            'meta_count': 0,
            'encoding': 'N/A',
            'html_size': 0
        }

def get_server_headers(url):
    """Phân tích server headers"""
    try:
        response = requests.head(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        headers = response.headers
        
        # Đếm security headers
        security_headers = ['Strict-Transport-Security', 'Content-Security-Policy', 
                          'X-Frame-Options', 'X-Content-Type-Options', 
                          'X-XSS-Protection', 'Referrer-Policy']
        security_count = sum(1 for h in security_headers if h in headers)
        
        return {
            'server': headers.get('Server', 'N/A'),
            'x-powered-by': headers.get('X-Powered-By', 'N/A'),
            'cookies': 'Có' if 'Set-Cookie' in headers else 'Không có',
            'content-type': headers.get('Content-Type', 'N/A'),
            'security': security_count
        }
    except:
        return {
            'server': 'N/A',
            'x-powered-by': 'N/A',
            'cookies': 'Không xác định',
            'content-type': 'N/A',
            'security': 0
        }

def create_source_links(url):
    """Tạo các link để xem source code"""
    encoded_url = requests.utils.quote(url)
    
    return {
        'view_source_online': f'https://view-source.online/#{url}',
        'view_page_source': f'https://view-page-source.com/?url={encoded_url}',
        'codebeautify': f'https://codebeautify.org/source-code-viewer#url={encoded_url}',
        'html_validation': f'https://validator.w3.org/nu/?doc={encoded_url}'
    }

def get_overall_assessment(success_rate, avg_response, ssl_info, whois_info):
    """Đánh giá tổng quan website"""
    assessment = []
    
    # Đánh giá kết nối
    if success_rate >= 90:
        assessment.append("✅ <b>Kết nối:</b> Rất ổn định và nhanh")
    elif success_rate >= 70:
        assessment.append("⚠️ <b>Kết nối:</b> Khá ổn định")
    else:
        assessment.append("❌ <b>Kết nối:</b> Không ổn định")
    
    # Đánh giá tốc độ
    if avg_response < 500:
        assessment.append("⚡ <b>Tốc độ:</b> Rất nhanh")
    elif avg_response < 1500:
        assessment.append("🐢 <b>Tốc độ:</b> Chấp nhận được")
    else:
        assessment.append("⏱️ <b>Tốc độ:</b> Chậm")
    
    # Đánh giá SSL
    if "✅" in ssl_info['status']:
        if ssl_info['days_left'] > 30:
            assessment.append("🔒 <b>Bảo mật:</b> SSL hợp lệ")
        else:
            assessment.append("⚠️ <b>Bảo mật:</b> SSL sắp hết hạn")
    else:
        assessment.append("🚫 <b>Bảo mật:</b> Không có SSL/TLS")
    
    # Đánh giá thông tin
    if whois_info['registrar'] not in ['Không công khai', 'Không thể truy vấn']:
        assessment.append("📋 <b>Thông tin:</b> Đã đăng ký công khai")
    else:
        assessment.append("🕵️ <b>Thông tin:</b> Ẩn danh/Private")
    
    return '\n'.join(assessment)

# Lệnh riêng để tải source code
@bot.message_handler(commands=['getsource', 'taihtml', 'downloadhtml'])
def download_html_source(message):
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập URL!\n\n👉 Ví dụ: /getsource https://google.com")
            return
        
        url = parts[1].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        loading = bot.reply_to(message, "📥 Đang tải mã nguồn HTML...")
        
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Tạo file HTML tạm
        filename = f"source_{int(time.time())}.html"
        html_content = f"""<!-- Source code of: {url} -->
<!-- Downloaded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
<!-- Tool: Telegram Website Inspector Bot -->
{response.text}"""
        
        # Lưu file tạm
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Gửi file
        with open(filename, 'rb') as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=f"📄 <b>Mã nguồn HTML của:</b> {url}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                parse_mode="HTML"
            )
        
        # Xóa file tạm
        import os
        os.remove(filename)
        
        bot.delete_message(message.chat.id, loading.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi khi tải source: {str(e)}")

# Handler callback cho nút tải HTML
@bot.callback_query_handler(func=lambda call: call.data.startswith('download_html:'))
def callback_download_html(call):
    try:
        url = call.data.split(':', 1)[1]
        download_html_source(call.message)
        bot.answer_callback_query(call.id, "📥 Đang tải mã nguồn HTML...")
    except:
        bot.answer_callback_query(call.id, "❌ Lỗi khi tải mã nguồn")

# Thêm alias cho lệnh chính
@bot.message_handler(commands=['webinfo', 'siteinfo', 'checkwebinfo', 'thongtinweb'])
def check_website_info_alias(message):
    check_website_info(message)

# Lệnh riêng chỉ để lấy link source code
@bot.message_handler(commands=['viewsource', 'xemcode', 'htmlsource', 'sourcecode'])
def get_source_links_only(message):
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập URL!\n\n👉 Ví dụ: /viewsource https://google.com")
            return
        
        url = parts[1].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        links = create_source_links(url)
        
        source_msg = f"""
🔗 <b>LINK XEM SOURCE CODE WEBSITE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 <b>URL:</b> <code>{url}</code>
📅 <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}

📄 <b>Các trang xem mã nguồn:</b>

1. <b>ViewSource.Online</b>
👉 <a href="{links['view_source_online']}">Xem Source Code Ngay</a>
📝 <i>Xem trực tiếp mã nguồn HTML</i>

2. <b>View Page Source</b>
👉 <a href="{links['view_page_source']}">Xem Source Code Ngay</a>
📝 <i>Phân tích mã nguồn chi tiết</i>

3. <b>CodeBeautify Viewer</b>
👉 <a href="{links['codebeautify']}">Xem Source Code Ngay</a>
📝 <i>Xem với định dạng đẹp</i>

4. <b>W3C Validator</b>
👉 <a href="{links['html_validation']}">Kiểm tra HTML</a>
📝 <i>Kiểm tra chuẩn HTML/W3C</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Lệnh tải về:</b> <code>/getsource {url}</code>
🔧 <i>Để phân tích chi tiết, dùng: /checkthongtinweb {url}</i>
        """
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📄 ViewSource.Online", url=links['view_source_online'])
        btn2 = types.InlineKeyboardButton("👁️ View Page Source", url=links['view_page_source'])
        btn3 = types.InlineKeyboardButton("🔍 CodeBeautify", url=links['codebeautify'])
        btn4 = types.InlineKeyboardButton("⚡ Tải HTML", callback_data=f"download_html:{url}")
        
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.send_message(
            message.chat.id, 
            source_msg, 
            parse_mode="HTML", 
            disable_web_page_preview=True,
            reply_markup=markup
        )
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")