import requests
import json
from colorama import Fore, Style
from datetime import datetime, timedelta
from pytz import timezone
import requests
import time
import json
import sys
import random
import string
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from threading import BoundedSemaphore

# Đọc tham số từ dòng lệnh
if len(sys.argv) < 2:
    print("Vui lòng cung cấp số điện thoại và số lần gửi (tùy chọn)")
    print("Cú pháp: python spam.py <số_điện_thoại> [số_lần_gửi]")
    sys.exit(1)

# Lấy số điện thoại từ tham số đầu tiên
target_phone = sys.argv[1]

# Lấy số lần gửi từ tham số thứ hai (nếu có), mặc định là vô hạn
run_count = None
if len(sys.argv) >= 3:
    try:
        run_count = int(sys.argv[2])
    except ValueError:
        print(f"Lỗi: '{sys.argv[2]}' không phải là số hợp lệ!")
        sys.exit(1)

print(f"Bắt đầu gửi OTP đến số: {target_phone}")
if run_count:
    print(f"Số lần gửi: {run_count}")
else:
    print("Chế độ: Vô hạn (cho đến khi bị dừng thủ công)")

# Thêm một biến toàn cục để kiểm soát vòng lặp
running = True

# Hàm để dừng chương trình khi nhấn Ctrl+C
import signal
def signal_handler(sig, frame):
    global running
    print(f"\n{Fore.YELLOW}Nhận tín hiệu dừng. Đang hoàn thành các tác vụ hiện tại...{Style.RESET_ALL}")
    running = False
    sys.exit(0)

# Đăng ký handler cho Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

MAX_THREADS = 18
semaphore = BoundedSemaphore(MAX_THREADS)

# Danh sách các họ, tên đệm và tên phổ biến
last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Võ', 'Hoàng']
middle_names = ['Vân', 'Thị', 'Quang', 'Hoàng', 'Anh', 'Thanh']
first_names = ['Nam', 'Tuấn', 'Hương', 'Linh', 'Long', 'Duy']

# Tạo tên ngẫu nhiên
def generate_random_name():
    last_name = random.choice(last_names)
    middle_name = random.choice(middle_names) if random.choice([True, False]) else ''  # Optional middle name
    first_name = random.choice(first_names)
    return f"{last_name} {middle_name} {first_name}".strip()

def generate_random_id():
    def random_segment(length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    return f"{random_segment(2)}7D7{random_segment(1)}6{random_segment(1)}E-D52E-46EA-8861-ED{random_segment(1)}BB{random_segment(2)}86{random_segment(3)}"

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

def format_device_id(device_id):
    return f"{device_id[:8]}-{device_id[8:12]}-{device_id[12:16]}-{device_id[16:20]}-{device_id[20:]}"

random_id = generate_random_id()
formatted_device_id = format_device_id(random_id)

# Danh sách các hàm gửi OTP (giữ nguyên như cũ)
# ... (tất cả các hàm send_otp_via_* giữ nguyên) ...

# Hàm chạy tất cả các phương thức gửi OTP trong một thread
def send_all_otp_methods(sdt, iteration):
    with semaphore:
        print(f"{Fore.CYAN}[Lần {iteration}] Bắt đầu gửi OTP đến {sdt}{Style.RESET_ALL}")
        
        # Danh sách tất cả các hàm gửi OTP
        otp_functions = [
            send_otp_via_sapo,
            send_otp_via_viettel,
            send_otp_via_medicare,
            send_otp_via_tv360,
            send_otp_via_dienmayxanh,
            send_otp_via_kingfoodmart,
            send_otp_via_mocha,
            send_otp_via_fptdk,
            send_otp_via_fptmk,
            send_otp_via_VIEON,
            send_otp_via_ghn,
            send_otp_via_lottemart,
            send_otp_via_DONGCRE,
            send_otp_via_shopee,
            send_otp_via_TGDD,
            send_otp_via_fptshop,
            send_otp_via_WinMart,
            send_otp_via_vietloan,
            send_otp_via_lozi,
            send_otp_via_F88,
            send_otp_via_spacet,
            send_otp_via_vinpearl,
            send_otp_via_traveloka,
            send_otp_via_dongplus,
            send_otp_via_longchau,
            send_otp_via_longchau1,
            send_otp_via_galaxyplay,
            send_otp_via_emartmall,
            send_otp_via_ahamove,
            send_otp_via_ViettelMoney,
            send_otp_via_xanhsmsms,
            send_otp_via_xanhsmzalo,
            send_otp_via_popeyes,
            send_otp_via_ACHECKIN,
            send_otp_via_APPOTA,
            send_otp_via_Watsons,
            send_otp_via_hoangphuc,
            send_otp_via_fmcomvn,
            send_otp_via_Reebokvn,
            send_otp_via_thefaceshop,
            send_otp_via_BEAUTYBOX,
            send_otp_via_winmart,
            send_otp_via_medicare,
            send_otp_via_futabus,
            send_otp_via_ViettelPost,
            send_otp_via_myviettel2,
            send_otp_via_myviettel3,
            send_otp_via_TOKYOLIFE,
            send_otp_via_30shine,
            send_otp_via_Cathaylife,
            send_otp_via_dominos,
            send_otp_via_vinamilk,
            send_otp_via_vietloan2,
            send_otp_via_batdongsan,
            send_otp_via_GUMAC,
            send_otp_via_mutosi,
            send_otp_via_mutosi1,
            send_otp_via_vietair,
            send_otp_via_FAHASA,
            send_otp_via_hopiness,
            send_otp_via_modcha35,
            send_otp_via_Bibabo,
            send_otp_via_MOCA,
            send_otp_via_pantio,
            send_otp_via_Routine,
            send_otp_via_vayvnd
        ]
        
        # Thêm delay ngẫu nhiên giữa các request
        delays = [0.5, 0.7, 1.0, 1.2, 1.5]
        
        # Chạy tất cả các hàm
        for i, func in enumerate(otp_functions):
            if not running:  # Kiểm tra nếu cần dừng
                break
                
            try:
                print(f"{Fore.GREEN}[Lần {iteration}] Đang gửi qua {func.__name__[11:]}...{Style.RESET_ALL}")
                func(sdt)
                time.sleep(random.choice(delays))
            except Exception as e:
                print(f"{Fore.RED}[Lần {iteration}] Lỗi khi gửi qua {func.__name__[11:]}: {str(e)}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}[Lần {iteration}] Hoàn thành gửi OTP đến {sdt}{Style.RESET_ALL}")

# Hàm chính để chạy vô hạn
def main_loop():
    iteration = 1
    
    while running:
        if run_count and iteration > run_count:
            print(f"{Fore.YELLOW}Đã đạt số lần gửi tối đa ({run_count}). Dừng chương trình.{Style.RESET_ALL}")
            break
        
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Bắt đầu chu kỳ gửi OTP lần thứ {iteration}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        # Tạo thread cho mỗi lần gửi
        thread = threading.Thread(target=send_all_otp_methods, args=(target_phone, iteration))
        thread.start()
        
        # Chờ một khoảng thời gian giữa các chu kỳ
        cycle_delay = random.randint(30, 60)  # Delay 30-60 giây giữa các chu kỳ
        print(f"{Fore.YELLOW}Chờ {cycle_delay} giây trước chu kỳ tiếp theo...{Style.RESET_ALL}")
        
        # Đếm ngược với khả năng dừng
        for i in range(cycle_delay):
            if not running:
                break
            time.sleep(1)
            if i % 10 == 0 and i > 0:
                print(f"{Fore.YELLOW}Còn {cycle_delay - i} giây...{Style.RESET_ALL}")
        
        iteration += 1
    
    print(f"{Fore.GREEN}Chương trình đã dừng. Tổng số lần gửi: {iteration-1}{Style.RESET_ALL}")

# Chạy chương trình
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Chương trình bị dừng bởi người dùng.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Lỗi không mong muốn: {str(e)}{Style.RESET_ALL}")