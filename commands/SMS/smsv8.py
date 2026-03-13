import sys
import subprocess
import os

def main():
    print("Chương trình spam SMS với các tùy chọn:")
    print("1. Chạy với tham số dòng lệnh")
    print("2. Chạy với GUI đơn giản")
    
    choice = input("Chọn (1-2): ").strip()
    
    if choice == "1":
        print("\nCách sử dụng:")
        print("python spm.py <số_điện_thoại> [tùy_chọn]")
        print("\nVí dụ:")
        print("  python spm.py 0918103224                 # Spam 1 lần")
        print("  python spm.py 0918103224 -c 10          # Spam 10 lần")
        print("  python spm.py 0918103224 -i             # Spam vô hạn")
        print("  python spm.py 0918103224 -p -pf proxy.txt  # Dùng proxy")
        print("  python spm.py 0918103224 -d 5           # Delay 5 giây")
        print("\nĐể xem tất cả tùy chọn:")
        print("  python spm.py --help")
        
        cmd = input("\nNhập lệnh: ").strip()
        os.system(f"python spm.py {cmd}")
    
    elif choice == "2":
        print("\nNhập thông tin spam:")
        phone = input("Số điện thoại: ").strip()
        infinite = input("Spam vô hạn? (y/n): ").lower() == 'y'
        count = 1
        delay = 2
        use_proxy = input("Dùng proxy? (y/n): ").lower() == 'y'
        proxy_file = ""
        
        if not infinite:
            count = int(input("Số lần spam: ").strip() or "1")
        
        delay = float(input("Delay (giây): ").strip() or "2")
        
        if use_proxy:
            proxy_file = input("File proxy (mặc định proxies.txt): ").strip() or "proxies.txt"
        
        cmd = [sys.executable, "spm.py", phone]
        
        if infinite:
            cmd.append("-i")
        else:
            cmd.extend(["-c", str(count)])
        
        cmd.extend(["-d", str(delay)])
        
        if use_proxy:
            cmd.append("-p")
            if proxy_file:
                cmd.extend(["-pf", proxy_file])
        
        print(f"\nĐang chạy lệnh: {' '.join(cmd)}")
        subprocess.run(cmd)

if __name__ == "__main__":
    main()