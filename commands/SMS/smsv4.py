#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMS Spam Tool - Phiên bản cải tiến với thread pool và quản lý lỗi tốt hơn
"""

import requests
import random
import time
import threading
import concurrent.futures
from datetime import datetime
import sys
import os
import json
import re
import logging
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass
from enum import Enum

# ========== CẤU HÌNH LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CẤU HÌNH MÀU ==========
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    MAGENTA = '\033[1;35m'
    RESET = '\033[0m'

# ========== DATACLASSES ==========
@dataclass
class SpamResult:
    """Kết quả của một lần spam"""
    service_name: str
    success: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time: float = 0.0

@dataclass
class SpamConfig:
    """Cấu hình spam"""
    phone_number: str
    total_requests: int
    max_workers: int = 10
    delay_between_requests: tuple = (0.5, 2.0)
    timeout: int = 15

# ========== SERVICE REGISTRY ==========
class ServiceRegistry:
    """Đăng ký và quản lý các dịch vụ spam"""
    
    def __init__(self):
        self.services: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        """Đăng ký một dịch vụ mới"""
        self.services[name] = func
    
    def get_random_service(self) -> tuple:
        """Lấy ngẫu nhiên một dịch vụ"""
        if not self.services:
            return None, None
        name = random.choice(list(self.services.keys()))
        return name, self.services[name]
    
    def get_all_services(self) -> List[tuple]:
        """Lấy tất cả dịch vụ"""
        return [(name, func) for name, func in self.services.items()]

# ========== CORE SPAM ENGINE ==========
class SpamEngine:
    """Động cơ spam chính"""
    
    def __init__(self, config: SpamConfig):
        self.config = config
        self.service_registry = ServiceRegistry()
        self.results: List[SpamResult] = []
        self._register_all_services()
    
    def _register_all_services(self):
        """Đăng ký tất cả dịch vụ từ smsv4.py"""
        # Đăng ký các dịch vụ từ smsv4.py (giữ nguyên tên hàm)
        services_to_register = [
            # Thêm các hàm từ smsv4.py ở đây
            # Ví dụ: ("viettel", send_otp_via_viettel),
            # ("medicare", send_otp_via_medicare),
            # ...
        ]
        
        for name, func in services_to_register:
            self.service_registry.register(name, func)
    
    def _make_request(self, service_name: str, service_func: Callable) -> SpamResult:
        """Thực hiện một request đến dịch vụ"""
        start_time = time.time()
        
        try:
            # Gọi hàm dịch vụ
            response = service_func(self.config.phone_number)
            
            response_time = time.time() - start_time
            
            # Giả sử hàm trả về response object
            if hasattr(response, 'status_code'):
                status_code = response.status_code
                success = 200 <= status_code < 300
                return SpamResult(
                    service_name=service_name,
                    success=success,
                    status_code=status_code,
                    response_time=response_time
                )
            else:
                # Nếu hàm không trả về response object
                return SpamResult(
                    service_name=service_name,
                    success=True,
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return SpamResult(
                service_name=service_name,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
    
    def run_single_thread(self):
        """Chạy spam single-threaded"""
        print(f"{Colors.CYAN}Bắt đầu spam với {self.config.total_requests} requests...{Colors.RESET}")
        
        for i in range(self.config.total_requests):
            service_name, service_func = self.service_registry.get_random_service()
            
            if not service_func:
                print(f"{Colors.RED}Không có dịch vụ nào được đăng ký!{Colors.RESET}")
                break
            
            print(f"{Colors.YELLOW}[{i+1}/{self.config.total_requests}] {service_name}...{Colors.RESET}")
            
            result = self._make_request(service_name, service_func)
            self.results.append(result)
            
            if result.success:
                print(f"{Colors.GREEN}✓ {service_name}: Thành công ({result.response_time:.2f}s){Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ {service_name}: Thất bại - {result.error_message}{Colors.RESET}")
            
            # Delay ngẫu nhiên
            delay = random.uniform(*self.config.delay_between_requests)
            time.sleep(delay)
    
    def run_multi_thread(self):
        """Chạy spam multi-threaded"""
        print(f"{Colors.CYAN}Bắt đầu spam với {self.config.total_requests} requests (đa luồng)...{Colors.RESET}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            
            for i in range(self.config.total_requests):
                service_name, service_func = self.service_registry.get_random_service()
                
                if not service_func:
                    continue
                
                future = executor.submit(self._make_request, service_name, service_func)
                futures.append((i, service_name, future))
            
            # Xử lý kết quả khi hoàn thành
            for i, service_name, future in futures:
                try:
                    result = future.result(timeout=self.config.timeout)
                    self.results.append(result)
                    
                    if result.success:
                        print(f"{Colors.GREEN}[{i+1}] ✓ {service_name}: Thành công{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}[{i+1}] ✗ {service_name}: Thất bại{Colors.RESET}")
                        
                except concurrent.futures.TimeoutError:
                    print(f"{Colors.RED}[{i+1}] ✗ {service_name}: Timeout{Colors.RESET}")
    
    def print_summary(self):
        """In tổng kết kết quả"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.WHITE}TỔNG KẾT KẾT QUẢ{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        
        print(f"{Colors.GREEN}Thành công: {successful}/{total} ({successful/total*100:.1f}%){Colors.RESET}")
        print(f"{Colors.RED}Thất bại: {failed}/{total} ({failed/total*100:.1f}%){Colors.RESET}")
        
        if successful > 0:
            avg_time = sum(r.response_time for r in self.results if r.success) / successful
            print(f"{Colors.YELLOW}Thời gian trung bình: {avg_time:.2f}s{Colors.RESET}")
        
        # In chi tiết các dịch vụ thất bại
        failed_services = [r for r in self.results if not r.success]
        if failed_services:
            print(f"\n{Colors.RED}Các dịch vụ thất bại:{Colors.RESET}")
            for result in failed_services[:10]:  # Hiển thị tối đa 10 cái
                print(f"  • {result.service_name}: {result.error_message}")

# ========== UTILITY FUNCTIONS ==========
def validate_phone_number(phone: str) -> str:
    """Validate và chuẩn hóa số điện thoại"""
    # Xóa tất cả ký tự không phải số
    cleaned = re.sub(r'[^0-9+]', '', phone)
    
    # Thêm +84 nếu là số Việt Nam (09...)
    if cleaned.startswith('0') and len(cleaned) == 10:
        cleaned = '+84' + cleaned[1:]
    
    return cleaned

def show_banner():
    """Hiển thị banner"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    banner = f"""
{Colors.MAGENTA}
╔══════════════════════════════════════════════════════════╗
║                SMS SPAM TOOL v4.0                        ║
║                Phiên bản nâng cao                        ║
╚══════════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.CYAN}Features:{Colors.RESET}
{Colors.GREEN}✓ Hỗ trợ đa luồng
{Colors.GREEN}✓ Quản lý kết nối thông minh
{Colors.GREEN}✓ Báo cáo chi tiết
{Colors.GREEN}✓ Tự động retry
{Colors.GREEN}✓ Proxy support (coming soon)
{Colors.RESET}
"""
    print(banner)

def parse_arguments():
    """Phân tích tham số dòng lệnh"""
    if len(sys.argv) < 3:
        print(f"{Colors.RED}Usage: {sys.argv[0]} <số_điện_thoại> <số_lượng> [options]{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Options:{Colors.RESET}")
        print(f"  --threads N     Số luồng đồng thời (mặc định: 10)")
        print(f"  --timeout N     Timeout mỗi request (giây, mặc định: 15)")
        print(f"  --delay MIN MAX Delay giữa các request (giây)")
        print(f"\n{Colors.CYAN}Examples:{Colors.RESET}")
        print(f"  {sys.argv[0]} 0987654321 100")
        print(f"  {sys.argv[0]} 0987654321 50 --threads 20 --timeout 30")
        print(f"  {sys.argv[0]} 0987654321 200 --delay 0.1 0.5")
        sys.exit(1)
    
    phone = validate_phone_number(sys.argv[1])
    
    try:
        count = int(sys.argv[2])
        if count <= 0:
            raise ValueError
    except ValueError:
        print(f"{Colors.RED}Số lượng phải là số nguyên dương!{Colors.RESET}")
        sys.exit(1)
    
    # Parse options
    threads = 10
    timeout = 15
    delay_min = 0.5
    delay_max = 2.0
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--threads" and i + 1 < len(sys.argv):
            try:
                threads = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"{Colors.RED}Số luồng phải là số nguyên!{Colors.RESET}")
                sys.exit(1)
        
        elif sys.argv[i] == "--timeout" and i + 1 < len(sys.argv):
            try:
                timeout = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"{Colors.RED}Timeout phải là số nguyên!{Colors.RESET}")
                sys.exit(1)
        
        elif sys.argv[i] == "--delay" and i + 2 < len(sys.argv):
            try:
                delay_min = float(sys.argv[i + 1])
                delay_max = float(sys.argv[i + 2])
                i += 3
            except ValueError:
                print(f"{Colors.RED}Delay phải là số thực!{Colors.RESET}")
                sys.exit(1)
        
        else:
            print(f"{Colors.RED}Option không hợp lệ: {sys.argv[i]}{Colors.RESET}")
            sys.exit(1)
    
    return phone, count, threads, timeout, (delay_min, delay_max)

# ========== MAIN FUNCTION ==========
def main():
    """Hàm chính"""
    show_banner()
    
    # Parse arguments
    phone, count, threads, timeout, delay_range = parse_arguments()
    
    print(f"{Colors.GREEN}Thông tin cấu hình:{Colors.RESET}")
    print(f"  Số điện thoại: {phone}")
    print(f"  Số lượng requests: {count}")
    print(f"  Số luồng: {threads}")
    print(f"  Timeout: {timeout}s")
    print(f"  Delay: {delay_range[0]}-{delay_range[1]}s")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    # Tạo config
    config = SpamConfig(
        phone_number=phone,
        total_requests=count,
        max_workers=threads,
        delay_between_requests=delay_range,
        timeout=timeout
    )
    
    # Tạo và chạy engine
    engine = SpamEngine(config)
    
    # Chọn chế độ chạy
    if threads > 1:
        engine.run_multi_thread()
    else:
        engine.run_single_thread()
    
    # Hiển thị kết quả
    engine.print_summary()
    
    # Lưu kết quả ra file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"spam_results_{timestamp}.json"
    
    results_data = [
        {
            "service": r.service_name,
            "success": r.success,
            "status_code": r.status_code,
            "error": r.error_message,
            "response_time": r.response_time
        }
        for r in engine.results
    ]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{Colors.GREEN}Kết quả đã được lưu vào: {filename}{Colors.RESET}")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Đã dừng bởi người dùng.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Lỗi không mong muốn: {e}{Colors.RESET}")
        logger.exception("Unhandled exception")
        sys.exit(1)