# commands/systeminfo.py
import os
import platform
import psutil
import time
import socket
import sys
from datetime import datetime
import subprocess
from telebot import types
from main import bot

@bot.message_handler(commands=['systeminfo', 'sysinfo', 'thongtinsystem'])
def system_info_command(message):
    """
    Lệnh hiển thị thông tin hệ thống bot
    """
    try:
        # Gửi action typing
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Hiệu ứng loading
        loading_icons = ["💻", "⚙️", "🔧", "🖥️", "📊", "💾", "🚀"]
        loading_msg = None
        start_time = time.time()
        
        def update_loading(stage):
            nonlocal loading_msg
            elapsed = time.time() - start_time
            icon = loading_icons[int(elapsed) % len(loading_icons)]
            
            loading_text = f"""
{icon} <b>ĐANG THU THẬP THÔNG TIN HỆ THỐNG</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Giai đoạn:</b> {stage}
⏳ <b>Thời gian:</b> {elapsed:.1f}s
🔄 <b>Trạng thái:</b> Đang xử lý...
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
        
        # Bước 1: Thông tin cơ bản
        update_loading("📡 Lấy thông tin hệ điều hành...")
        os_info = get_os_info()
        
        # Bước 2: Thông tin CPU
        update_loading("⚡ Phân tích CPU...")
        cpu_info = get_cpu_info()
        
        # Bước 3: Thông tin RAM
        update_loading("💾 Phân tích bộ nhớ...")
        memory_info = get_memory_info()
        
        # Bước 4: Thông tin ổ đĩa
        update_loading("💽 Phân tích ổ đĩa...")
        disk_info = get_disk_info()
        
        # Bước 5: Thông tin mạng
        update_loading("🌐 Phân tích mạng...")
        network_info = get_network_info()
        
        # Bước 6: Thông tin Python & Bot
        update_loading("🐍 Phân tích Python & Bot...")
        python_info = get_python_info()
        bot_info = get_bot_info()
        
        # Bước 7: Thông tin process
        update_loading("📈 Phân tích tiến trình...")
        process_info = get_process_info()
        
        # Xóa loading
        try:
            bot.delete_message(message.chat.id, loading_msg.message_id)
        except:
            pass
        
        # Tạo báo cáo hệ thống
        report = f"""
🏢 <b>THÔNG TIN HỆ THỐNG BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}
⏳ <b>Thời gian xử lý:</b> {time.time()-start_time:.2f} giây

🖥️ <b>HỆ ĐIỀU HÀNH:</b>
├ 🏷️ <b>Hệ thống:</b> {os_info['system']}
├ 📊 <b>Phiên bản:</b> {os_info['version']}
├ 🏗️ <b>Kiến trúc:</b> {os_info['architecture']}
├ 👤 <b>User:</b> {os_info['username']}
└ 🏠 <b>Hostname:</b> {os_info['hostname']}

⚡ <b>THÔNG TIN CPU:</b>
├ 🏷️ <b>CPU:</b> {cpu_info['name']}
├ 📊 <b>Số nhân:</b> {cpu_info['cores']} nhân ({cpu_info['threads']} luồng)
├ 📈 <b>Tần số:</b> {cpu_info['freq_current']} GHz (Max: {cpu_info['freq_max']} GHz)
├ 🔄 <b>Tải CPU:</b> {cpu_info['usage']}%
└ 🌡️ <b>Nhiệt độ:</b> {cpu_info['temp']}

💾 <b>THÔNG TIN BỘ NHỚ (RAM):</b>
├ 📊 <b>Tổng:</b> {memory_info['total']} GB
├ 🟢 <b>Đã dùng:</b> {memory_info['used']} GB ({memory_info['percent']}%)
├ 🟡 <b>Còn trống:</b> {memory_info['available']} GB
└ ⚡ <b>Swap:</b> {memory_info['swap']} GB ({memory_info['swap_percent']}% dùng)

💽 <b>THÔNG TIN Ổ ĐĨA:</b>
├ 📁 <b>Ổ hệ thống:</b> {disk_info['system']['total']} GB
├ 📊 <b>Đã dùng:</b> {disk_info['system']['used']} GB ({disk_info['system']['percent']}%)
├ 📈 <b>Còn trống:</b> {disk_info['system']['free']} GB
└ 🔄 <b>IO Read/Write:</b> {disk_info['io_read']} MB / {disk_info['io_write']} MB

🌐 <b>THÔNG TIN MẠNG:</b>
├ 📡 <b>Địa chỉ IP:</b> {network_info['ip']}
├ 🌍 <b>IPv6:</b> {network_info['ipv6']}
├ 🔌 <b>Kết nối mở:</b> {network_info['connections']}
├ 📊 <b>Bytes gửi:</b> {network_info['bytes_sent']}
└ 📥 <b>Bytes nhận:</b> {network_info['bytes_recv']}

🐍 <b>THÔNG TIN PYTHON & BOT:</b>
├ 🏷️ <b>Python:</b> {python_info['version']}
├ 📁 <b>Thư mục:</b> {python_info['cwd']}
├ 📊 <b>Uptime bot:</b> {bot_info['uptime']}
├ 👥 <b>Số command:</b> {bot_info['command_count']}
└ 📈 <b>Phiên bản bot:</b> {bot_info['version']}

📈 <b>THÔNG TIN TIẾN TRÌNH:</b>
├ ⚡ <b>PID:</b> {process_info['pid']}
├ 📊 <b>CPU tiến trình:</b> {process_info['cpu_percent']}%
├ 💾 <b>RAM tiến trình:</b> {process_info['memory_percent']}%
├ 🕒 <b>Thời gian chạy:</b> {process_info['create_time']}
└ 🔄 <b>Trạng thái:</b> {process_info['status']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>TỔNG QUAN HIỆU SUẤT:</b>
{get_performance_summary(cpu_info, memory_info, disk_info)}

🔔 <b>THÔNG BÁO HỆ THỐNG:</b>
{get_system_alerts(cpu_info, memory_info, disk_info)}

💡 <i>Thông tin cập nhật theo thời gian thực</i>
        """
        
        # Gửi báo cáo
        bot.reply_to(message, report, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi khi lấy thông tin hệ thống: {str(e)}")

# ========== CÁC HÀM HỖ TRỢ ==========

def get_os_info():
    """Lấy thông tin hệ điều hành"""
    try:
        return {
            'system': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'architecture': platform.machine(),
            'username': os.getlogin() if hasattr(os, 'getlogin') else 'N/A',
            'hostname': socket.gethostname()
        }
    except:
        return {
            'system': 'N/A',
            'version': 'N/A',
            'release': 'N/A',
            'architecture': 'N/A',
            'username': 'N/A',
            'hostname': 'N/A'
        }

def get_cpu_info():
    """Lấy thông tin CPU"""
    try:
        # Thông tin cơ bản
        cpu_freq = psutil.cpu_freq()
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        # Lấy tên CPU (chỉ hoạt động trên Linux)
        cpu_name = "Unknown"
        try:
            if platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            cpu_name = line.split(':')[1].strip()
                            break
            elif platform.system() == "Windows":
                cpu_name = platform.processor()
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                cpu_name = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
        except:
            cpu_name = platform.processor() or "Unknown"
        
        # Nhiệt độ CPU (chỉ hoạt động trên một số hệ thống)
        cpu_temp = "N/A"
        try:
            if platform.system() == "Linux":
                # Thử đọc nhiệt độ từ sysfs
                for sensor_file in ['/sys/class/thermal/thermal_zone0/temp', 
                                   '/sys/class/hwmon/hwmon0/temp1_input']:
                    if os.path.exists(sensor_file):
                        with open(sensor_file, 'r') as f:
                            temp = int(f.read().strip())
                            cpu_temp = f"{temp/1000:.1f}°C"
                            break
        except:
            pass
        
        return {
            'name': cpu_name,
            'cores': cpu_count_physical or "N/A",
            'threads': cpu_count_logical or "N/A",
            'freq_current': f"{cpu_freq.current/1000:.2f}" if cpu_freq else "N/A",
            'freq_max': f"{cpu_freq.max/1000:.2f}" if cpu_freq else "N/A",
            'usage': psutil.cpu_percent(interval=0.5),
            'temp': cpu_temp
        }
    except:
        return {
            'name': 'N/A',
            'cores': 'N/A',
            'threads': 'N/A',
            'freq_current': 'N/A',
            'freq_max': 'N/A',
            'usage': 'N/A',
            'temp': 'N/A'
        }

def get_memory_info():
    """Lấy thông tin bộ nhớ RAM"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        def bytes_to_gb(bytes_value):
            return f"{bytes_value / (1024**3):.2f}"
        
        return {
            'total': bytes_to_gb(mem.total),
            'available': bytes_to_gb(mem.available),
            'used': bytes_to_gb(mem.used),
            'percent': mem.percent,
            'swap': bytes_to_gb(swap.total),
            'swap_used': bytes_to_gb(swap.used),
            'swap_percent': swap.percent
        }
    except:
        return {
            'total': 'N/A',
            'available': 'N/A',
            'used': 'N/A',
            'percent': 'N/A',
            'swap': 'N/A',
            'swap_used': 'N/A',
            'swap_percent': 'N/A'
        }

def get_disk_info():
    """Lấy thông tin ổ đĩa"""
    try:
        # Thông tin ổ hệ thống
        disk = psutil.disk_usage('/')
        
        # Thông tin IO
        io_counters = psutil.disk_io_counters()
        
        def bytes_to_mb(bytes_value):
            return f"{bytes_value / (1024**2):.0f}" if bytes_value else "0"
        
        return {
            'system': {
                'total': f"{disk.total / (1024**3):.2f}",
                'used': f"{disk.used / (1024**3):.2f}",
                'free': f"{disk.free / (1024**3):.2f}",
                'percent': disk.percent
            },
            'io_read': bytes_to_mb(io_counters.read_bytes if io_counters else 0),
            'io_write': bytes_to_mb(io_counters.write_bytes if io_counters else 0)
        }
    except:
        return {
            'system': {
                'total': 'N/A',
                'used': 'N/A',
                'free': 'N/A',
                'percent': 'N/A'
            },
            'io_read': 'N/A',
            'io_write': 'N/A'
        }

def get_network_info():
    """Lấy thông tin mạng"""
    try:
        # Địa chỉ IP
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # Lấy IPv6 nếu có
        ipv6 = "Không hỗ trợ"
        try:
            ipv6_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
            if ipv6_info:
                ipv6 = ipv6_info[0][4][0]
        except:
            ipv6 = "N/A"
        
        # Kết nối mạng
        connections = len(psutil.net_connections())
        
        # Thông tin IO mạng
        net_io = psutil.net_io_counters()
        
        def bytes_to_mb(bytes_value):
            return f"{bytes_value / (1024**2):.1f}"
        
        return {
            'ip': ip_address,
            'ipv6': ipv6[:20] + "..." if len(ipv6) > 20 else ipv6,
            'connections': connections,
            'bytes_sent': f"{bytes_to_mb(net_io.bytes_sent)} MB",
            'bytes_recv': f"{bytes_to_mb(net_io.bytes_recv)} MB"
        }
    except:
        return {
            'ip': 'N/A',
            'ipv6': 'N/A',
            'connections': 'N/A',
            'bytes_sent': 'N/A',
            'bytes_recv': 'N/A'
        }

def get_python_info():
    """Lấy thông tin Python"""
    try:
        return {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'cwd': os.getcwd()
        }
    except:
        return {
            'version': 'N/A',
            'implementation': 'N/A',
            'cwd': 'N/A'
        }

def get_bot_info():
    """Lấy thông tin bot"""
    try:
        # Lấy thời gian uptime (giả sử lưu trong global)
        import time
        if 'bot_start_time' not in globals():
            globals()['bot_start_time'] = time.time()
        
        uptime_seconds = time.time() - globals()['bot_start_time']
        
        # Tính thời gian uptime
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s" if days > 0 else f"{hours}h {minutes}m {seconds}s"
        
        return {
            'uptime': uptime_str,
            'command_count': len(bot.message_handlers) if hasattr(bot, 'message_handlers') else 'N/A',
            'version': '1.0.0'
        }
    except:
        return {
            'uptime': 'N/A',
            'command_count': 'N/A',
            'version': 'N/A'
        }

def get_process_info():
    """Lấy thông tin tiến trình hiện tại"""
    try:
        process = psutil.Process()
        
        # Thời gian tạo tiến trình
        create_time = datetime.fromtimestamp(process.create_time()).strftime('%H:%M:%S %d/%m/%Y')
        
        return {
            'pid': process.pid,
            'name': process.name(),
            'cpu_percent': f"{process.cpu_percent(interval=0.1):.1f}",
            'memory_percent': f"{process.memory_percent():.2f}",
            'create_time': create_time,
            'status': process.status()
        }
    except:
        return {
            'pid': 'N/A',
            'name': 'N/A',
            'cpu_percent': 'N/A',
            'memory_percent': 'N/A',
            'create_time': 'N/A',
            'status': 'N/A'
        }

def get_performance_summary(cpu_info, memory_info, disk_info):
    """Tạo đánh giá hiệu suất tổng quan"""
    summary = []
    
    # Đánh giá CPU
    cpu_usage = float(cpu_info.get('usage', 0))
    if cpu_usage < 30:
        summary.append("⚡ <b>CPU:</b> Tải thấp, hoạt động tốt")
    elif cpu_usage < 70:
        summary.append("⚠️ <b>CPU:</b> Tải trung bình")
    else:
        summary.append("🔥 <b>CPU:</b> Tải cao, cần theo dõi")
    
    # Đánh giá RAM
    ram_percent = float(memory_info.get('percent', 0))
    if ram_percent < 60:
        summary.append("💾 <b>RAM:</b> Đủ dung lượng")
    elif ram_percent < 85:
        summary.append("⚠️ <b>RAM:</b> Sắp đầy")
    else:
        summary.append("🚨 <b>RAM:</b> Gần hết, cần giải phóng")
    
    # Đánh giá Disk
    disk_percent = float(disk_info['system'].get('percent', 0))
    if disk_percent < 70:
        summary.append("💽 <b>Disk:</b> Còn nhiều không gian")
    elif disk_percent < 90:
        summary.append("⚠️ <b>Disk:</b> Sắp đầy")
    else:
        summary.append("🚨 <b>Disk:</b> Sắp hết dung lượng")
    
    return '\n'.join(summary)

def get_system_alerts(cpu_info, memory_info, disk_info):
    """Tạo cảnh báo hệ thống"""
    alerts = []
    
    # Kiểm tra CPU
    cpu_usage = float(cpu_info.get('usage', 0))
    if cpu_usage > 90:
        alerts.append("🔥 <b>CPU:</b> Quá tải nghiêm trọng (>90%)")
    elif cpu_usage > 80:
        alerts.append("⚠️ <b>CPU:</b> Tải cao (>80%)")
    
    # Kiểm tra RAM
    ram_percent = float(memory_info.get('percent', 0))
    if ram_percent > 95:
        alerts.append("🚨 <b>RAM:</b> Sắp hết (>95%)")
    elif ram_percent > 85:
        alerts.append("⚠️ <b>RAM:</b> Sử dụng nhiều (>85%)")
    
    # Kiểm tra Disk
    disk_percent = float(disk_info['system'].get('percent', 0))
    if disk_percent > 95:
        alerts.append("🚨 <b>Disk:</b> Sắp hết dung lượng (>95%)")
    elif disk_percent > 90:
        alerts.append("⚠️ <b>Disk:</b> Sắp đầy (>90%)")
    
    if not alerts:
        alerts.append("✅ <b>Tất cả hệ thống đang hoạt động ổn định</b>")
    
    return '\n'.join(alerts)

# Thêm alias cho lệnh
@bot.message_handler(commands=['sys', 'serverinfo', 'info'])
def system_info_alias(message):
    system_info_command(message)