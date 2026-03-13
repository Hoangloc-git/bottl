import subprocess
import threading
import os
import sys
import time
from telebot.types import Message
from main import bot

running_processes = []

@bot.message_handler(commands=['spmnglink'])
def video_gai(message: Message):
    global running_processes
    
    command_parts = message.text.split()
    
    if len(command_parts) < 4:
        bot.reply_to(message, "Sai rồi, dùng: /spmnglink <link|username> <threads> <message>\nVí dụ: /spmnglink https://ngl.link/username 50 Hello")
        return
    
    ngl_link = command_parts[1]
    
    try:
        threads = int(command_parts[2])
        if threads < 1 or threads > 500:
            bot.reply_to(message, "Threads 1-500 thôi")
            return
    except:
        bot.reply_to(message, "❌ Threads phải là số")
        return
    
    # Lấy message (có thể có khoảng trắng)
    message_text = " ".join(command_parts[3:])
    
    # Kiểm tra emoji option
    enable_emoji = "no"
    if message_text.endswith(" yes"):
        message_text = message_text[:-4].strip()
        enable_emoji = "yes"
    elif message_text.endswith(" no"):
        message_text = message_text[:-3].strip()
    
    if len(message_text) > 70:
        bot.reply_to(message, "❌ Message dài quá 70 ký tự")
        return
    
    bot.reply_to(message, f"🚀 Đang setup NGL spam cho {ngl_link}...")
    
    try:
        # Tạo file Python tạm thời để chạy
        script_content = f'''
import sys
import os
sys.path.append('/home/container/commands')

import requests
import random
import time
import threading
from urllib.parse import urlparse, urlencode
import json
from urllib.parse import quote

class SimpleNGL:
    def __init__(self, username, threads, question, enable_emoji):
        self.username = username
        self.threads = threads
        self.question = question
        self.enable_emoji = enable_emoji == "yes"
        self.success = 0
        self.running = True
        
    def _random_str(self, length=10):
        return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length))
    
    def send_message(self):
        try:
            icon = random.choice([" 😊", " 😎", " 😍"]) if self.enable_emoji else ""
            device_id = f"{{self._random_str(8)}}-{{self._random_str(4)}}-{{self._random_str(4)}}-{{self._random_str(4)}}-{{self._random_str(12)}}"
            
            headers = {{
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": f"https://ngl.link/{{self.username}}",
                "Origin": "https://ngl.link",
                "X-Requested-With": "XMLHttpRequest"
            }}
            
            data = {{
                "username": self.username,
                "question": self.question + icon,
                "deviceId": device_id,
                "gameSlug": "",
                "referrer": "",
            }}
            
            response = requests.post(
                "https://ngl.link/api/submit",
                headers=headers,
                data=urlencode(data),
                timeout=10
            )
            
            if response.status_code == 200:
                self.success += 1
                print(f"[SUCCESS] {{self.success}} messages sent to {{self.username}}")
            return True
        except Exception as e:
            print(f"[ERROR] {{e}}")
            return False
    
    def worker(self):
        while self.running and self.success < self.threads * 5:
            self.send_message()
            time.sleep(0.1)
    
    def run(self):
        print(f"Starting NGL spam to {{self.username}}")
        print(f"Threads: {{self.threads}}")
        print(f"Message: {{self.question}}")
        print(f"Emoji: {{'yes' if self.enable_emoji else 'no'}}")
        
        threads_list = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        try:
            while self.running and self.success < self.threads * 5:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.running = False
        for t in threads_list:
            t.join(timeout=1)
        
        print(f"COMPLETED: Sent {{self.success}} messages to {{self.username}}")

def convert_link(link):
    link = link.strip()
    if link.startswith("https://ngl.link/"):
        try:
            parsed = urlparse(link)
            username = parsed.path.lstrip('/')
            return username
        except:
            return link
    return link

# Lấy tham số
ngl_link = "{ngl_link}"
threads = {threads}
question = "{message_text}"
enable_emoji = "{enable_emoji}"

username = convert_link(ngl_link)
print(f"Target: {{username}}")

# Kiểm tra user
try:
    resp = requests.get(f"https://ngl.link/{{username}}", timeout=10)
    if "Could not find user" in resp.text:
        print("ERROR: User not found")
        sys.exit(1)
except:
    print("ERROR: Cannot check user")
    sys.exit(1)

# Chạy spam
ngl = SimpleNGL(username, threads, question, enable_emoji)
ngl.run()
'''
        
        # Tạo file tạm
        temp_file = "/tmp/ngl_spam.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # Chạy script
        cmd = [sys.executable, temp_file]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        running_processes.append(process)
        
        # Thread đọc output
        def read_output():
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    print(line)  # In ra console
                    output_lines.append(line)
                    
                    if "COMPLETED:" in line:
                        bot.send_message(message.chat.id, f"✅ {line}")
                        break
                    elif "ERROR:" in line:
                        bot.send_message(message.chat.id, f"❌ {line}")
                        break
            
            # Đọc lỗi nếu có
            stderr_output = process.stderr.read()
            if stderr_output:
                error_msg = stderr_output[:200]
                if error_msg and "ERROR" not in "\n".join(output_lines):
                    bot.send_message(message.chat.id, f"⚠️ Lỗi: {error_msg}")
        
        thread = threading.Thread(target=read_output)
        thread.daemon = True
        thread.start()
        
        bot.send_message(message.chat.id, f"🔥 Đang spam NGL đến {ngl_link}\n📝 Message: {message_text}\n⚡ Threads: {threads}\n🎯 Emoji: {enable_emoji}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi chạy: {str(e)}")

@bot.message_handler(commands=['stopngl'])
def stop_ngl(message: Message):
    global running_processes
    
    if not running_processes:
        bot.reply_to(message, "Không có NGL nào đang chạy")
        return
    
    stopped = 0
    for process in running_processes:
        try:
            process.terminate()
            stopped += 1
        except:
            pass
    
    running_processes.clear()
    bot.reply_to(message, f"✅ Đã dừng {stopped} NGL spam")