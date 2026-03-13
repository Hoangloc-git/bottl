# commands/encode.py
import base64
import hashlib
import binascii
import time
from datetime import datetime
from telebot import types
from main import bot

# Bảng mã Morse
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', '0': '-----', ' ': '/',
    ',': '--..--', '.': '.-.-.-', '?': '..--..', '!': '-.-.--',
    "'": '.----.', '"': '.-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '/': '-..-.',
    '_': '..--.-', '=': '-...-', '+': '.-.-.', '-': '-....-',
    '$': '...-..-', '@': '.--.-.'
}

@bot.message_handler(commands=['encode'])
def encode_main_command(message):
    """
    Lệnh mã hóa chính: /encode <method> <text>
    Nếu không có tham số thì hiện hướng dẫn
    """
    try:
        # Tách các phần của lệnh
        text = message.text.strip()
        
        if text == '/encode' or len(text.split()) == 1:
            # Hiển thị hướng dẫn nếu không có tham số
            show_encode_help(message)
            return
        
        parts = text.split(" ", 2)
        
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Thiếu tham số!\n\nSử dụng: <code>/encode &lt;phương pháp&gt; &lt;text&gt;</code>\n\nGõ <code>/encode</code> để xem tất cả phương pháp", parse_mode="HTML")
            return
        
        method = parts[1].lower()
        input_text = parts[2]
        
        # Gửi action typing
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Hiệu ứng loading
        loading_msg = bot.reply_to(message, f"🔐 Đang mã hóa với {method.upper()}...")
        
        # Xử lý mã hóa theo phương pháp
        result = process_encoding(method, input_text)
        
        if result is None:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            show_encode_help(message)
            return
        
        # Tạo kết quả đẹp
        response = create_encode_result(method, input_text, result)
        
        # Xóa loading và gửi kết quả
        bot.delete_message(message.chat.id, loading_msg.message_id)
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

def show_encode_help(message):
    """Hiển thị hướng dẫn sử dụng lệnh encode"""
    help_text = """
🔐 <b>LỆNH MÃ HÓA /encode</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 <b>Cú pháp:</b> <code>/encode &lt;phương pháp&gt; &lt;text&gt;</code>

🔢 <b>PHƯƠNG PHÁP MÃ HÓA:</b>

<b>📊 Base64:</b>
<code>/encode base64 Hello World</code>
→ Mã hóa/giải mã Base64

<b>🔢 Binary:</b>
<code>/encode binary Hello</code>
→ Chuyển sang mã nhị phân

<b>📡 Morse:</b>
<code>/encode morse SOS</code>
→ Mã hóa Morse code

<b>🔐 Hash Functions:</b>
<code>/encode md5 password</code>
<code>/encode sha1 secret</code>
<code>/encode sha256 data</code>
→ Tạo hash MD5, SHA1, SHA256

<b>🎨 Hexadecimal:</b>
<code>/encode hex text</code>
→ Mã hóa Hex

<b>🌀 ROT13:</b>
<code>/encode rot13 hello</code>
→ Mã hóa ROT13

<b>🔄 Reverse:</b>
<code>/encode reverse hello</code>
→ Đảo ngược chuỗi

<b>🔡 Caesar:</b>
<code>/encode caesar5 hello</code>
→ Mã hóa Caesar với shift=5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔓 <b>GIẢI MÃ:</b>
<code>/decode &lt;phương pháp&gt; &lt;text&gt;</code>

💡 <b>Ví dụ:</b>
<code>/encode base64 Hello World</code>
<code>/decode base64 SGVsbG8gV29ybGQ=</code>
<code>/encode morse SOS</code>
    """
    
    # Tạo inline keyboard với các phương pháp nhanh
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    buttons = [
        types.InlineKeyboardButton("Base64", callback_data="encode_help_base64"),
        types.InlineKeyboardButton("Binary", callback_data="encode_help_binary"),
        types.InlineKeyboardButton("Morse", callback_data="encode_help_morse"),
        types.InlineKeyboardButton("MD5", callback_data="encode_help_md5"),
        types.InlineKeyboardButton("SHA256", callback_data="encode_help_sha256"),
        types.InlineKeyboardButton("Hex", callback_data="encode_help_hex"),
    ]
    
    markup.add(*buttons)
    
    bot.reply_to(message, help_text, parse_mode="HTML", reply_markup=markup)

def process_encoding(method, text):
    """Xử lý mã hóa theo phương pháp"""
    try:
        if method == 'base64':
            return base64_encode(text)
            
        elif method == 'binary':
            return text_to_binary(text)
            
        elif method == 'morse':
            return text_to_morse(text)
            
        elif method == 'md5':
            return hash_md5(text)
            
        elif method == 'sha1':
            return hash_sha1(text)
            
        elif method == 'sha256':
            return hash_sha256(text)
            
        elif method == 'hex':
            return text_to_hex(text)
            
        elif method == 'rot13':
            return rot13_encode(text)
            
        elif method == 'reverse':
            return text[::-1]
            
        elif method.startswith('caesar'):
            # /encode caesar5 text
            try:
                shift = int(method.replace('caesar', ''))
                return caesar_cipher(text, shift)
            except:
                return caesar_cipher(text, 3)  # Mặc định shift=3
                
        elif method == 'url':
            return url_encode(text)
            
        elif method == 'ascii':
            return text_to_ascii(text)
            
        else:
            return None
            
    except Exception:
        return None

def create_encode_result(method, original_text, encoded_text):
    """Tạo định dạng kết quả đẹp"""
    method_names = {
        'base64': 'Base64 Encode',
        'binary': 'Binary Encode',
        'morse': 'Morse Code',
        'md5': 'MD5 Hash',
        'sha1': 'SHA1 Hash',
        'sha256': 'SHA256 Hash',
        'hex': 'Hexadecimal',
        'rot13': 'ROT13 Cipher',
        'reverse': 'Reverse Text',
        'url': 'URL Encode',
        'ascii': 'ASCII Codes',
        'caesar': 'Caesar Cipher'
    }
    
    method_display = method_names.get(method, method.upper())
    
    # Kiểm tra nếu là mã hóa caesar
    if method.startswith('caesar'):
        shift = method.replace('caesar', '')
        method_display = f"Caesar Cipher (Shift={shift if shift else 3})"
    
    # Rút gọn text nếu quá dài
    original_display = original_text
    if len(original_text) > 50:
        original_display = original_text[:47] + "..."
    
    encoded_display = encoded_text
    if len(encoded_text) > 100:
        encoded_display = encoded_text[:97] + "..."
    
    result = f"""
🔐 <b>KẾT QUẢ MÃ HÓA</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Phương pháp:</b> {method_display}
⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S')}

📝 <b>Văn bản gốc:</b>
<code>{original_display}</code>

🔒 <b>Kết quả mã hóa:</b>
<code>{encoded_display}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 <b>Thống kê:</b>
├ 🔤 Độ dài gốc: {len(original_text)} ký tự
├ 🔢 Độ dài mã hóa: {len(encoded_text)} ký tự
└ 🔄 Tỉ lệ: {len(encoded_text)/len(original_text):.2f}x

💡 <b>Để giải mã:</b>
<code>/decode {method} {encoded_text[:30] if len(encoded_text) > 30 else encoded_text}</code>
    """
    
    return result

# ========== CÁC HÀM MÃ HÓA ==========

def base64_encode(text):
    """Mã hóa Base64"""
    try:
        # Thử giải mã trước để xem có phải base64 không
        try:
            decoded = base64.b64decode(text).decode('utf-8')
            # Nếu giải mã được, thì đây là base64, trả về decoded
            return f"⚠️ Đây là Base64 encoded, giải mã ra: {decoded}"
        except:
            # Không giải mã được, mã hóa nó
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return encoded
    except:
        return "Lỗi khi mã hóa Base64"

def text_to_binary(text):
    """Chuyển text sang binary"""
    try:
        binary = ' '.join(format(ord(char), '08b') for char in text)
        return binary
    except:
        return "Lỗi khi chuyển sang binary"

def text_to_morse(text):
    """Chuyển text sang mã Morse"""
    try:
        morse = []
        for char in text.upper():
            if char in MORSE_CODE_DICT:
                morse.append(MORSE_CODE_DICT[char])
            else:
                morse.append('?')  # Ký tự không xác định
        return ' '.join(morse)
    except:
        return "Lỗi khi chuyển sang Morse"

def hash_md5(text):
    """Tạo MD5 hash"""
    try:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    except:
        return "Lỗi khi tạo MD5 hash"

def hash_sha1(text):
    """Tạo SHA1 hash"""
    try:
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    except:
        return "Lỗi khi tạo SHA1 hash"

def hash_sha256(text):
    """Tạo SHA256 hash"""
    try:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    except:
        return "Lỗi khi tạo SHA256 hash"

def text_to_hex(text):
    """Chuyển text sang hex"""
    try:
        return text.encode('utf-8').hex()
    except:
        return "Lỗi khi chuyển sang hex"

def rot13_encode(text):
    """Mã hóa ROT13"""
    try:
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    except:
        return "Lỗi khi mã hóa ROT13"

def caesar_cipher(text, shift=3):
    """Mã hóa Caesar cipher"""
    try:
        result = []
        for char in text:
            if char.isalpha():
                shift_base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - shift_base + shift) % 26 + shift_base))
            else:
                result.append(char)
        return ''.join(result)
    except:
        return "Lỗi khi mã hóa Caesar"

def url_encode(text):
    """Mã hóa URL"""
    try:
        import urllib.parse
        return urllib.parse.quote(text)
    except:
        return "Lỗi khi mã hóa URL"

def text_to_ascii(text):
    """Chuyển text sang mã ASCII"""
    try:
        ascii_codes = ' '.join(str(ord(char)) for char in text)
        return ascii_codes
    except:
        return "Lỗi khi chuyển sang ASCII"

# ========== LỆNH GIẢI MÃ ==========

@bot.message_handler(commands=['decode', 'decrypt'])
def decode_command(message):
    """Lệnh giải mã"""
    try:
        text = message.text.strip()
        
        if text == '/decode' or len(text.split()) == 1:
            bot.reply_to(message, "🔓 <b>LỆNH GIẢI MÃ</b>\n\n<code>/decode &lt;phương pháp&gt; &lt;text&gt;</code>\n\nPhương pháp: base64, binary, morse, rot13, caesar\n\nVí dụ: <code>/decode base64 SGVsbG8=</code>", parse_mode="HTML")
            return
        
        parts = text.split(" ", 2)
        
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Thiếu tham số!\n\nSử dụng: <code>/decode &lt;phương pháp&gt; &lt;text&gt;</code>", parse_mode="HTML")
            return
        
        method = parts[1].lower()
        input_text = parts[2]
        
        bot.send_chat_action(message.chat.id, 'typing')
        loading_msg = bot.reply_to(message, f"🔓 Đang giải mã {method.upper()}...")
        
        result = process_decoding(method, input_text)
        
        if result is None:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.reply_to(message, f"⚠️ Không thể giải mã với phương pháp {method}!\n\nCác phương pháp hỗ trợ: base64, binary, morse, rot13, caesar")
            return
        
        response = f"""
🔓 <b>KẾT QUẢ GIẢI MÃ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Phương pháp:</b> {method.upper()}
⏰ <b>Thời gian:</b> {datetime.now().strftime('%H:%M:%S')}

🔒 <b>Văn bản mã hóa:</b>
<code>{input_text[:50]}{'...' if len(input_text) > 50 else ''}</code>

📝 <b>Kết quả giải mã:</b>
<code>{result}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Giải mã thành công!</b>
        """
        
        bot.delete_message(message.chat.id, loading_msg.message_id)
        bot.reply_to(message, response, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

def process_decoding(method, text):
    """Xử lý giải mã"""
    try:
        if method == 'base64':
            try:
                return base64.b64decode(text).decode('utf-8')
            except:
                return "Không thể giải mã Base64 (có thể không phải base64 hợp lệ)"
                
        elif method == 'binary':
            try:
                # Xóa khoảng trắng và chuyển từ binary sang text
                binary_chunks = text.split()
                chars = []
                for chunk in binary_chunks:
                    if len(chunk) == 8:  # 8-bit binary
                        chars.append(chr(int(chunk, 2)))
                    else:
                        # Thử xử lý không có khoảng trắng
                        if len(text) % 8 == 0:
                            result = ''
                            for i in range(0, len(text), 8):
                                result += chr(int(text[i:i+8], 2))
                            return result
                return ''.join(chars)
            except:
                return "Không thể giải mã Binary"
                
        elif method == 'morse':
            try:
                # Đảo ngược bảng morse
                reverse_morse = {v: k for k, v in MORSE_CODE_DICT.items()}
                words = text.split(' / ')
                decoded_words = []
                for word in words:
                    letters = word.split()
                    decoded_letters = []
                    for letter in letters:
                        if letter in reverse_morse:
                            decoded_letters.append(reverse_morse[letter])
                        else:
                            decoded_letters.append('?')
                    decoded_words.append(''.join(decoded_letters))
                return ' '.join(decoded_words)
            except:
                return "Không thể giải mã Morse"
                
        elif method == 'rot13':
            # ROT13 encode/decode giống nhau
            return rot13_encode(text)
            
        elif method.startswith('caesar'):
            try:
                shift = int(method.replace('caesar', '')) if method != 'caesar' else 3
                # Giải mã caesar = mã hóa với shift ngược lại
                return caesar_cipher(text, -shift)
            except:
                # Thử tất cả các shift từ 1-25
                results = []
                for shift in range(1, 26):
                    results.append(f"Shift {shift:2d}: {caesar_cipher(text, -shift)}")
                return "Có thể là Caesar cipher, thử các shift:\n" + '\n'.join(results)
                
        else:
            return None
            
    except Exception:
        return None

# ========== CALLBACK HANDLER ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith('encode_help_'))
def encode_help_callback(call):
    """Xử lý callback cho help buttons"""
    method = call.data.replace('encode_help_', '')
    
    examples = {
        'base64': {
            'encode': '/encode base64 Hello World',
            'decode': '/decode base64 SGVsbG8gV29ybGQ=',
            'desc': 'Mã hóa/giải mã Base64 - chuẩn mã hóa binary thành ASCII'
        },
        'binary': {
            'encode': '/encode binary Hello',
            'decode': '/decode binary 01001000 01100101 01101100 01101100 01101111',
            'desc': 'Chuyển text sang mã nhị phân 8-bit và ngược lại'
        },
        'morse': {
            'encode': '/encode morse SOS',
            'decode': '/decode morse ... --- ...',
            'desc': 'Mã hóa Morse code (chỉ hỗ trợ chữ cái, số, dấu câu cơ bản)'
        },
        'md5': {
            'encode': '/encode md5 password123',
            'decode': 'Không thể giải mã (one-way hash)',
            'desc': 'Tạo MD5 hash 128-bit (không thể giải mã ngược)'
        },
        'sha256': {
            'encode': '/encode sha256 secret data',
            'decode': 'Không thể giải mã (one-way hash)',
            'desc': 'Tạo SHA-256 hash 256-bit (không thể giải mã ngược)'
        },
        'hex': {
            'encode': '/encode hex Hello',
            'decode': '/decode hex 48656c6c6f',
            'desc': 'Chuyển text sang mã Hexadecimal (cơ số 16)'
        }
    }
    
    if method in examples:
        example = examples[method]
        response = f"""
🔐 <b>PHƯƠNG PHÁP: {method.upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━
📝 <b>Mô tả:</b> {example['desc']}

💡 <b>Ví dụ mã hóa:</b>
<code>{example['encode']}</code>

{'🔓' if 'decode' in example and 'Không' not in example['decode'] else '🚫'} <b>Ví dụ giải mã:</b>
<code>{example['decode']}</code>

━━━━━━━━━━━━━━━━━━━━━━
📌 <b>Lưu ý:</b>
• Một số phương pháp không thể giải mã ngược (hash functions)
• Binary cần đúng định dạng 8-bit với khoảng trắng
• Morse phân biệt khoảng trắng giữa các từ
        """
        
        bot.answer_callback_query(call.id, f"Hiển thị ví dụ {method}")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, "Phương pháp không tồn tại")