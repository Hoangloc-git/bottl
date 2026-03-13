import requests
import json
from datetime import datetime
from main import bot
import time

# =============== COMMON FUNCTIONS ===============
def get_current_time():
    """Lấy thời gian hiện tại"""
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

# =============== HITCLUB API HANDLER ===============
def get_hitclub_data():
    """Lấy dữ liệu từ API HitClub"""
    try:
        response = requests.get("https://hitclub-ovh1.onrender.com/api/taixiu", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def format_hitclub_message(data):
    """Format message HitClub đẹp với dữ liệu đầy đủ"""
    if not data:
        return "❌ Không thể kết nối đến API hoặc API không phản hồi"
    
    current_time = get_current_time()
    
    # Xác định emoji cho kết quả
    ket_qua_emoji = "🟢" if data.get('ket_qua') == "Tài" else "🔴"
    du_doan_emoji = "🟢" if data.get('du_doan') == "Tài" else "🔴"
    
    # Xác định dice emoji
    dice_emojis = {
        1: "⚀", 2: "⚁", 3: "⚂", 
        4: "⚃", 5: "⚄", 6: "⚅"
    }
    
    xuc_xac_1_emoji = dice_emojis.get(data.get('xuc_xac_1', 1), "🎲")
    xuc_xac_2_emoji = dice_emojis.get(data.get('xuc_xac_2', 1), "🎲")
    xuc_xac_3_emoji = dice_emojis.get(data.get('xuc_xac_3', 1), "🎲")
    
    # Xác định kết quả dựa trên tổng điểm
    tong_diem = data.get('tong', 0)
    if tong_diem >= 11:
        phan_tich_tong = "Tổng ≥ 11 → Tài"
    else:
        phan_tich_tong = "Tổng < 11 → Xỉu"
    
    message = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         🎰 *HITCLUB TÀI XỈU*          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📅 *Thời gian:* {current_time}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔢 *THÔNG TIN PHIÊN*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 📈 *Phiên trước:* `{data.get('phien', 'N/A')}`
• 📉 *Phiên hiện tại:* `{data.get('phien_hien_tai', 'N/A')}`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🎲 *KẾT QUẢ XÚC XẮC*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{xuc_xac_1_emoji} *Xúc xắc 1:* `{data.get('xuc_xac_1', 'N/A')}`
{xuc_xac_2_emoji} *Xúc xắc 2:* `{data.get('xuc_xac_2', 'N/A')}`
{xuc_xac_3_emoji} *Xúc xắc 3:* `{data.get('xuc_xac_3', 'N/A')}`

• 🧮 *Tổng điểm:* `{data.get('tong', 'N/A')}`
• 📊 *Phân tích:* {phan_tich_tong}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🏆 *KẾT QUẢ & DỰ ĐOÁN*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{ket_qua_emoji} *Kết quả phiên trước:* **{data.get('ket_qua', 'N/A')}**
{du_doan_emoji} *Dự đoán phiên tiếp:* **{data.get('du_doan', 'N/A')}**

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📝 *THÔNG TIN THỐNG KÊ*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🔍 *Phân tích toán học:* 
  - Xúc xắc: [{data.get('xuc_xac_1')}, {data.get('xuc_xac_2')}, {data.get('xuc_xac_3')}]
  - Tổng: {data.get('tong')} điểm
  - Kết quả: {data.get('ket_qua')} (Theo luật: Tổng ≥ 11 = Tài, < 11 = Xỉu)

• 🎯 *Dự đoán tiếp theo:* {data.get('du_doan')}
  - Dựa trên thuật toán phân tích xác suất
  - Cập nhật theo thời gian thực

*🔄 Dữ liệu được cập nhật tự động mỗi lần gọi API*
    """
    return message

# =============== SUNWIN API HANDLER ===============
def get_sunwin_data():
    """Lấy dữ liệu từ API Sunwin"""
    try:
        response = requests.get("https://sunwinsaygex-vd0m.onrender.com/api/sun", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def format_sunwin_message(data):
    """Format message Sunwin đẹp với dữ liệu chi tiết"""
    if not data:
        return "❌ Không thể kết nối đến API Sunwin hoặc API không phản hồi"
    
    current_time = get_current_time()
    
    # Xác định emoji cho kết quả
    ket_qua_emoji = "🟢" if data.get('ket_qua') == "Tài" else "🔴"
    
    # Xác định dice emoji
    dice_emojis = {
        1: "⚀", 2: "⚁", 3: "⚂", 
        4: "⚃", 5: "⚄", 6: "⚅"
    }
    
    xuc_xac_1_emoji = dice_emojis.get(data.get('xuc_xac_1', 1), "🎲")
    xuc_xac_2_emoji = dice_emojis.get(data.get('xuc_xac_2', 1), "🎲")
    xuc_xac_3_emoji = dice_emojis.get(data.get('xuc_xac_3', 1), "🎲")
    
    # Xác định kết quả dựa trên tổng điểm
    tong_diem = data.get('tong', 0)
    if tong_diem >= 11:
        phan_tich_tong = "Tổng ≥ 11 → Tài"
    else:
        phan_tich_tong = "Tổng < 11 → Xỉu"
    
    # Lấy thông tin từ phân tích chi tiết
    phan_tich = data.get('phan_tich_chi_tiet', {})
    thong_ke = phan_tich.get('statistics', {})
    trends = phan_tich.get('trends', {})
    
    # Format xác suất
    xac_suat = data.get('xac_suat', {})
    ti_le_tai = thong_ke.get('ti_le_tai', '0%')
    ti_le_xiu = thong_ke.get('ti_le_xiu', '0%')
    
    # Lấy 10 phiên gần nhất
    last_10 = phan_tich.get('last_10_sessions', [])
    last_10_display = ""
    for i, ket_qua in enumerate(last_10[:10], 1):
        emoji = "🟢" if ket_qua == "Tài" else "🔴"
        last_10_display += f"{emoji} "
        if i % 5 == 0:
            last_10_display += "\n"
    
    # Format độ tin cậy
    do_tin_cay = data.get('do_tin_cay', 0)
    if do_tin_cay >= 70:
        tin_cay_emoji = "🟢"
        tin_cay_text = "CAO"
    elif do_tin_cay >= 40:
        tin_cay_emoji = "🟡"
        tin_cay_text = "TRUNG BÌNH"
    else:
        tin_cay_emoji = "🔴"
        tin_cay_text = "THẤP"
    
    # Tính điểm Tài/Xỉu từ scores
    scores = phan_tich.get('scores', {}).get('raw', {})
    pattern_scores = scores.get('pattern', {})
    diem_tai_pattern = pattern_scores.get('tai', 0)
    diem_xiu_pattern = pattern_scores.get('xiu', 0)
    
    message = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         🎰 *SUNWIN TÀI XỈU*           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📅 *Thời gian:* {current_time}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔢 *THÔNG TIN PHIÊN*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 📈 *Phiên trước:* `{data.get('phien', 'N/A')}`
• 📉 *Phiên hiện tại:* `{data.get('phien_hien_tai', 'N/A')}`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🎲 *KẾT QUẢ XÚC XẮC*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{xuc_xac_1_emoji} *Xúc xắc 1:* `{data.get('xuc_xac_1', 'N/A')}`
{xuc_xac_2_emoji} *Xúc xắc 2:* `{data.get('xuc_xac_2', 'N/A')}`
{xuc_xac_3_emoji} *Xúc xắc 3:* `{data.get('xuc_xac_3', 'N/A')}`

• 🧮 *Tổng điểm:* `{data.get('tong', 'N/A')}`
• 📊 *Phân tích:* {phan_tich_tong}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🏆 *KẾT QUẢ PHIÊN TRƯỚC*  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{ket_qua_emoji} *Kết quả:* **{data.get('ket_qua', 'N/A')}**

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📊 *THỐNG KÊ XÁC SUẤT*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 📈 *Tỉ lệ Tài/Xỉu:*
  - Tài: `{ti_le_tai}%`
  - Xỉu: `{ti_le_xiu}%`
  - Xác suất trực tiếp:
    • Tài: `{xac_suat.get('tai', 'N/A')}%`
    • Xỉu: `{xac_suat.get('xiu', 'N/A')}%`

• 🎯 *Độ tin cậy dự đoán:* {tin_cay_emoji} **{do_tin_cay}%** ({tin_cay_text})

• 📝 *Tổng số phiên phân tích:* `{thong_ke.get('tong_so_phien', 0)}`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📈 *PHÂN TÍCH XU HƯỚNG*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🔄 *Xu hướng ngắn hạn:* `{trends.get('trend_ngan_han', 'N/A')}`
• 📊 *Sức mạnh xu hướng:* `{trends.get('strength_ngan_han', 0)}%`
• 🎲 *Xu hướng dài hạn:* `{trends.get('trend_dai_han', 'N/A')}`
• 📊 *Điểm Tài/Xỉu:* Tài: `{diem_tai_pattern}`, Xỉu: `{diem_xiu_pattern}`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📋 *10 PHIÊN GẦN NHẤT*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{last_10_display}

• 📊 *Thống kê 10 phiên:*
  - Tài: `{phan_tich.get('recent', {}).get('last_10', {}).get('tai', 0)}` phiên
  - Xỉu: `{phan_tich.get('recent', {}).get('last_10', {}).get('xiu', 0)}` phiên

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔍 *PHÂN TÍCH CHI TIẾT*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🎯 *Phân tích mẫu:*
  - Chuỗi liên tiếp: `{phan_tich.get('patterns', [{}])[0].get('strength', 0) if phan_tich.get('patterns') else 0}%`
  - Xen kẽ: `{phan_tich.get('patterns', [{}])[1].get('strength', 0) if len(phan_tich.get('patterns', [])) > 1 else 0}%`
  - Nhóm: `{phan_tich.get('patterns', [{}])[2].get('strength', 0) if len(phan_tich.get('patterns', [])) > 2 else 0}%`
  - Tổng điểm: `{phan_tich.get('patterns', [{}])[3].get('strength', 0) if len(phan_tich.get('patterns', [])) > 3 else 0}%`

• 📊 *Phân bố tổng điểm:*
  - Trung bình: `{thong_ke.get('phan_bo_tong_diem', {}).get('trungBinhTong', 'N/A')}`
  - Độ lệch chuẩn: `{thong_ke.get('phan_bo_tong_diem', {}).get('doLechChuan', 'N/A')}`

• 🎲 *Điểm số phân tích:*
  - Pattern: Tài `{diem_tai_pattern}`, Xỉu `{diem_xiu_pattern}`
  - Xu hướng: Tài `{trends.get('diem_tai', 0)}`, Xỉu `{trends.get('diem_xiu', 0)}`

*🔬 Dữ liệu phân tích dựa trên thuật toán AI và thống kê toán học*
    """
    return message

# =============== TELEGRAM COMMAND HANDLERS ===============
@bot.message_handler(commands=['dudoantaixiu'])
def handle_dudoantaixiu(message):
    """Hiển thị hướng dẫn sử dụng"""
    help_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        🎰 *ĐỌC CẦU TÀI XỈU BOT*       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📅 *Thời gian:* {current_time}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚀 *LỆNH CÓ SẴN*          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• `/hitclub` - Xem kết quả Tài Xỉu HitClub
  - Hiển thị phiên trước và phiên hiện tại
  - Kết quả xúc xắc chi tiết
  - Dự đoán phiên tiếp theo

• `/sunwin` - Xem kết quả Tài Xỉu Sunwin
  - Phân tích chi tiết với AI
  - Thống kê xác suất
  - Xu hướng và dự đoán
  - 10 phiên gần nhất

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📊 *THÔNG TIN TÀI XỈU*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎲 Luật chơi Tài Xỉu:*
- 3 xúc xắc, mỗi xúc xắc từ 1-6 điểm
- Tổng 3 xúc xắc từ 3-18 điểm
- **Tài**: Tổng từ 11-18 điểm
- **Xỉu**: Tổng từ 3-10 điểm

*📈 Phân tích kết quả:*
- Dựa trên xác suất toán học
- Phân tích xu hướng
- Thống kê lịch sử
- Dự đoán AI

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ℹ️ *THÔNG TIN BỔ SUNG*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 📡 *Dữ liệu được cập nhật realtime*
• 🔒 *Bảo mật thông tin API*
• 📊 *Phân tích chính xác cao*
• 🎯 *Dự đoán dựa trên thuật toán*

*💡 Sử dụng các lệnh trên để xem kết quả chi tiết!*
    """.format(current_time=get_current_time())
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['hitclub'])
def handle_hitclub(message):
    """Xử lý lệnh /hitclub"""
    # Gửi thông báo đang xử lý
    processing_msg = bot.reply_to(message, 
        "⏳ *Đang lấy dữ liệu HitClub...*\n"
        "🔄 Kết nối API...",
        parse_mode='Markdown'
    )
    
    # Lấy dữ liệu từ API
    data = get_hitclub_data()
    
    if data:
        # Format và gửi message
        formatted_message = format_hitclub_message(data)
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.reply_to(message, formatted_message, parse_mode='Markdown')
    else:
        bot.edit_message_text(
            "❌ *Không thể lấy dữ liệu HitClub*\n\n"
            "Nguyên nhân có thể:\n"
            "• API không khả dụng\n"
            "• Mất kết nối internet\n"
            "• API đang bảo trì\n\n"
            "Vui lòng thử lại sau ít phút!",
            message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['sunwin'])
def handle_sunwin(message):
    """Xử lý lệnh /sunwin"""
    # Gửi thông báo đang xử lý
    processing_msg = bot.reply_to(message, 
        "⏳ *Đang lấy dữ liệu Sunwin...*\n"
        "🔄 Kết nối API và phân tích AI...",
        parse_mode='Markdown'
    )
    
    # Lấy dữ liệu từ API
    data = get_sunwin_data()
    
    if data:
        # Format và gửi message
        formatted_message = format_sunwin_message(data)
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.reply_to(message, formatted_message, parse_mode='Markdown')
    else:
        bot.edit_message_text(
            "❌ *Không thể lấy dữ liệu Sunwin*\n\n"
            "Nguyên nhân có thể:\n"
            "• API không khả dụng\n"
            "• Mất kết nối internet\n"
            "• API đang bảo trì\n\n"
            "Vui lòng thử lại sau ít phút!",
            message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )

# =============== INITIALIZATION ===============
# Không có output trên console khi import