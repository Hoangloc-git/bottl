# commands/traippro.py
import requests
import socket
import json
import folium
from main import bot

API_KEY = "88e44d13c7d941709222cbdba2fc7d86"
API_URL = "https://ip-intelligence.abstractapi.com/v1/"

# ===========================
# TẠO BẢN ĐỒ HTML
# ===========================
def create_map(lat, lon, filename):
    html_map = f"{filename}.html"

    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], tooltip="IP Location").add_to(m)
    m.save(html_map)

    return html_map


# ===========================
# BLACKLIST CHECK
# ===========================
def check_blacklist(ip):
    try:
        url = f"https://blackbox.ipinfo.app/lookup/{ip}"
        res = requests.get(url, timeout=7).text.strip()

        if res == "Y":
            return True
        return False
    except:
        return "unknown"


# ===========================
# REVERSE DNS
# ===========================
def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Không có Reverse DNS"


# ===========================
# PORT SCAN (10 port cơ bản)
# ===========================
SCAN_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 8080]

def scan_ports(ip):
    result = []
    for port in SCAN_PORTS:
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((ip, port))
            result.append(f"{port}/OPEN")
        except:
            result.append(f"{port}/CLOSED")
        s.close()
    return result


# ===========================
# COMMAND /traippro
# ===========================
@bot.message_handler(commands=["traip"])
def tra_ip_pro(message):
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "⚠️ Sai cú pháp!\n"
            "Dùng: /traippro <ip>\n"
            "Ví dụ: /traip 8.8.8.8  , ip v6 khá chính xác , ip v4 có thể bị lệch"
        )
        return

    ip = args[1]

    try:
        # GỌI API ABSTRACT
        url = f"{API_URL}?api_key={API_KEY}&ip_address={ip}"
        res = requests.get(url, timeout=10)
        data = res.json()

        # ======= TRÍCH XUẤT DỮ LIỆU ========
        ip_addr = data.get("ip_address", "Không rõ")

        sec = data.get("security", {})
        asn = data.get("asn", {})
        comp = data.get("company", {})
        loc = data.get("location", {})
        tz = data.get("timezone", {})
        flag = data.get("flag", {})

        vpn = sec.get("is_vpn", False)
        proxy = sec.get("is_proxy", False)
        tor = sec.get("is_tor", False)
        abuse = sec.get("is_abuse", False)

        asn_name = asn.get("name", "Không rõ")
        asn_domain = asn.get("domain", "Không rõ")

        city = loc.get("city", "Không rõ")
        region = loc.get("region", "Không rõ")
        country = loc.get("country", "Không rõ")
        lat = loc.get("latitude", 0)
        lon = loc.get("longitude", 0)

        tz_name = tz.get("name", "Không rõ")
        flag_emoji = flag.get("emoji", "🏳")

        # ======= BLACKLIST CHECK ========
        blacklist = check_blacklist(ip)

        # ======= REVERSE DNS ========
        rDNS = reverse_dns(ip)

        # ======= PORT SCAN ========
        ports = scan_ports(ip)
        ports_text = "\n".join([f"• {x}" for x in ports])

        # ======= TẠO MAP HTML ========
        map_file = None
        if lat and lon:
            safe_ip = ip.replace(":", "_")
            map_file = create_map(lat, lon, f"map_{safe_ip}")

        # ======= SEND REPORT ========
        bot.send_message(
            message.chat.id,
            (
                f"🌐 <b>TRA IP PRO</b>\n\n"
                f"🔎 IP: <code>{ip_addr}</code>\n"
                f"Quốc gia: {country} {flag_emoji}\n"
                "-------------------------------------\n"
                f"🛡 <b>Bảo mật</b>\n"
                f"• VPN: {vpn}\n"
                f"• Proxy: {proxy}\n"
                f"• TOR: {tor}\n"
                f"• Abuse: {abuse}\n\n"
                f"🧅 <b>Reverse DNS:</b> {rDNS}\n"
                f"🚫 Blacklist: {blacklist}\n"
                "-------------------------------------\n"
                f"🏢 <b>ISP</b>\n"
                f"• Tên: {asn_name}\n"
                f"• Domain: {asn_domain}\n"
                "-------------------------------------\n"
                f"📍 <b>Vị trí</b>\n"
                f"• Thành phố: {city}\n"
                f"• Khu vực: {region}\n"
                f"• Quốc gia: {country}\n"
                f"• Lat/Lon: {lat}, {lon}\n"
                "-------------------------------------\n"
                f"⏰ <b>Múi giờ</b>\n"
                f"• {tz_name}\n"
                "-------------------------------------\n"
                f"🔌 <b>Port Scan</b>\n"
                f"{ports_text}\n"
            ),
            parse_mode="HTML"
        )

        # ======= GỬI FILE BẢN ĐỒ ========
        if map_file:
            bot.send_document(
                message.chat.id,
                open(map_file, "rb"),
                caption="🗺 Bản đồ vị trí IP (mở file HTML để xem)"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
