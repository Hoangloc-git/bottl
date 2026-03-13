# checkuid.py
import requests
import sqlite3
import time
import threading
from datetime import datetime
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from main import bot

# Database setup
DB_PATH = "/home/container/data/fb_check.db"

# Khởi tạo database
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fb_uids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            uid TEXT NOT NULL,
            note TEXT,
            status TEXT DEFAULT 'unknown',
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, uid)
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# Hàm check UID
def check_uid_status(uid):
    try:
        url = f"https://graph.facebook.com/{uid}/picture?redirect=false"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.text
            if '"height"' in result and '"width"' in result:
                return "🟢 LIVE"
        return "🔴 DIE"
    except:
        return "🔴 DIE"

# /checkuid - LUÔN CHECK THỰC TẾ VÀ UPDATE DATABASE
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/checkuid'))
def handle_checkuid(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) == 1:
            bot.reply_to(message, 
                "🔍 <b>UID CHECKER</b>\n"
                "────────────────\n"
                "<code>/checkuid UID</code> - Check & update\n"
                "<code>/adduid UID [note]</code> - Thêm UID\n"
                "<code>/listuid</code> - Danh sách hiện tại\n"
                "<code>/deletetask UID</code> - Xóa UID\n"
                "────────────────\n"
                "<b>Ví dụ:</b>\n"
                "<code>/checkuid 4</code>",
                parse_mode="HTML"
            )
            return
        
        uid = parts[1].strip()
        
        if not uid.isdigit():
            bot.reply_to(message, "❌ UID phải là số!")
            return
        
        # Check trạng thái THỰC TẾ
        new_status = check_uid_status(uid)
        
        # UPDATE DATABASE nếu UID đã có
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Kiểm tra UID đã có trong DB chưa
        cursor.execute("SELECT status FROM fb_uids WHERE user_id = ? AND uid = ?", 
                      (message.from_user.id, uid))
        old_status_result = cursor.fetchone()
        
        # Nếu có thì UPDATE
        if old_status_result:
            old_status = old_status_result[0]
            cursor.execute('''
                UPDATE fb_uids 
                SET status = ?, last_checked = CURRENT_TIMESTAMP
                WHERE user_id = ? AND uid = ?
            ''', (new_status, message.from_user.id, uid))
        else:
            # Nếu chưa có thì INSERT
            cursor.execute('''
                INSERT INTO fb_uids (user_id, uid, status)
                VALUES (?, ?, ?)
            ''', (message.from_user.id, uid, new_status))
        
        conn.commit()
        conn.close()
        
        # Hiển thị kết quả
        if new_status == "🟢 LIVE":
            bot.reply_to(message, 
                f"✅ <b>UID LIVE</b>\n"
                f"────────────────\n"
                f"<b>UID:</b> <code>{uid}</code>\n"
                f"<b>Trạng thái:</b> {new_status}\n"
                f"<b>Đã cập nhật database</b>",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(message, 
                f"❌ <b>UID DIE</b>\n"
                f"────────────────\n"
                f"<b>UID:</b> <code>{uid}</code>\n"
                f"<b>Trạng thái:</b> {new_status}\n"
                f"<b>Đã cập nhật database</b>",
                parse_mode="HTML"
            )
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# /adduid
@bot.message_handler(commands=['adduid'])
def adduid_cmd(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ <code>/adduid UID [note]</code>", parse_mode="HTML")
            return
        
        uid = parts[1].strip()
        
        if not uid.isdigit():
            bot.reply_to(message, "❌ UID phải là số!")
            return
        
        note = " ".join(parts[2:]) if len(parts) > 2 else ""
        
        # Check trạng thái THỰC TẾ và lưu
        status = check_uid_status(uid)
        
        # Lưu vào DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO fb_uids (user_id, uid, note, status)
            VALUES (?, ?, ?, ?)
        ''', (message.from_user.id, uid, note, status))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, 
            f"✅ <b>Đã thêm UID</b>\n"
            f"────────────────\n"
            f"<b>UID:</b> <code>{uid}</code>\n"
            f"<b>Trạng thái:</b> {status}\n"
            f"<b>Ghi chú:</b> {note or 'Không có'}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# /listuid - LUÔN LẤY TỪ DATABASE (trạng thái mới nhất)
@bot.message_handler(commands=['listuid'])
def listuid_cmd(message: Message):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT uid, note, status, last_checked 
            FROM fb_uids 
            WHERE user_id = ? 
            ORDER BY last_checked DESC
        ''', (message.from_user.id,))
        
        uids = cursor.fetchall()
        conn.close()
        
        if not uids:
            bot.reply_to(message, "📭 Chưa có UID nào!")
            return
        
        response_text = f"📋 <b>DANH SÁCH UID ({len(uids)})</b>\n────────────────\n"
        
        for i, (uid, note, status, last_checked) in enumerate(uids, 1):
            # Format thời gian
            check_time = datetime.strptime(last_checked, '%Y-%m-%d %H:%M:%S').strftime('%H:%M %d/%m')
            note_text = f" - {note}" if note else ""
            
            response_text += f"{i}. {status} <code>{uid}</code>{note_text}\n"
            response_text += f"   🕐 Check: {check_time}\n"
        
        response_text += "────────────────\n"
        response_text += "<i>Trạng thái được cập nhật tự động</i>"
        
        bot.reply_to(message, response_text, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# /deletetask
@bot.message_handler(commands=['deletetask'])
def deletetask_cmd(message: Message):
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ <code>/deletetask UID</code>", parse_mode="HTML")
            return
        
        uid = parts[1].strip()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fb_uids WHERE user_id = ? AND uid = ?", 
                      (message.from_user.id, uid))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            bot.reply_to(message, f"✅ Đã xóa UID <code>{uid}</code>!", parse_mode="HTML")
        else:
            bot.reply_to(message, f"❌ Không tìm thấy UID <code>{uid}</code>!", parse_mode="HTML")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# Auto check - LUÔN UPDATE DATABASE KHI CÓ THAY ĐỔI
def auto_check_thread():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Lấy UID chưa check trong 20s
            cursor.execute('''
                SELECT user_id, uid, status 
                FROM fb_uids 
                WHERE datetime(last_checked) <= datetime('now', '-20 seconds')
                LIMIT 30
            ''')
            
            for user_id, uid, old_status in cursor.fetchall():
                # Check trạng thái mới
                new_status = check_uid_status(uid)
                
                # Update thời gian check
                cursor.execute('''
                    UPDATE fb_uids 
                    SET last_checked = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND uid = ?
                ''', (user_id, uid))
                
                # QUAN TRỌNG: Nếu status thay đổi -> UPDATE database
                if old_status != new_status:
                    cursor.execute('''
                        UPDATE fb_uids 
                        SET status = ?
                        WHERE user_id = ? AND uid = ?
                    ''', (new_status, user_id, uid))
                    
                    # Gửi thông báo
                    try:
                        if new_status == "🟢 LIVE":
                            bot.send_message(user_id, 
                                f"🎉 <b>UID LIVE LẠI!</b>\n"
                                f"────────────────\n"
                                f"<b>UID:</b> <code>{uid}</code>\n"
                                f"<b>Trước:</b> {old_status}\n"
                                f"<b>Hiện tại:</b> {new_status}\n"
                                f"<b>Đã cập nhật trong danh sách</b>",
                                parse_mode="HTML"
                            )
                        else:
                            bot.send_message(user_id, 
                                f"⚠️ <b>UID VỪA DIE!</b>\n"
                                f"────────────────\n"
                                f"<b>UID:</b> <code>{uid}</code>\n"
                                f"<b>Trước:</b> {old_status}\n"
                                f"<b>Hiện tại:</b> {new_status}\n"
                                f"<b>Đã cập nhật trong danh sách</b>",
                                parse_mode="HTML"
                            )
                    except:
                        pass
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Auto-check error: {e}")
        
        time.sleep(20)

# Chạy auto check
threading.Thread(target=auto_check_thread, daemon=True).start()

print("✅ UID Checker ready!")