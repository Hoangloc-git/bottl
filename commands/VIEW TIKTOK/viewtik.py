import random, requests, re, threading, time, secrets, os, sys
from hashlib import md5
from time import time as T

# ===============================
# 🔧 Random Device + Build System
# ===============================

def random_device():
    devices = [
        ("Pixel 6", "TQ3A.230805.001"),
        ("Pixel 7 Pro", "UPB1.230309.014"),
        ("Samsung Galaxy S21", "SP1A.210812.016"),
        ("Samsung Galaxy S23 Ultra", "TP1A.220624.014"),
        ("Oppo Reno 8", "CPH2359_11.C.21"),
        ("Oppo Find X5", "CPH2307_11.A.19"),
        ("Xiaomi Mi 11", "RKQ1.200710.003"),
        ("Xiaomi 13 Pro", "TKQ1.221114.001"),
        ("Vivo V27", "PD2269F_EX_A_13.0.11.2.W30"),
        ("OnePlus 11", "NE2213_11.C.47"),
        ("Realme GT Neo 5", "RMX3708_11.A.22"),
        ("Asus ROG Phone 7", "WW_33.0820.0810.241"),
        ("Huawei P50 Pro", "HUAWEIP50Pro-C00B125")
    ]
    os_versions = ["12", "13", "14"]
    device, build = random.choice(devices)
    os_version = random.choice(os_versions)
    os_api = random.randint(26, 34)
    return device, os_version, os_api, build

def build_user_agents():
    ua_templates = []
    for _ in range(15):
        device, os_version, _, build = random_device()
        ua = (f"com.ss.android.ugc.trill/400304 (Linux; U; Android {os_version}; vi_VN; "
              f"{device}; Build/{build}; Cronet/TTNetVersion:df66ad56)")
        ua_templates.append(ua)
    return ua_templates

ua_list = build_user_agents()

# ===============================
# 🔒 Tạo Signature cho request
# ===============================
class Signature:
    def __init__(self, params: str, data: str, cookies: str) -> None:
        self.params = params
        self.data = data
        self.cookies = cookies

    def hash(self, data: str) -> str:
        return str(md5(data.encode()).hexdigest())

    def calc_gorgon(self) -> str:
        g = self.hash(self.params)
        g += self.hash(self.data) if self.data else "0"*32
        g += self.hash(self.cookies) if self.cookies else "0"*32
        g += "0"*32
        return g

    def get_value(self):
        return self.encrypt(self.calc_gorgon())

    def encrypt(self, data: str):
        unix = int(T())
        length = 0x14
        key = [
            0xDF,0x77,0xB9,0x40,0xB9,0x9B,0x84,0x83,0xD1,0xB9,
            0xCB,0xD1,0xF7,0xC2,0xB9,0x85,0xC3,0xD0,0xFB,0xC3
        ]
        pl=[]
        for i in range(0,12,4):
            t = data[8*i:8*(i+1)]
            for j in range(4):
                pl.append(int(t[j*2:(j+1)*2],16))
        pl.extend([0x0,0x6,0xB,0x1C])
        H = int(hex(unix),16)
        pl+=[
            (H & 0xFF000000)>>24,
            (H & 0x00FF0000)>>16,
            (H & 0x0000FF00)>>8,
            (H & 0x000000FF)>>0,
        ]
        e = [a^b for a,b in zip(pl,key)]
        for i in range(length):
            C = self.reverse(e[i])
            D = e[(i+1)%length]
            F = self.rbit(C^D)
            H = ((F^0xFFFFFFFF)^length)&0xFF
            e[i]=H
        r="".join(self.hex_string(x) for x in e)
        return {"X-Gorgon":"840280416000"+r,"X-Khronos":str(unix)}

    def rbit(self,n):
        s=bin(n)[2:].zfill(8)
        return int(s[::-1],2)

    def hex_string(self,n):
        s=hex(n)[2:]
        return s if len(s)==2 else "0"+s

    def reverse(self,n):
        s=self.hex_string(n)
        return int(s[1:]+s[:1],16)

# ===============================
# 🚀 Main
# ===============================
os.system("cls" if os.name=="nt" else "clear")
print("""          
                        \x1b[1;37m╔╦╗ ╔═╗ \x1b[38;5;55m╔╗╔ ╦ ╦
                        \x1b[1;37m║║║ ║╣  \x1b[38;5;55m║║║ ║ ║ 
                        \x1b[1;37m╩ ╩ ╚═╝ \x1b[38;5;55m╝╚╝ ╚═╝
                  \x1b[1;37m-Best TOOL  \x1b[38;5;55m BUFF VIEW TIKTOK
             \x1b[1;37m╚═╦═══════════════\x1b[38;5;55m════════════════╦═╝       
          \x1b[1;37m╚╦═══╩═══════════════\x1b[38;5;55m════════════════╩═══╦╝
    \x1b[1;37m╚╦═══════╩═══════════════════\x1b[38;5;55m═══════════════════════╩═══════╦╝
     \x1b[1;37m║        -Welcome To     \x1b[38;5;55mMY TOOL                   ║
     \x1b[1;37m║             -Powerful L\x1b[38;5;55mSPEED MAX                 ║        
    \x1b[1;37m╔╩═╦═══════════════════════\x1b[38;5;55m═══════════════════════════╦═╩╗
       \x1b[1;37m║            -HOANGLOC \x1b[38;5;55m X VLXX.BZ              ║
      \x1b[1;37m╔╩═══════════════════════\x1b[38;5;55m═══════════════════════════╩╗
      \x1b[1;37m║  _Copyright © 2025 LOC\x1b[38;5;55m TOOL BUFF SPEED 10000_ ║
     \x1b[1;37m╔╩═══════════════════════\x1b[38;5;55m════════════════════════════╩╗
""")

# Kiểm tra argument
if len(sys.argv) < 2:
    print("\x1b[1;31m[-] Usage: python viewtik.py <URL_VIDEO>\x1b[0m")
    print("\x1b[1;33m[-] Example: python viewtik.py https://www.tiktok.com/@username/video/1234567890\x1b[0m")
    sys.exit(1)

link = sys.argv[1]

try:
    m=re.search(r'/(?:video|photo)/(\d+)',link)
    if m:
        video_id=m.group(1)
        print(f"[+] Video/Photo ID: {video_id}")
    else:
        page=requests.get(link,headers={'User-Agent':'Mozilla/5.0'},timeout=10).text
        m=re.search(r'"(video|photo)":\{"id":"(\d+)"',page)
        if m:
            video_id=m.group(2)
            print(f"[+] ID (từ HTML): {video_id}")
        else:
            print("[-] Không tìm thấy ID Video/Ảnh")
            exit(1)
except Exception as e:
    print(f"[-] Lỗi lấy ID: {e}")
    exit(1)

# ===============================
# 🧵 Gửi view thread
# ===============================
printed_flags={"banner":False,"success":False,"error":False}

def send_view():
    device_type, os_version, os_api, build=random_device()
    params=(
        f"channel=googleplay&aid=1233&app_name=musical_ly&version_code=400304&device_platform=android"
        f"&device_type={device_type.replace(' ','+')}&os_version={os_version}"
        f"&build={build}&device_id={random.randint(600000000000000,699999999999999)}"
        f"&os_api={os_api}&app_language=vi&tz_name=Asia%2FHo_Chi_Minh"
    )
    url=f"https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/?{params}"
    cookies={"sessionid":secrets.token_hex(8)}

    if not printed_flags["banner"]:
     print(f""" 
    ═══════════════════════════════════════════════════════════════════════════
                 \x1b[1;37m╔═╗╔╦╗╔╦╗╔═╗╔═╗\x1b[38;5;55m╦╔═  ╔═╗╔═╗╔╗╔╔╦╗                              
                 \x1b[1;37m╠═╣ ║  ║ ╠═╣║  \x1b[38;5;55m╠╩╗  ╚═╗║╣ ║║║ ║                               
                 \x1b[1;37m╩ ╩ ╩  ╩ ╩ ╩╚═╝\x1b[38;5;55m╩ ╩  ╚═╝╚═╝╝╚╝ ╩                               
         \x1b[1;37m╚═══════╦═══════════════\x1b[38;5;55m════════════════╦═══════╝                     
       \x1b[1;37m╔═══════════╩═══════════════\x1b[38;5;55m════════════════╩═══════════╗                     
                 \x1b[1;37mTarget× \x1b[38;5;55m[\x1b[1;37m{link}\x1b[38;5;55m]                      
                 \x1b[1;37mTime  × \x1b[38;5;55m[\x1b[1;37mTime : ∞\x1b[38;5;55m]                    
                 \x1b[1;37mID    × \x1b[38;5;55m[\x1b[1;37m{video_id}\x1b[38;5;55m]                 
                 \x1b[1;37mSpeed × \x1b[38;5;55m[\x1b[1;37mSPEED x1000\x1b[38;5;55m]                
                 \x1b[1;37mUser  × \x1b[38;5;55m[\x1b[1;37mSTART\x1b[38;5;55m]                      
                 \x1b[1;37mVip   × \x1b[38;5;55m[\x1b[1;37mTRUE\x1b[38;5;55m]                       
       \x1b[1;37m╚═══════════╦═══════════════\x1b[38;5;55m══════════════════╦═══════╝                   
         \x1b[1;37m╔═══════╩═══════════════\x1b[38;5;55m══════════════════╩═══════╗                     
                 \x1b[1;37mADMIN      × \x1b[38;5;55m[\x1b[1;37mHOANGLOC\x1b[38;5;55m]                
                 \x1b[1;37mNAME       × \x1b[38;5;55m[\x1b[1;37mHOANGLOC X Vlxx.bz\x1b[38;5;55m]      
         \x1b[1;37m╚═══════════════════════\x1b[38;5;55m══════════════════════════╝                     
    ═══════════════════════════════════════════════════════════════════════════          
    """)
    printed_flags["banner"]=True

    while True:
        data={"item_id":video_id,"play_delta":1,"action_time":int(time.time())}
        sig=Signature(params=params,data=str(data),cookies=str(cookies)).get_value()
        headers={
            "Host":"api16-core-c-alisg.tiktokv.com",
            "Connection":"keep-alive",
            "Accept-Encoding":"gzip",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent":random.choice(ua_list),
            "Sdk-Version":"2",
            "Passport-Sdk-Version":"19",
            "X-SS-DP":"1233",
            "X-Khronos":sig["X-Khronos"],
            "X-Gorgon":sig["X-Gorgon"],
        }

        try:
            r=requests.post(url,data=data,headers=headers,cookies=cookies,timeout=10)
            if "application/json" in r.headers.get("Content-Type",""):
                resp=r.json()
                if not printed_flags["success"]:
                   print(f"\x1b[38;5;55m 👤Tool by Hoang Loc | code={resp.get('status_code')}\x1b[0m")
                   printed_flags["success"]=True
        except Exception as e:
            if not printed_flags["error"]:
                print("\x1b[38;5;93m  TOOL STARTED🎶\x1b[0m")
                printed_flags["error"]=True

        time.sleep(random.uniform(0.3,1.2))

threads=[]
for i in range(1000):
    t=threading.Thread(target=send_view)
    t.daemon=True
    t.start()
    threads.append(t)

for t in threads:
    t.join()