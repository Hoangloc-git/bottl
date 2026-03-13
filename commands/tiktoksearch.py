import os
import json
import requests
import tempfile
import time
import io
from main import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# API endpoint từ adidaphat.site
API_BASE_URL = "https://dungkon.lol/tiktok"

# Lưu trữ tạm thời kết quả search cho mỗi user
user_search_data = {}

def download_image(url):
    """Tải ảnh từ URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except:
        return None

@bot.message_handler(commands=['tiktoksearch'])
def tiktok_search_command(message):
    """Tìm kiếm video TikTok với ảnh preview"""
    try:
        # Lấy từ khóa tìm kiếm
        if len(message.text.split()) < 2:
            bot.reply_to(message, 
                "🎬 **HƯỚNG DẪN TÌM KIẾM TIKTOK**\n\n"
                "📌 **Cú pháp:**\n"
                "`/tiktoksearch <từ khóa>`\n\n"
                "📝 **Ví dụ:**\n"
                "• `/tiktoksearch sad songs`\n"
                "• `/tiktoksearch funny cat`\n"
                "• `/tiktoksearch dance trend`\n\n"
                "🎯 **Sau đó chọn số video để tải!**",
                parse_mode="Markdown"
            )
            return
        
        keywords = message.text.split(' ', 1)[1]
        
        # Gửi thông báo đang xử lý
        processing_msg = bot.reply_to(message, 
            f"🔍 **ĐANG TÌM KIẾM...**\n\n"
            f"📝 Từ khóa: `{keywords}`\n"
            f"⏳ Vui lòng chờ trong giây lát...",
            parse_mode="Markdown"
        )
        
        # Gọi API tìm kiếm
        api_url = f"{API_BASE_URL}?type=searchvideo&keywords={keywords}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            bot.edit_message_text(
                "❌ **LỖI KẾT NỐI**\n\n"
                "Không thể kết nối đến API TikTok.\n"
                "Vui lòng thử lại sau!",
                message.chat.id, 
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            return
        
        data = response.json()
        
        if data.get("code") != 0:
            bot.edit_message_text(
                "❌ **KHÔNG TÌM THẤY**\n\n"
                f"Không tìm thấy video nào cho từ khóa: `{keywords}`\n"
                "Thử từ khóa khác hoặc tiếng Việt không dấu.",
                message.chat.id, 
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            return
        
        videos = data.get("data", {}).get("videos", [])
        
        if not videos:
            bot.edit_message_text(
                "❌ **KHÔNG CÓ KẾT QUẢ**\n\n"
                "Không tìm thấy video nào phù hợp.\n"
                "Thử từ khóa khác!",
                message.chat.id, 
                processing_msg.message_id,
                parse_mode="Markdown"
            )
            return
        
        # Lưu kết quả tìm kiếm cho user này
        user_id = message.from_user.id
        user_search_data[user_id] = {
            "keywords": keywords,
            "videos": videos,
            "timestamp": time.time()
        }
        
        # Xóa message xử lý
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # Gửi ảnh cover đầu tiên + danh sách
        send_search_results_with_images(message.chat.id, user_id, keywords, videos[:5], 1)
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Lỗi hệ thống:**\n`{str(e)[:100]}`", parse_mode="Markdown")

def send_search_results_with_images(chat_id, user_id, keywords, videos, page=1):
    """Gửi kết quả tìm kiếm với ảnh preview"""
    try:
        total_videos = len(user_search_data[user_id]["videos"]) if user_id in user_search_data else len(videos)
        
        # Gửi message giới thiệu
        intro_text = f"""
🎬 **KẾT QUẢ TÌM KIẾM TIKTOK**

📝 **Từ khóa:** `{keywords}`
📊 **Tìm thấy:** {total_videos} video
📑 **Trang:** {page}/{(total_videos-1)//5 + 1}

👇 **Chọn số để tải video:**
━━━━━━━━━━━━━━━━━━
"""
        
        intro_msg = bot.send_message(chat_id, intro_text, parse_mode="Markdown")
        
        # Gửi từng video với ảnh cover
        for i, video in enumerate(videos, start=(page-1)*5 + 1):
            # Lấy thông tin video
            video_id = video.get('video_id', '')
            title = video.get('title', 'Video TikTok')[:60]
            author = video.get('author', {}).get('nickname', 'Unknown')
            duration = video.get('duration', 0)
            play_count = format_number(video.get('play_count', 0))
            cover_url = video.get('cover', '')
            
            # Tạo caption cho ảnh
            caption = f"""
🎬 **Video {i}**

📌 **{title}**

👤 **Tác giả:** {author}
⏱️ **Thời lượng:** {duration}s
👁️ **Lượt xem:** {play_count}
❤️ **Lượt thích:** {format_number(video.get('digg_count', 0))}

👇 **Bấm nút [{i}] bên dưới để tải video**
"""
            
            # Tải và gửi ảnh cover
            if cover_url:
                try:
                    # Tải ảnh
                    img_data = download_image(cover_url)
                    if img_data:
                        # Gửi ảnh với caption
                        bot.send_photo(
                            chat_id,
                            img_data,
                            caption=caption,
                            parse_mode="Markdown"
                        )
                    else:
                        # Nếu không tải được ảnh, gửi text thay thế
                        bot.send_message(chat_id, caption, parse_mode="Markdown")
                except:
                    bot.send_message(chat_id, caption, parse_mode="Markdown")
            else:
                bot.send_message(chat_id, caption, parse_mode="Markdown")
            
            time.sleep(0.3)  # Delay để không bị rate limit
        
        # Tạo inline keyboard
        keyboard = InlineKeyboardMarkup()
        row_buttons = []
        
        # Nút số video
        start_num = (page-1)*5 + 1
        for i in range(start_num, start_num + len(videos)):
            row_buttons.append(InlineKeyboardButton(str(i), callback_data=f"tiktok_dl_{i}"))
            if len(row_buttons) == 5:  # 5 nút mỗi hàng
                keyboard.row(*row_buttons)
                row_buttons = []
        
        if row_buttons:
            keyboard.row(*row_buttons)
        
        # Nút điều hướng
        nav_buttons = []
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀️ Trang trước", callback_data=f"tiktok_page_{page-1}"))
        
        if total_videos > page * 5:
            nav_buttons.append(InlineKeyboardButton("Trang sau ▶️", callback_data=f"tiktok_page_{page+1}"))
        
        if nav_buttons:
            keyboard.row(*nav_buttons)
        
        # Nút chức năng
        keyboard.row(
            InlineKeyboardButton("🔄 Tìm lại", callback_data="tiktok_refresh"),
            InlineKeyboardButton("🎬 Tải nhiều", callback_data="tiktok_batch"),
            InlineKeyboardButton("❌ Hủy", callback_data="tiktok_cancel")
        )
        
        # Gửi message với nút bấm
        control_text = f"""
━━━━━━━━━━━━━━━━━━
📋 **ĐIỀU KHIỂN**

• Bấm số **[1-{min(start_num + len(videos) - 1, total_videos)}]** để tải video
• **Trang trước/Trang sau** để xem thêm
• **Tải nhiều** để chọn nhiều video cùng lúc
• **Tìm lại** để tìm từ khóa khác
━━━━━━━━━━━━━━━━━━
"""
        
        bot.send_message(
            chat_id,
            control_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi hiển thị kết quả: {str(e)[:100]}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('tiktok_'))
def handle_tiktok_callback(call):
    """Xử lý callback từ nút bấm"""
    user_id = call.from_user.id
    
    if user_id not in user_search_data:
        bot.answer_callback_query(call.id, "⚠️ Phiên tìm kiếm đã hết hạn!")
        return
    
    videos = user_search_data[user_id]["videos"]
    keywords = user_search_data[user_id]["keywords"]
    
    if call.data == "tiktok_cancel":
        bot.answer_callback_query(call.id, "Đã hủy tìm kiếm")
        # Xóa tất cả message từ bot trong cuộc trò chuyện
        try:
            for i in range(call.message.message_id - 20, call.message.message_id + 1):
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    pass
        except:
            pass
        return
    
    elif call.data == "tiktok_refresh":
        bot.answer_callback_query(call.id, "🔄 Đang làm mới...")
        # Xóa message cũ
        try:
            for i in range(call.message.message_id - 30, call.message.message_id + 1):
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    pass
        except:
            pass
        
        # Yêu cầu nhập từ khóa mới
        msg = bot.send_message(
            call.message.chat.id,
            "🔄 **TÌM KIẾM MỚI**\n\n"
            "Nhập từ khóa bạn muốn tìm kiếm:\n"
            "Ví dụ: `sad songs`, `funny videos`, `dance trend`\n\n"
            "Hoặc gõ: `/tiktoksearch <từ khóa>`",
            parse_mode="Markdown"
        )
        return
    
    elif call.data.startswith("tiktok_page_"):
        page = int(call.data.split("_")[2])
        bot.answer_callback_query(call.id, f"📄 Đang chuyển đến trang {page}")
        
        # Xóa message cũ
        try:
            for i in range(call.message.message_id - 40, call.message.message_id + 1):
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    pass
        except:
            pass
        
        # Hiển thị trang mới
        start_idx = (page-1) * 5
        end_idx = start_idx + 5
        send_search_results_with_images(
            call.message.chat.id, 
            user_id, 
            keywords, 
            videos[start_idx:end_idx], 
            page
        )
        return
    
    elif call.data == "tiktok_batch":
        bot.answer_callback_query(call.id, "📦 Chế độ tải nhiều")
        # Hiển thị hướng dẫn tải nhiều
        batch_msg = """
📦 **CHẾ ĐỘ TẢI NHIỀU VIDEO**

📌 **Cách sử dụng:**
Gửi các số video cách nhau bằng dấu phẩy

📝 **Ví dụ:**
• `1,3,5` - Tải video 1, 3 và 5
• `2-5` - Tải video từ 2 đến 5
• `1,3,7-10` - Kết hợp cả hai

⚠️ **Lưu ý:**
• Tối đa 5 video mỗi lần
• Video >50MB sẽ bị bỏ qua

👇 **Gửi số video bạn muốn tải:**
"""
        bot.send_message(call.message.chat.id, batch_msg, parse_mode="Markdown")
        return
    
    elif call.data.startswith("tiktok_dl_"):
        # Tải video được chọn
        try:
            video_index = int(call.data.split("_")[2]) - 1
            
            if video_index < 0 or video_index >= len(videos):
                bot.answer_callback_query(call.id, "⚠️ Video không tồn tại!")
                return
            
            video = videos[video_index]
            bot.answer_callback_query(call.id, f"📥 Đang tải video {video_index + 1}...")
            
            # Gửi thông báo đang tải với ảnh preview
            loading_msg = bot.send_message(
                call.message.chat.id,
                f"⏳ **ĐANG TẢI VIDEO {video_index + 1}**\n\n"
                f"📌 {video.get('title', 'Video TikTok')[:50]}...\n"
                f"👤 {video.get('author', {}).get('nickname', 'Unknown')}\n\n"
                f"🔄 Đang xử lý, vui lòng chờ...",
                parse_mode="Markdown"
            )
            
            # Gửi ảnh cover trước khi tải
            cover_url = video.get('cover', '')
            if cover_url:
                try:
                    img_data = download_image(cover_url)
                    if img_data:
                        bot.send_photo(
                            call.message.chat.id,
                            img_data,
                            caption=f"🖼️ **Ảnh preview video {video_index + 1}**",
                            parse_mode="Markdown"
                        )
                except:
                    pass
            
            # Tải video
            download_tiktok_video(call.message.chat.id, video, loading_msg.message_id, video_index + 1)
            
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)[:50]}")
    
    # Xóa dữ liệu cũ sau 10 phút
    cleanup_old_searches()

def download_tiktok_video(chat_id, video, loading_msg_id, video_number):
    """Tải và gửi video TikTok"""
    try:
        # Lấy URL video (ưu tiên không watermark)
        video_url = video.get('play')  # Video không watermark
        if not video_url:
            video_url = video.get('wmplay')  # Video có watermark
        
        if not video_url:
            bot.edit_message_text("❌ Không tìm thấy link video", chat_id, loading_msg_id)
            return
        
        # Thông tin video
        title = video.get('title', 'Video TikTok')[:100]
        author = video.get('author', {}).get('nickname', 'Unknown')
        duration = video.get('duration', 0)
        play_count = format_number(video.get('play_count', 0))
        
        # Cập nhật trạng thái
        bot.edit_message_text(
            f"📥 **ĐANG TẢI VIDEO {video_number}**\n\n"
            f"🎬 **{title}**\n"
            f"👤 **Tác giả:** {author}\n"
            f"⏱️ **Thời lượng:** {duration}s\n"
            f"👁️ **Lượt xem:** {play_count}\n\n"
            f"📊 **Kích thước:** Đang kiểm tra...\n"
            f"⏳ **Tiến trình:** 0%",
            chat_id,
            loading_msg_id,
            parse_mode="Markdown"
        )
        
        # Tải video về temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            response = requests.get(video_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size > 50 * 1024 * 1024:  # Giới hạn 50MB
                bot.edit_message_text(
                    "❌ **VIDEO QUÁ LỚN**\n\n"
                    "Video vượt quá 50MB, không thể gửi qua Telegram.\n"
                    "Vui lòng chọn video khác!",
                    chat_id,
                    loading_msg_id,
                    parse_mode="Markdown"
                )
                return
            
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Cập nhật tiến trình mỗi 10%
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if percent % 10 < 1:  # Cập nhật mỗi 10%
                            try:
                                bot.edit_message_text(
                                    f"📥 **ĐANG TẢI VIDEO {video_number}**\n\n"
                                    f"🎬 **{title[:50]}...**\n\n"
                                    f"📊 **Kích thước:** {format_size(total_size)}\n"
                                    f"⏳ **Tiến trình:** {percent:.0f}%\n"
                                    f"⬇️ **Đã tải:** {format_size(downloaded)}",
                                    chat_id,
                                    loading_msg_id,
                                    parse_mode="Markdown"
                                )
                            except:
                                pass
            
            tmp_file_path = tmp_file.name
        
        # Cập nhật trạng thái
        bot.edit_message_text(
            f"📤 **ĐANG GỬI VIDEO {video_number}**\n\n"
            f"✅ **Đã tải xong:** {format_size(downloaded)}\n"
            f"🔄 **Đang upload lên Telegram...**\n\n"
            f"⏳ Vui lòng chờ, đừng đóng ứng dụng!",
            chat_id,
            loading_msg_id,
            parse_mode="Markdown"
        )
        
        # Gửi video lên Telegram
        with open(tmp_file_path, 'rb') as video_file:
            # Tạo caption cho video
            caption = f"""
🎬 **VIDEO TIKTOK #{video_number}**

📌 **{title}**

👤 **Tác giả:** {author}
⏱️ **Thời lượng:** {duration} giây
👁️ **Lượt xem:** {play_count}
❤️ **Lượt thích:** {format_number(video.get('digg_count', 0))}
💬 **Bình luận:** {format_number(video.get('comment_count', 0))}
🔄 **Chia sẻ:** {format_number(video.get('share_count', 0))}

🔗 **Video ID:** `{video.get('video_id', 'N/A')}`
📍 **Khu vực:** {video.get('region', 'N/A')}

━━━━━━━━━━━━━━━━━━
📥 **Tải xuống bởi TikTok Bot**
🎬 Tìm thêm: /tiktoksearch
            """
            
            # Gửi video
            bot.send_video(
                chat_id,
                video_file,
                caption=caption,
                parse_mode="Markdown",
                duration=duration,
                supports_streaming=True
            )
        
        # Xóa file tạm
        os.unlink(tmp_file_path)
        
        # Cập nhật message loading thành hoàn tất
        bot.edit_message_text(
            f"✅ **ĐÃ TẢI XONG VIDEO {video_number}!**\n\n"
            f"🎬 **{title[:50]}...**\n\n"
            f"📁 File đã được gửi thành công!\n"
            f"🗑️ File tạm đã được xóa khỏi server.\n\n"
            f"🔍 **Tìm kiếm tiếp:** /tiktoksearch",
            chat_id,
            loading_msg_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ **LỖI KHI TẢI VIDEO**\n\n"
            f"**Lỗi:** `{str(e)[:200]}`\n\n"
            f"Vui lòng thử lại video khác!\n"
            f"Hoặc báo lỗi cho admin.",
            chat_id,
            loading_msg_id,
            parse_mode="Markdown"
        )

def format_number(num):
    """Định dạng số lớn"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def format_size(size_bytes):
    """Định dạng kích thước file"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes/1024:.1f} KB"
    return f"{size_bytes} bytes"

def cleanup_old_searches():
    """Dọn dẹp dữ liệu tìm kiếm cũ"""
    current_time = time.time()
    to_remove = []
    
    for user_id, data in user_search_data.items():
        if current_time - data["timestamp"] > 600:  # 10 phút
            to_remove.append(user_id)
    
    for user_id in to_remove:
        del user_search_data[user_id]

# Xử lý chế độ tải nhiều
@bot.message_handler(func=lambda m: m.text and any(c.isdigit() for c in m.text) and not m.text.startswith('/'))
def handle_batch_download(message):
    """Xử lý tải nhiều video"""
    try:
        user_id = message.from_user.id
        if user_id not in user_search_data:
            return
        
        videos = user_search_data[user_id]["videos"]
        numbers = message.text.strip()
        
        # Parse số video
        video_indices = set()
        for part in numbers.split(','):
            part = part.strip()
            if '-' in part:
                start_end = part.split('-')
                if len(start_end) == 2:
                    try:
                        start = int(start_end[0].strip())
                        end = int(start_end[1].strip())
                        for i in range(start, end + 1):
                            if 1 <= i <= len(videos):
                                video_indices.add(i - 1)
                    except:
                        pass
            else:
                try:
                    num = int(part)
                    if 1 <= num <= len(videos):
                        video_indices.add(num - 1)
                except:
                    pass
        
        if not video_indices:
            bot.reply_to(message, "❌ Không tìm thấy số video hợp lệ!")
            return
        
        if len(video_indices) > 5:
            bot.reply_to(message, "⚠️ Tối đa 5 video mỗi lần!")
            return
        
        # Xác nhận tải nhiều
        indices_list = sorted(list(video_indices))
        confirm_text = f"""
📦 **XÁC NHẬN TẢI NHIỀU VIDEO**

📊 **Số lượng:** {len(indices_list)} video
📝 **Danh sách:** {', '.join([str(i+1) for i in indices_list])}

📌 **Video sẽ được tải:**
"""
        
        for idx in indices_list:
            if idx < len(videos):
                video = videos[idx]
                title = video.get('title', 'Video TikTok')[:40]
                author = video.get('author', {}).get('nickname', 'Unknown')
                confirm_text += f"\n**{idx+1}. {title}...** - {author}"
        
        confirm_text += "\n\n⚠️ **Lưu ý:** Quá trình có thể mất vài phút!"
        confirm_text += "\n\n✅ **Bấm OK để bắt đầu tải:**"
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("✅ OK, bắt đầu tải", callback_data=f"tiktok_batch_confirm_{','.join([str(i) for i in indices_list])}"),
            InlineKeyboardButton("❌ Hủy", callback_data="tiktok_cancel")
        )
        
        bot.reply_to(message, confirm_text, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)[:100]}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('tiktok_batch_confirm_'))
def handle_batch_confirm(call):
    """Xác nhận tải nhiều video"""
    try:
        indices_str = call.data.split('_')[3]
        indices = [int(i) for i in indices_str.split(',')]
        
        user_id = call.from_user.id
        if user_id not in user_search_data:
            bot.answer_callback_query(call.id, "⚠️ Phiên đã hết hạn!")
            return
        
        videos = user_search_data[user_id]["videos"]
        
        bot.answer_callback_query(call.id, f"📥 Bắt đầu tải {len(indices)} video...")
        
        # Xóa message xác nhận
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Tải từng video
        for i, idx in enumerate(indices, 1):
            if idx < len(videos):
                video = videos[idx]
                
                # Thông báo đang tải video thứ i
                status_msg = bot.send_message(
                    call.message.chat.id,
                    f"📥 **ĐANG TẢI VIDEO {i}/{len(indices)}**\n\n"
                    f"🎬 {video.get('title', 'Video TikTok')[:50]}...\n"
                    f"👤 {video.get('author', {}).get('nickname', 'Unknown')}\n\n"
                    f"🔄 Đang xử lý...",
                    parse_mode="Markdown"
                )
                
                # Tải video
                download_tiktok_video(call.message.chat.id, video, status_msg.message_id, idx + 1)
                
                # Delay giữa các video
                if i < len(indices):
                    time.sleep(2)
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)[:50]}")

# Lệnh hướng dẫn chi tiết
@bot.message_handler(commands=['tiktokhelp'])
def tiktok_help_command(message):
    help_text = """
🎬 **HƯỚNG DẪN CHI TIẾT TIKTOK BOT**

━━━━━━━━━━━━━━━━━━

📌 **CÁCH SỬ DỤNG:**

1. **Tìm kiếm video:**
   `/tiktoksearch <từ khóa>`
   Ví dụ: `/tiktoksearch nhạc buồn`

2. **Xem kết quả:**
   • Bot sẽ hiển thị ảnh preview
   • Thông tin chi tiết từng video
   • Nút số để chọn tải

3. **Tải video:**
   • Bấm số tương ứng với video
   • Bot sẽ tải và gửi video
   • Hiển thị tiến trình tải

━━━━━━━━━━━━━━━━━━

🎯 **TÍNH NĂNG NỔI BẬT:**

• **Ảnh preview** - Xem trước video
• **Thông tin chi tiết** - Lượt xem, thời lượng, tác giả
• **Tải không watermark** - Ưu tiên video gốc
• **Tiến trình tải** - Hiển thị % tải về
• **Tải nhiều video** - Chọn nhiều video cùng lúc
• **Phân trang** - Xem nhiều kết quả

━━━━━━━━━━━━━━━━━━

⚠️ **LƯU Ý QUAN TRỌNG:**

• Video >50MB không gửi được
• Mỗi phiên tìm kiếm có hiệu lực 10 phút
• Sử dụng API bên thứ 3 (adidaphat.site)
• Có thể gặp lỗi với video bản quyền

━━━━━━━━━━━━━━━━━━

🛠️ **CÁC LỆNH KHÁC:**

• `/tiktoktest` - Kiểm tra API
• `/tiktokhelp` - Hướng dẫn này

━━━━━━━━━━━━━━━━━━

🎌 **CHÚC BẠN SỬ DỤNG VUI VẺ!**
    """
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

# Lệnh kiểm tra API
@bot.message_handler(commands=['tiktoktest'])
def tiktok_test_command(message):
    """Kiểm tra API hoạt động"""
    try:
        test_msg = bot.reply_to(message, 
            "🔧 **KIỂM TRA HỆ THỐNG TIKTOK**\n\n"
            "⏳ Đang kiểm tra kết nối API...",
            parse_mode="Markdown"
        )
        
        # Test với từ khóa mẫu
        api_url = f"{API_BASE_URL}?type=searchvideo&keywords=trending"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                videos_count = len(data.get("data", {}).get("videos", []))
                
                # Gửi ảnh test
                try:
                    test_img_url = "https://p16-sign-sg.tiktokcdn.com/obj/tiktok-obj/1664896110452737.png"
                    img_data = download_image(test_img_url)
                    if img_data:
                        bot.send_photo(
                            message.chat.id,
                            img_data,
                            caption="🖼️ **Ảnh test từ TikTok CDN**"
                        )
                except:
                    pass
                
                bot.edit_message_text(
                    f"✅ **HỆ THỐNG HOẠT ĐỘNG TỐT**\n\n"
                    f"📡 **Trạng thái:** Online\n"
                    f"⚡ **Ping API:** {response.elapsed.total_seconds():.2f}s\n"
                    f"📊 **Video test:** {videos_count} video\n"
                    f"🔄 **Xử lý ảnh:** Hoạt động\n\n"
                    f"🎬 **Sẵn sàng tìm kiếm video TikTok!**",
                    message.chat.id,
                    test_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    f"⚠️ **API TRẢ VỀ LỖI**\n\n"
                    f"**Mã lỗi:** {data.get('code', 'Unknown')}\n"
                    f"**Thông báo:** {data.get('msg', 'Unknown')}",
                    message.chat.id,
                    test_msg.message_id,
                    parse_mode="Markdown"
                )
        else:
            bot.edit_message_text(
                f"❌ **LỖI KẾT NỐI**\n\n"
                f"**Mã lỗi:** {response.status_code}\n"
                f"**Chi tiết:** Không thể kết nối đến API",
                message.chat.id,
                test_msg.message_id,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        bot.reply_to(message, f"❌ **Lỗi kiểm tra:**\n`{str(e)[:100]}`", parse_mode="Markdown")