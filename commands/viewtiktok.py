import os
import subprocess
import time
import threading
import sys
import json
import signal
from datetime import datetime
import atexit
import random

# =============== GLOBAL VARIABLES ===============
VIEW_PROCESSES = {}  # Lưu trữ nhiều process: {task_id: {process, start_time, target, chat_id, message_id}}
VIEW_TASK_COUNTER = 0
VIEW_TASK_FILE = "running_viewtasks.json"

# =============== SILENT UTILITY FUNCTIONS ===============
def get_commands_dir():
    """Lấy đường dẫn đến thư mục commands/"""
    return os.path.dirname(os.path.abspath(__file__))

def format_elapsed_time(start_time):
    """Định dạng thời gian đẹp - KHÔNG IN RA CONSOLE"""
    if not start_time:
        return "00:00:00"
    
    elapsed = time.time() - start_time
    
    if elapsed < 60:
        return f"00:00:{int(elapsed):02d}"
    elif elapsed < 3600:
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"00:{minutes:02d}:{seconds:02d}"
    else:
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_time_difference(start_time):
    """Tính thời gian chạy với đơn vị đẹp - KHÔNG IN RA CONSOLE"""
    if not start_time:
        return "0 giây"
    
    elapsed = time.time() - start_time
    
    if elapsed < 60:
        return f"{int(elapsed)} giây"
    elif elapsed < 3600:
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes} phút {seconds} giây"
    elif elapsed < 86400:
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        return f"{hours} giờ {minutes} phút"
    else:
        days = int(elapsed // 86400)
        hours = int((elapsed % 86400) // 3600)
        return f"{days} ngày {hours} giờ"

def validate_tiktok_url(url):
    """Kiểm tra URL TikTok hợp lệ"""
    if not url:
        return False, "❌ URL không được để trống!"
    
    if not url.startswith("http"):
        url = "https://" + url
    
    tiktok_domains = ['tiktok.com', 'vt.tiktok.com', 'vm.tiktok.com', 'www.tiktok.com']
    if not any(domain in url for domain in tiktok_domains):
        return False, "❌ URL phải là TikTok hợp lệ!"
    
    return True, url

def run_viewtik_script(url, task_id):
    """Chạy file viewtik.py với URL - CHẠY VĨNH VIỄN VÀ ẨN HOÀN TOÀN"""
    global VIEW_PROCESSES
    
    try:
        commands_dir = get_commands_dir()
        
        # Tìm file viewtik.py trong thư mục VIEW TIKTOK
        target_dir = os.path.join(commands_dir, "VIEW TIKTOK")
        viewtik_path = os.path.join(target_dir, "viewtik.py")
        
        if not os.path.exists(viewtik_path):
            return False, f"Không tìm thấy file viewtik.py"
        
        # CHẠY ẨN HOÀN TOÀN - KHÔNG OUTPUT TRÊN CONSOLE
        if sys.platform == "win32":
            # Windows: chạy ẩn hoàn toàn
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            VIEW_PROCESSES[task_id]['process'] = subprocess.Popen(
                ["python", "viewtik.py", url],
                cwd=target_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # Linux/Mac: chạy ẩn hoàn toàn
            VIEW_PROCESSES[task_id]['process'] = subprocess.Popen(
                ["python3", "viewtik.py", url],
                cwd=target_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=True,
                preexec_fn=os.setsid
            )
        
        pid = VIEW_PROCESSES[task_id]['process'].pid
        
        # Lưu thông tin task
        VIEW_PROCESSES[task_id]['start_time'] = time.time()
        VIEW_PROCESSES[task_id]['target'] = url
        VIEW_PROCESSES[task_id]['pid'] = pid
        VIEW_PROCESSES[task_id]['status'] = 'running'
        save_tasks()
        
        return True, f"Task {task_id} đang chạy vĩnh viễn (ẩn)"
        
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def stop_viewtik_task(task_id):
    """Dừng một task cụ thể - KHÔNG IN RA CONSOLE"""
    global VIEW_PROCESSES
    
    if task_id not in VIEW_PROCESSES:
        return False
    
    process_info = VIEW_PROCESSES[task_id]
    
    if process_info.get('process'):
        try:
            pid = process_info['pid']
            
            # Kill process và tất cả child processes
            if sys.platform == "win32":
                subprocess.run(
                    f"taskkill /PID {pid} /T /F >nul 2>&1",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                try:
                    # Kill toàn bộ process group
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(0.5)
                    os.kill(pid, signal.SIGKILL)
                except:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(0.5)
                        os.kill(pid, signal.SIGKILL)
                    except:
                        pass
            
        except:
            pass
    
    # Cập nhật thông tin task
    if task_id in VIEW_PROCESSES:
        # Xóa process object để tránh memory leak
        if 'process' in VIEW_PROCESSES[task_id]:
            VIEW_PROCESSES[task_id]['process'] = None
        
        # Đánh dấu đã dừng
        VIEW_PROCESSES[task_id]['status'] = 'stopped'
        VIEW_PROCESSES[task_id]['end_time'] = time.time()
    
    save_tasks()
    return True

def save_tasks():
    """Lưu thông tin tasks đang chạy vào file - KHÔNG IN RA CONSOLE"""
    try:
        tasks_to_save = {}
        for task_id, info in VIEW_PROCESSES.items():
            if info.get('status') == 'running':
                tasks_to_save[task_id] = {
                    'target': info.get('target', ''),
                    'start_time': info.get('start_time', 0),
                    'chat_id': info.get('chat_id'),
                    'message_id': info.get('message_id'),
                    'pid': info.get('pid'),
                    'status': 'running',
                    'username': info.get('username', 'Unknown')
                }
        
        with open(VIEW_TASK_FILE, 'w') as f:
            json.dump(tasks_to_save, f, indent=2)
    except:
        pass

def load_tasks():
    """Load tasks từ file (nếu có) - KHÔNG IN RA CONSOLE"""
    global VIEW_PROCESSES
    try:
        if os.path.exists(VIEW_TASK_FILE):
            with open(VIEW_TASK_FILE, 'r') as f:
                saved_tasks = json.load(f)
            
            # Chỉ load thông tin, không khôi phục process
            for task_id_str, info in saved_tasks.items():
                task_id = int(task_id_str)
                VIEW_PROCESSES[task_id] = {
                    'process': None,
                    'target': info.get('target', ''),
                    'start_time': info.get('start_time', 0),
                    'chat_id': info.get('chat_id'),
                    'message_id': info.get('message_id'),
                    'pid': info.get('pid'),
                    'status': 'stopped',  # Đánh dấu đã dừng
                    'username': info.get('username', 'Unknown')
                }
    except:
        pass

def cleanup_all_tasks():
    """Dọn dẹp tất cả tasks khi thoát - KHÔNG IN RA CONSOLE"""
    task_ids = list(VIEW_PROCESSES.keys())
    for task_id in task_ids:
        if VIEW_PROCESSES[task_id].get('status') == 'running':
            stop_viewtik_task(task_id)
    
    # Xóa file tasks
    try:
        if os.path.exists(VIEW_TASK_FILE):
            os.remove(VIEW_TASK_FILE)
    except:
        pass

# Đăng ký cleanup khi thoát
atexit.register(cleanup_all_tasks)
load_tasks()

# =============== TELEGRAM COMMAND HANDLERS ===============
try:
    # Import bot từ main.py
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    
    from main import bot
    
    @bot.message_handler(commands=['viewtiktok'])
    def handle_viewtiktok(message):
        """Xử lý lệnh /viewtiktok <url> - CHẠY VĨNH VIỄN"""
        global VIEW_TASK_COUNTER
        
        parts = message.text.split(' ', 1)
        
        # Nếu chỉ có lệnh không có URL -> hiển thị hướng dẫn
        if len(parts) < 2:
            help_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       🎬 *TIKTOK VIEW BOT PRO*        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*✨ CHẠY VĨNH VIỄN - KHÔNG TỰ DỪNG*

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚀 *CÁCH DÙNG*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

`/viewtiktok <url_tiktok>`

*📌 VÍ DỤ:*
• `/viewtiktok https://www.tiktok.com/@username/video/123456789`
• `/viewtiktok vt.tiktok.com/ABC123XYZ`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ⚡ *TÍNH NĂNG*             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🕒 *VĨNH VIỄN* - Không tự động dừng
• 🔄 *ĐA NHIỆM* - Nhiều task cùng lúc
• 🚫 *ẨN HOÀN TOÀN* - Không hiện output
• ⚡ *HIỆU SUẤT CAO* - Tối ưu tối đa

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🛠️ *LỆNH QUẢN LÝ*         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• `/stopview <task_id>` - Dừng task cụ thể
• `/stopviewall` - Dừng tất cả tasks
• `/viewstatus` - Trạng thái chi tiết
• `/listview` - Danh sách tất cả tasks
• `/viewhelp` - Hướng dẫn đầy đủ

*💡 Ghi chú:* Chạy cho đến khi bạn dùng lệnh dừng!
            """
            bot.reply_to(message, help_text, parse_mode='Markdown')
            return
        
        url = parts[1].strip()
        
        # Validate URL
        is_valid, result_msg = validate_tiktok_url(url)
        if not is_valid:
            bot.reply_to(message, result_msg)
            return
        
        if is_valid and result_msg.startswith("http"):
            url = result_msg
        
        # Tạo task ID mới
        VIEW_TASK_COUNTER += 1
        task_id = VIEW_TASK_COUNTER
        
        # Khởi tạo thông tin task
        VIEW_PROCESSES[task_id] = {
            'process': None,
            'target': url,
            'start_time': None,
            'chat_id': message.chat.id,
            'message_id': None,
            'pid': None,
            'status': 'initializing',
            'username': message.from_user.username or message.from_user.first_name
        }
        
        # Gửi thông báo bắt đầu với hiệu ứng đẹp
        msg = bot.reply_to(message, f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        🚀 *ĐANG KHỞI ĐỘNG TASK*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🆔 Task ID:* `{task_id}`
*👤 Người dùng:* {message.from_user.first_name}
*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📊 *THÔNG TIN*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎯 URL:* `{url}`
*⚡ Chế độ:* Vĩnh viễn
*🚫 Output:* Ẩn hoàn toàn

⏳ *Đang khởi tạo hệ thống...*
        """, parse_mode='Markdown')
        
        # Lưu message_id
        VIEW_PROCESSES[task_id]['message_id'] = msg.message_id
        
        # Chạy trong thread riêng
        def run_attack():
            success, result = run_viewtik_script(url, task_id)
            
            if success:
                elapsed = format_elapsed_time(VIEW_PROCESSES[task_id]['start_time'])
                time_running = get_time_difference(VIEW_PROCESSES[task_id]['start_time'])
                
                # Gửi thông báo thành công
                result_msg = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         ✅ *TASK KHỞI ĐỘNG THÀNH CÔNG* ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🆔 Task ID:* `{task_id}`
*👤 Người dùng:* {message.from_user.first_name}
*🕐 Bắt đầu:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📋 *THÔNG TIN CHI TIẾT*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎯 Target:* `{url}`
*⏱️ Đã chạy:* {time_running}
*📊 Status:* 🟢 ĐANG HOẠT ĐỘNG
*⚡ PID:* `{VIEW_PROCESSES[task_id].get('pid', 'N/A')}`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ⚠️ *THÔNG BÁO QUAN TRỌNG* ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• ✅ *Task đang chạy VĨNH VIỄN*
• 🚫 *Output được ẩn hoàn toàn*
• ⚡ *Hiệu suất tối ưu tối đa*
• 🛑 *Chỉ dừng khi có lệnh*

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔧 *LỆNH QUẢN LÝ*         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Dùng `/stopview {task_id}` để dừng khi cần
Dùng `/viewstatus` để kiểm tra trạng thái

*🎉 Chúc bạn có thật nhiều view!*
                """
                
                try:
                    bot.edit_message_text(
                        result_msg,
                        message.chat.id,
                        msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
            else:
                # Xóa task nếu thất bại
                if task_id in VIEW_PROCESSES:
                    del VIEW_PROCESSES[task_id]
                
                error_msg = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          ❌ *KHỞI ĐỘNG THẤT BẠI*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🆔 Task ID:* `{task_id}`
*👤 Người dùng:* {message.from_user.first_name}
*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚫 *THÔNG TIN LỖI*        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎯 URL:* `{url}`
*⚠️ Lỗi:* {result}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔧 *GIẢI PHÁP*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. Kiểm tra lại URL TikTok
2. Đảm bảo file viewtik.py tồn tại
3. Thử lại sau ít phút
4. Liên hệ quản trị viên nếu cần

*🔄 Vui lòng thử lại!*
                """
                
                try:
                    bot.edit_message_text(
                        error_msg,
                        message.chat.id,
                        msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
        
        # Chạy attack trong thread riêng
        attack_thread = threading.Thread(target=run_attack)
        attack_thread.daemon = True
        attack_thread.start()
    
    @bot.message_handler(commands=['stopview'])
    def handle_stopview(message):
        """Dừng một task cụ thể"""
        parts = message.text.split(' ', 1)
        
        if len(parts) < 2:
            # Hiển thị danh sách tasks nếu không có ID
            running_tasks = []
            for task_id, info in VIEW_PROCESSES.items():
                if info.get('status') == 'running':
                    elapsed = get_time_difference(info.get('start_time'))
                    running_tasks.append(f"• *Task {task_id}:* `{info.get('target', 'N/A')}` ({elapsed})")
            
            if running_tasks:
                tasks_list = "\n".join(running_tasks)
                bot.reply_to(message, f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          🛑 *DỪNG TASK VIEWTIKTOK*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*📋 TASKS ĐANG CHẠY:*
{tasks_list}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🛠️ *CÁCH DÙNG*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

`/stopview <task_id>`

*📌 Ví dụ:* `/stopview 1`

*💡 Ghi chú:* Nhập Task ID từ danh sách trên
                """, parse_mode='Markdown')
            else:
                bot.reply_to(message, 
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃         ℹ️ *KHÔNG CÓ TASK ĐANG CHẠY*   ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    "*Hiện tại không có task view TikTok nào đang hoạt động.*",
                    parse_mode='Markdown')
            return
        
        try:
            task_id = int(parts[1].strip())
        except ValueError:
            bot.reply_to(message, 
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃       ❌ *TASK ID KHÔNG HỢP LỆ*        ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "*Task ID phải là số nguyên.*\n"
                "*📌 Ví dụ:* `/stopview 1`",
                parse_mode='Markdown')
            return
        
        if task_id not in VIEW_PROCESSES:
            bot.reply_to(message, 
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃     ❌ *KHÔNG TÌM THẤY TASK {task_id}*  ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"*Task ID `{task_id}` không tồn tại hoặc đã bị dừng.*\n"
                f"*🔍 Dùng `/listview` để xem danh sách tasks.*",
                parse_mode='Markdown')
            return
        
        msg = bot.reply_to(message, 
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃       🛑 *ĐANG DỪNG TASK {task_id}*    ┃\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"*⏳ Vui lòng chờ trong giây lát...*",
            parse_mode='Markdown')
        
        stop_success = stop_viewtik_task(task_id)
        
        if stop_success:
            elapsed = get_time_difference(VIEW_PROCESSES.get(task_id, {}).get('start_time', 0))
            target = VIEW_PROCESSES.get(task_id, {}).get('target', 'N/A')
            
            bot.edit_message_text(
                f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       ✅ *TASK ĐÃ ĐƯỢC DỪNG THÀNH CÔNG*┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🆔 Task ID:* `{task_id}`
*👤 Người dừng:* {message.from_user.first_name}
*🕐 Kết thúc:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📊 *THÔNG TIN TASK*       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎯 Target:* `{target}`
*⏱️ Thời gian đã chạy:* {elapsed}
*📊 Status:* 🔴 ĐÃ DỪNG

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🎉 *THÔNG BÁO*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• ✅ *Process đã được dừng hoàn toàn*
• 🗑️ *Tài nguyên đã được giải phóng*
• 🔄 *Sẵn sàng cho task mới*

*🙏 Cảm ơn bạn đã sử dụng dịch vụ!*
                """,
                message.chat.id,
                msg.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      ❌ *KHÔNG THỂ DỪNG TASK {task_id}*┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🆔 Task ID:* `{task_id}`
*👤 Người dừng:* {message.from_user.first_name}
*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚫 *THÔNG TIN LỖI*        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*Task `{task_id}` không thể dừng được.*

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🔧 *GIẢI PHÁP*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. Kiểm tra xem task có tồn tại không
2. Thử dùng `/stopviewall` để dừng tất cả
3. Liên hệ quản trị viên nếu cần
                """,
                message.chat.id,
                msg.message_id,
                parse_mode='Markdown'
            )
    
    @bot.message_handler(commands=['stopviewall'])
    def handle_stopviewall(message):
        """Dừng tất cả tasks"""
        running_tasks = []
        for task_id, info in VIEW_PROCESSES.items():
            if info.get('status') == 'running':
                running_tasks.append(task_id)
        
        if not running_tasks:
            bot.reply_to(message, 
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃         ℹ️ *KHÔNG CÓ TASK ĐANG CHẠY*   ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "*Hiện tại không có task view TikTok nào đang hoạt động.*",
                parse_mode='Markdown')
            return
        
        msg = bot.reply_to(message, 
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃     🛑 *ĐANG DỪNG {len(running_tasks)} TASK(S)* ┃\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"*⏳ Vui lòng chờ trong giây lát...*",
            parse_mode='Markdown')
        
        stopped_count = 0
        for task_id in running_tasks:
            if stop_viewtik_task(task_id):
                stopped_count += 1
        
        bot.edit_message_text(
            f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       ✅ *ĐÃ DỪNG TẤT CẢ TASKS*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*👤 Người dừng:* {message.from_user.first_name}
*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📊 *KẾT QUẢ*              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*📈 Tổng số tasks:* {len(running_tasks)}
*✅ Đã dừng thành công:* {stopped_count}
*❌ Không thể dừng:* {len(running_tasks) - stopped_count}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🎉 *THÔNG BÁO*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🗑️ *Tất cả tài nguyên đã được giải phóng*
• 🔄 *Hệ thống sẵn sàng cho các task mới*
• 📊 *Không còn task nào đang chạy*

*🙏 Cảm ơn bạn đã sử dụng dịch vụ!*
                """,
            message.chat.id,
            msg.message_id,
            parse_mode='Markdown'
        )
    
    @bot.message_handler(commands=['viewstatus'])
    def handle_viewstatus(message):
        """Kiểm tra trạng thái tất cả tasks - CHI TIẾT"""
        
        active_tasks = []
        total_views = 0
        
        for task_id, info in VIEW_PROCESSES.items():
            if info.get('status') == 'running':
                elapsed = get_time_difference(info.get('start_time'))
                formatted_time = format_elapsed_time(info.get('start_time'))
                
                task_info = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           🟢 *TASK {task_id}*         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🎯 URL:* `{info.get('target', 'N/A')}`
*👤 User:* {info.get('username', 'N/A')}
*⏱️ Thời gian:* {elapsed}
*🕐 Chi tiết:* {formatted_time}
*🔢 PID:* `{info.get('pid', 'N/A')}`
*📅 Bắt đầu:* {datetime.fromtimestamp(info.get('start_time', 0)).strftime('%H:%M:%S %d/%m') if info.get('start_time') else 'N/A'}
                """.strip()
                active_tasks.append(task_info)
                total_views += 1
        
        # Tính thống kê
        total_tasks = len(VIEW_PROCESSES)
        running_tasks = len(active_tasks)
        stopped_tasks = total_tasks - running_tasks
        
        if active_tasks:
            tasks_text = "\n\n".join(active_tasks)
            status_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       📊 *TRẠNG THÁI HỆ THỐNG*       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📈 *THỐNG KÊ*             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🏃 Đang chạy:* {running_tasks} task(s)
*🛑 Đã dừng:* {stopped_tasks} task(s)
*📋 Tổng số:* {total_tasks} task(s)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🏃 *TASKS ĐANG CHẠY*      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{tasks_text}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ⚡ *THÔNG TIN HỆ THỐNG*   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🚀 *Chế độ:* VĨNH VIỄN
• 🔄 *Đa nhiệm:* Hỗ trợ nhiều task
• 🚫 *Output:* Ẩn hoàn toàn
• 🛠️ *Quản lý:* Dừng bằng lệnh

*🔍 Dùng `/listview` để xem tất cả tasks!*
            """
        else:
            status_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       📊 *TRẠNG THÁI HỆ THỐNG*       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📈 *THỐNG KÊ*             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🏃 Đang chạy:* 0 task(s)
*🛑 Đã dừng:* {total_tasks} task(s)
*📋 Tổng số:* {total_tasks} task(s)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ℹ️ *THÔNG BÁO*            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*Hiện tại không có task nào đang chạy!*

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚀 *BẮT ĐẦU TASK MỚI*     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Dùng lệnh: `/viewtiktok <url_tiktok>`

*📌 Ví dụ:* `/viewtiktok https://www.tiktok.com/@user/video/123456789`

*Hệ thống sẵn sàng hoạt động!* 🎬
            """
        
        bot.reply_to(message, status_text, parse_mode='Markdown')
    
    @bot.message_handler(commands=['listview'])
    def handle_listview(message):
        """Hiển thị danh sách chi tiết các tasks"""
        
        if not VIEW_PROCESSES:
            bot.reply_to(message, 
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃         📭 *DANH SÁCH TRỐNG*          ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "*Chưa có task nào được tạo.*\n"
                "*🚀 Dùng `/viewtiktok <url>` để bắt đầu!*",
                parse_mode='Markdown')
            return
        
        tasks_list = []
        running_count = 0
        stopped_count = 0
        
        for task_id, info in VIEW_PROCESSES.items():
            is_running = info.get('status') == 'running'
            pid = info.get('pid', 'N/A')
            
            if is_running:
                running_count += 1
                status = "🟢 ĐANG CHẠY"
                status_emoji = "⚡"
            else:
                stopped_count += 1
                status = "🔴 ĐÃ DỪNG"
                status_emoji = "⏹️"
            
            elapsed = get_time_difference(info.get('start_time'))
            start_time_str = datetime.fromtimestamp(info.get('start_time', 0)).strftime('%H:%M %d/%m') if info.get('start_time') else "N/A"
            
            tasks_list.append(f"""
{status_emoji} *TASK {task_id}:*
*🎯 URL:* `{info.get('target', 'N/A')}`
*📊 Status:* {status}
*⏱️ Thời gian:* {elapsed}
*🔢 PID:* `{pid}`
*👤 User:* {info.get('username', 'N/A')}
*📅 Bắt đầu:* {start_time_str}
            """.strip())
        
        all_tasks = "\n\n".join(tasks_list)
        
        list_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       📋 *DANH SÁCH TẤT CẢ TASKS*    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🕐 Thời gian:* {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📈 *THỐNG KÊ*             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*🟢 Đang chạy:* {running_count} task(s)
*🔴 Đã dừng:* {stopped_count} task(s)
*📊 Tổng số:* {len(VIEW_PROCESSES)} task(s)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📝 *CHI TIẾT TASKS*       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{all_tasks}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🛠️ *LỆNH QUẢN LÝ*         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*`/stopview <id>`* - Dừng task cụ thể
*`/stopviewall`* - Dừng tất cả tasks
*`/viewstatus`* - Trạng thái tasks đang chạy
*`/viewtiktok <url>`* - Tạo task mới

*💡 Dữ liệu được cập nhật theo thời gian thực*
        """
        
        bot.reply_to(message, list_text, parse_mode='Markdown')
    
    @bot.message_handler(commands=['viewhelp'])
    def handle_viewhelp(message):
        """Hướng dẫn đầy đủ"""
        help_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       🎬 *HƯỚNG DẪN SỬ DỤNG*         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*✨ TIKTOK VIEW BOT PRO - CHẠY VĨNH VIỄN*

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            🚀 *LỆNH CƠ BẢN*          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

*`/viewtiktok <url>`* - Bắt đầu view TikTok
*`/stopview <id>`* - Dừng task cụ thể
*`/stopviewall`* - Dừng tất cả tasks
*`/viewstatus`* - Trạng thái tasks đang chạy
*`/listview`* - Danh sách tất cả tasks
*`/viewhelp`* - Xem hướng dẫn này

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ⚡ *TÍNH NĂNG NỔI BẬT*     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• 🕒 *VĨNH VIỄN* - Không tự động dừng
• 🔄 *ĐA NHIỆM* - Nhiều task cùng lúc
• 🚫 *ẨN HOÀN TOÀN* - Không hiện output
• ⚡ *HIỆU SUẤT* - Tối ưu tối đa

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            📋 *ĐỊNH DẠNG URL*        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

• `https://www.tiktok.com/@user/video/123`
• `vt.tiktok.com/ABC123XYZ`
• `vm.tiktok.com/ABC123XYZ`
• `tiktok.com/@user/video/123`

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            ⚠️ *LƯU Ý QUAN TRỌNG*     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. Task chạy VĨNH VIỄN cho đến khi dừng
2. Có thể chạy nhiều task cùng lúc
3. Output được ẩn hoàn toàn
4. Dùng lệnh dừng khi không cần nữa
5. Hệ thống tự động dọn dẹp khi thoát

*🎉 Chúc bạn sử dụng hiệu quả!*
        """
        bot.reply_to(message, help_text, parse_mode='Markdown')
    
    # KHÔNG IN BẤT KỲ THÔNG BÁO NÀO TRÊN CONSOLE
    
except ImportError:
    pass
except Exception:
    pass