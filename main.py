import telebot
import os
import sys
import threading
import time
from time import sleep
import shutil
from flask import Flask, Response
from pystyle import Colors, Colorate
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import colorama
colorama.init()
from config import TOKEN

# ================== SETUP ==================
bot = telebot.TeleBot(TOKEN, threaded=True)
console = Console()
app = Flask(__name__)
PORT = 30466

# ================== BANNER ==================
banner = r"""
 ▄▄▄▄    ▒█████  ▄▄▄█████▓   ▄▄▄█████▓▓█████  ██▓    ▓█████   ▄████  ██▀███   ▄▄▄       ███▄ ▄███▓
▓█████▄ ▒██▒  ██▒▓  ██▒ ▓▒   ▓  ██▒ ▓▒▓█   ▀ ▓██▒    ▓█   ▀  ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓██▒▀█▀ ██▒
▒██▒ ▄██▒██░  ██▒▒ ▓██░ ▒░   ▒ ▓██░ ▒░▒███   ▒██░    ▒███   ▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▓██    ▓██░
▒██░█▀  ▒██   ██░░ ▓██▓ ░    ░ ▓██▓ ░ ▒▓█  ▄ ▒██░    ▒▓█  ▄ ░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██    ▒██ 
░▓█  ▀█▓░ ████▓▒░  ▒██▒ ░      ▒██▒ ░ ░▒████▒░██████▒░▒████▒░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒▒██▒   ░██▒
░▒▓███▀▒░ ▒░▒░▒░   ▒ ░░        ▒ ░░   ░░ ▒░ ░░ ▒░▓  ░░░ ▒░ ░ ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ░  ░
▒░▒   ░   ░ ▒ ▒░     ░           ░     ░ ░  ░░ ░ ▒  ░ ░ ░  ░  ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░░  ░      ░
 ░    ░ ░ ░ ░ ▒    ░           ░         ░     ░ ░      ░   ░ ░   ░   ░░   ░   ░   ▒   ░      ░   
 ░          ░ ░                          ░  ░    ░  ░   ░  ░      ░    ░           ░  ░       ░   
      ░                                                                                                                                                                                    
"""

# ================== HIỆU ỨNG ==================
def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Banner với gradient đẹp
    gradient_banner = Colorate.Horizontal(Colors.blue_to_purple, banner, 1)
    print(gradient_banner)
    
    # Tạo panel thông tin
    info_text = Text(
        "🤖 BOT TELEGRAM - SAKURA EDITION 🤖\n"
        "✨ Hoàng Lộc | Version 2.0 ✨\n"
        "🎯 Auto Load Commands | Web Dashboard 🎯",
        justify="center",
        style="bold cyan"
    )
    
    info_panel = Panel(
        info_text,
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(1, 2),
        title="[bold red]⚡ SYSTEM ONLINE ⚡[/bold red]",
        subtitle="[italic yellow]📡 Initializing...[/italic yellow]"
    )
    
    console.print(info_panel)
    print()

def sakura_effect():
    print(Colorate.Horizontal(Colors.blue_to_purple, "\n" + "━" * 60, 1))
    
    sakura_frames = [
        "🌸 Sakura System Initializing...",
        "🌸 Loading Core Modules...", 
        "🌸 Connecting to Telegram API..."
    ]
    
    for frame in sakura_frames:
        print(Colorate.Horizontal(Colors.purple_to_blue, f"  {frame}", 1))
        sleep(0.5)
    
    print(Colorate.Horizontal(Colors.blue_to_purple, "━" * 60, 1))

# ================== LOAD COMMANDS ĐƠN GIẢN ==================
def load_commands():
    print(Colorate.Horizontal(Colors.cyan_to_blue, "\n🔄 ĐANG LOAD MODULES...", 1))
    
    folder = "commands"
    
    # Kiểm tra thư mục
    if not os.path.exists(folder):
        print(Colorate.Horizontal(Colors.red_to_yellow, f"❌ Thư mục '{folder}' không tồn tại!", 1))
        os.makedirs(folder, exist_ok=True)
        print(Colorate.Horizontal(Colors.green_to_yellow, f"✅ Đã tạo thư mục '{folder}'", 1))
        return 0
    
    # Lấy danh sách file
    files = [f for f in os.listdir(folder) if f.endswith(".py") and f not in ["__init__.py"]]
    total_files = len(files)
    
    if total_files == 0:
        print(Colorate.Horizontal(Colors.yellow_to_red, "⚠️ Không tìm thấy file command nào!", 1))
        return 0
    
    loaded_count = 0
    
    # Hiệu ứng loading đơn giản
    print(Colorate.Horizontal(Colors.blue_to_cyan, f"📁 Đang xử lý {total_files} module(s)...", 1))
    sleep(0.5)
    
    for file in sorted(files):
        module_name = file[:-3]
        
        try:
            module_path = os.path.join(folder, file)
            
            with open(module_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Xử lý circular import
            if "from main import bot" in code:
                code = code.replace("from main import bot", "# bot object injected")
            
            # Tạo namespace và thực thi
            namespace = {
                'bot': bot, 
                'telebot': telebot, 
                'os': os,
                '__file__': module_path,
                '__name__': f'commands.{module_name}'
            }
            
            # Thêm các imports thông dụng
            try:
                import requests, json, random, datetime, time as ttime, re, sys as sysmod
                namespace.update({
                    'requests': requests,
                    'json': json,
                    'random': random,
                    'datetime': datetime,
                    'time': ttime,
                    're': re,
                    'sys': sysmod
                })
            except:
                pass
            
            exec(compile(code, module_path, 'exec'), namespace)
            loaded_count += 1
            
        except Exception:
            pass  # Bỏ qua lỗi
    
    # Hiển thị kết quả đơn giản
    print()
    print(Colorate.Horizontal(Colors.blue_to_purple, "━" * 50, 1))
    
    if loaded_count > 0:
        print(Colorate.Horizontal(
            Colors.green_to_cyan, 
            f"✅ ĐÃ LOAD THÀNH CÔNG {loaded_count}/{total_files} MODULES", 
            1
        ))
    else:
        print(Colorate.Horizontal(
            Colors.red_to_yellow, 
            f"⚠️ KHÔNG THỂ LOAD BẤT KỲ MODULE NÀO", 
            1
        ))
    
    print(Colorate.Horizontal(Colors.blue_to_purple, "━" * 50, 1))
    print()
    
    return loaded_count

# ================== WEB DASHBOARD ĐẸP ==================
@app.route("/")
def home():
    try:
        return Response(open("index.html", encoding="utf-8").read(), mimetype="text/html")
    except:
        # Fallback dashboard đẹp
        return '''
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🤖 Sakura Bot Dashboard</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    color: #fff;
                    font-family: 'Arial', sans-serif;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                
                .container {
                    width: 90%;
                    max-width: 800px;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                h1 {
                    background: linear-gradient(90deg, #ff0080, #ff8c00, #40e0d0);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 2.8em;
                    margin-bottom: 20px;
                }
                
                .status {
                    display: inline-block;
                    padding: 10px 30px;
                    background: linear-gradient(90deg, #00b09b, #96c93d);
                    border-radius: 50px;
                    font-weight: bold;
                    margin: 20px 0;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                .info {
                    background: rgba(255, 255, 255, 0.05);
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    text-align: left;
                }
                
                .info-item {
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .info-item:last-child {
                    border-bottom: none;
                }
                
                .terminal {
                    background: #000;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 30px;
                    font-family: monospace;
                    text-align: left;
                }
                
                .terminal-line {
                    color: #0f0;
                    margin-bottom: 5px;
                }
                
                .blink {
                    animation: blink 1s infinite;
                }
                
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0; }
                }
                
                .footer {
                    margin-top: 30px;
                    color: #888;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 SAKURA BOT DASHBOARD</h1>
                <div>Telegram Bot • Auto Load Commands • Real-time Monitoring</div>
                
                <div class="status">🟢 SYSTEM ONLINE</div>
                
                <div class="info">
                    <div class="info-item"><strong>Bot:</strong> Sakura Edition</div>
                    <div class="info-item"><strong>Author:</strong> Hoàng Lộc</div>
                    <div class="info-item"><strong>Port:</strong> ''' + str(PORT) + '''</div>
                    <div class="info-item"><strong>Status:</strong> Running</div>
                    <div class="info-item"><strong>Commands:</strong> Auto-loaded</div>
                </div>
                
                <div class="terminal">
                    <div class="terminal-line">$ system status check</div>
                    <div class="terminal-line">✅ Telegram Bot: <span style="color:#0f0">CONNECTED</span></div>
                    <div class="terminal-line">✅ Web Server: <span style="color:#0f0">RUNNING</span></div>
                    <div class="terminal-line">✅ Command Modules: <span style="color:#0f0">LOADED</span></div>
                    <div class="terminal-line">$ █<span class="blink">_</span></div>
                </div>
                
                <div class="footer">
                    © 2024 Sakura Bot Edition • Made with ❤️ by Hoàng Lộc
                </div>
            </div>
        </body>
        </html>
        '''

def run_web():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False, threaded=True)

# ================== HANDLERS MẶC ĐỊNH ==================
@bot.message_handler(commands=['ping', 'status'])
def ping_command(message):
    bot.reply_to(message, "🏓 Pong! Bot đang hoạt động ổn định!")

# ================== MAIN ==================
if __name__ == "__main__":
    # Hiển thị banner và hiệu ứng
    show_banner()
    sakura_effect()
    
    # Load commands (không thanh loading, không liệt kê)
    loaded_count = load_commands()
    
    # Thông báo bot bắt đầu
    print(Colorate.Horizontal(Colors.green_to_blue, "\n" + "═" * 60, 1))
    
    start_text = Text(
        f"🤖 BOT TELEGRAM ĐANG CHẠY\n"
        f"📱 Kết nối với Telegram API\n"
        f"🌐 Dashboard: http://0.0.0.0:{PORT}\n"
        f"⏰ {time.strftime('%H:%M:%S %d/%m/%Y')}",
        justify="center",
        style="bold cyan"
    )
    
    start_panel = Panel(
        start_text,
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2),
        title="[bold magenta]🚀 BOT ACTIVE 🚀[/bold magenta]"
    )
    console.print(start_panel)
    
    print(Colorate.Horizontal(Colors.green_to_blue, "═" * 60, 1))
    print()
    
    # Hiển thị hướng dẫn
    print(Colorate.Horizontal(Colors.cyan_to_blue, "💡 Nhấn Ctrl+C để dừng bot", 1))
    print()
    
    # Khởi động web trong background
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Chạy bot
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
    except KeyboardInterrupt:
        print("\n" + Colorate.Horizontal(Colors.red_to_yellow, "━" * 60, 1))
        
        stop_text = Text(
            "🛑 BOT ĐÃ DỪNG\n"
            "👋 Hẹn gặp lại!",
            justify="center",
            style="bold red"
        )
        
        stop_panel = Panel(
            stop_text,
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
            title="[bold white]🔴 SYSTEM OFFLINE 🔴[/bold white]"
        )
        console.print(stop_panel)
        
        print(Colorate.Horizontal(Colors.red_to_yellow, "━" * 60 + "\n", 1))
    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_purple, f"\n❌ Lỗi: {e}", 1))