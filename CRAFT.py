import telebot
import os
import requests
import json
import re
import time
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running..."
    
# Bot Token
BOT_TOKEN = "8897824915:AAFTyektgm4lze_n87WU3QI5rtaNb4RklmA"
bot = telebot.TeleBot(BOT_TOKEN)

# API Endpoint
API_URL = "https://flw-api-free-fire-max.vercel.app/follow"
UNFOLLOW_API_URL = "https://flw-api-free-fire-max.vercel.app/unfollow"


# Store user data
user_data = {}

# ============== MAIN REPLY KEYBOARD ==============
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.row("🔴 TOKEN ADD", "🔴 FOLLOW SEND")
    keyboard.row("🔴 UNFOLLOW SEND", "🔴 TOKEN CHK")
    keyboard.row("🔴 DELETE ALL", "🔴 MY ACCOUNTS")
    keyboard.row("🔴 HELP", "🔴 ABOUT")
    return keyboard
    

# ============== REGION REPLY KEYBOARD ==============
def region_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("🇮🇳 𝙄𝙉𝘿", "🇧🇩 𝘽𝘿", "🇵🇰 𝙋𝙆")
    keyboard.row("🇸🇬 𝙎𝙂", "🇪🇺 𝙀𝙐", "🇺🇸 𝙐𝙎")
    keyboard.row("🇮🇩 𝙄𝘿", "🇹🇭 𝙏𝙃", "🇻🇳 𝙑𝙉")
    keyboard.row("🔙 𝘽𝘼𝘾𝙆")
    return keyboard

# ============== FOLLOW REGION KEYBOARD ==============
def follow_region_keyboard(regions):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row = []
    for r in regions:
        row.append(f"🌍 {r}")
        if len(row) == 2:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)
    keyboard.row("🔙 𝘽𝘼𝘾𝙆")
    return keyboard

# ============== FOLLOW COUNT KEYBOARD ==============
def follow_count_keyboard(max_count):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row = []
    if max_count >= 5:
        row.append("5️⃣ 5")
    if max_count >= 10:
        row.append("🔟 10")
    if max_count >= 25:
        row.append("2️⃣5️⃣ 25")
    if max_count >= 50:
        row.append("5️⃣0️⃣ 50")
    if max_count >= 100:
        row.append("1️⃣0️⃣0️⃣ 100")
    if max_count >= 250:
        row.append("2️⃣5️⃣0️⃣ 250")
    if max_count >= 500:
        row.append("5️⃣0️⃣0️⃣ 500")
    if row:
        keyboard.row(*row)
    keyboard.row("📤 𝙎𝙀𝙉𝘿 𝘼𝙇𝙇", "🔙 𝘽𝘼𝘾𝙆")
    return keyboard

# ============== HELPER FUNCTIONS ==============
def chunk_array(arr, size):
    for i in range(0, len(arr), size):
        yield arr[i:i + size]

def parse_accounts(content):
    accounts = []
    try:
        # Try JSON
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                if "uid" in item and "password" in item:
                    accounts.append({"uid": str(item["uid"]), "password": str(item["password"])})
    except:
        # Try TXT
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r'[:|,]\s*', line)
            if len(parts) >= 2:
                accounts.append({"uid": parts[0].strip(), "password": parts[1].strip()})
    return accounts

# ============== START COMMAND ==============
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {"state": None}
    
    welcome = f"""✨ *╔═══╗╔═══╗╔═══╗╔═══╗*
✨ *║╔═╗║║╔═╗║║╔═╗║║╔═╗║*
✨ *║╚═╝║║╚═╝║║╚═╝║║╚═╝║*
✨ *║╔╗╔╝║╔╗╔╝║╔╗╔╝║╔╗╔╝*
✨ *║║║╚╗║║║╚╗║║║╚╗║║║╚╗*
✨ *╚╝╚═╝╚╝╚═╝╚╝╚═╝╚╝╚═╝*

🌟 *𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙁𝙁 𝙈𝘼𝙓 𝙁𝙊𝙇𝙇𝙊𝙒 𝘽𝙊𝙏* 🌟

⚡ *𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎:*
┌─────────────────────┐
│ ✅ Add Multiple Accounts     │
│ ✅ Bulk Follow Send          │
│ ✅ Account Status Check      │
│ ✅ Multi-Thread Support      │
│ ✅ Live Progress Update      │
│ ✅ Delete All Accounts       │
│ ✅ View My Accounts          │
└─────────────────────┘

⚠️ *𝙎𝙀𝙇𝙀𝘾𝙏 𝘼𝙉 𝙊𝙋𝙏𝙄𝙊𝙉 𝘽𝙀𝙇𝙊𝙒*"""
    
    bot.reply_to(message, welcome, parse_mode='Markdown', reply_markup=main_keyboard())

# ============== HANDLE MAIN MENU BUTTONS ==============
@bot.message_handler(func=lambda message: message.text == "🔴 𝙏𝙊𝙆𝙀𝙉 𝘼𝘿𝘿")
def token_add(message):
    user_id = message.chat.id
    user_data[user_id]["state"] = "token_add"
    
    msg = """📥 *𝙎𝙀𝙇𝙀𝘾𝙏 𝙔𝙊𝙐𝙍 𝙍𝙀𝙂𝙄𝙊𝙉*

┌─────────────────┐
│ 🌏 Choose Region│
│ 📍 For Accounts │
└─────────────────┘"""
    
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=region_keyboard())

@bot.message_handler(func=lambda message: message.text == "🔴 𝙁𝙊𝙇𝙇𝙊𝙒 𝙎𝙀𝙉𝘿")
def follow_send(message):
    user_id = message.chat.id
    
    if user_id not in user_data or "accounts" not in user_data[user_id]:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*\n\n⚠️ Please add accounts first using:\n🔴 𝙏𝙊𝙆𝙀𝙉 𝘼𝘿𝘿", 
                    parse_mode='Markdown', reply_markup=main_keyboard())
        return
    
    regions = list(user_data[user_id]["accounts"].keys())
    if not regions:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*", parse_mode='Markdown')
        return
    
    user_data[user_id]["state"] = "follow_send"
    
    region_list = ""
    for r in regions:
        count = len(user_data[user_id]["accounts"][r])
        region_list += f"│ 🌍 {r.ljust(8)} : {str(count).rjust(3)} Accounts │\n"
    
    msg = f"""📤 *𝙁𝙊𝙇𝙇𝙊𝙒 𝙎𝙀𝙉𝘿 𝙎𝙀𝙏𝙐𝙋*

┌─────────────────────┐
{region_list}└─────────────────────┘

📝 *𝙎𝙀𝙉𝘿 𝙏𝘼𝙍𝙂𝙀𝙏 𝙐𝙄𝘿:*"""
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("🔙 𝘽𝘼𝘾𝙆")
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🔴 𝙏𝙊𝙆𝙀𝙉 𝘾𝙃𝙆")
def token_chk(message):
    user_id = message.chat.id
    
    if user_id not in user_data or "accounts" not in user_data[user_id]:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*\n\n⚠️ Please add accounts first using:\n🔴 𝙏𝙊𝙆𝙀𝙉 𝘼𝘿𝘿", 
                    parse_mode='Markdown', reply_markup=main_keyboard())
        return
    
    data = user_data[user_id]["accounts"]
    msg = "📊 *𝘼𝘾𝘾𝙊𝙐𝙉𝙏 𝙎𝙐𝙈𝙈𝘼𝙍𝙔*\n\n┌─────────────────────┐\n"
    total = 0
    for region, accounts in data.items():
        msg += f"│ 🌍 {region.ljust(8)} : {str(len(accounts)).rjust(3)} Accounts │\n"
        total += len(accounts)
    msg += f"├─────────────────────┤\n"
    msg += f"│ 📈 𝙏𝙊𝙏𝘼𝙇      : {str(total).rjust(3)} Accounts │\n"
    msg += "└─────────────────────┘"
    
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())

# ============== NEW BUTTON: DELETE ALL ==============
@bot.message_handler(func=lambda message: message.text == "🔴 𝘿𝙀𝙇𝙀𝙏𝙀 𝘼𝙇𝙇")
def delete_all(message):
    user_id = message.chat.id
    
    if user_id not in user_data or "accounts" not in user_data[user_id]:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙏𝙊 𝘿𝙀𝙇𝙀𝙏𝙀!*", parse_mode='Markdown')
        return
    
    # Ask for confirmation
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("✅ 𝙔𝙀𝙎 𝘿𝙀𝙇𝙀𝙏𝙀", "❌ 𝙉𝙊")
    bot.reply_to(message, "⚠️ *𝘼𝙍𝙀 𝙔𝙊𝙐 𝙎𝙐𝙍𝙀?*\n\nThis will delete ALL your saved accounts!", 
                parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "✅ 𝙔𝙀𝙎 𝘿𝙀𝙇𝙀𝙏𝙀")
def confirm_delete(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id]["accounts"] = {}
        user_data[user_id]["state"] = None
        bot.reply_to(message, "🗑️ *𝙊𝙇𝙇 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝘿𝙀𝙇𝙀𝙏𝙀𝘿!*", 
                    parse_mode='Markdown', reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "❌ 𝙉𝙊")
def cancel_delete(message):
    bot.reply_to(message, "✅ *𝘿𝙀𝙇𝙀𝙏𝙀 𝘾𝘼𝙉𝘾𝙀𝙇𝙇𝙀𝘿!*", 
                parse_mode='Markdown', reply_markup=main_keyboard())

# ============== NEW BUTTON: MY ACCOUNTS ==============
@bot.message_handler(func=lambda message: message.text == "🔴 𝙈𝙔 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎")
def my_accounts(message):
    user_id = message.chat.id
    
    if user_id not in user_data or "accounts" not in user_data[user_id]:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*", parse_mode='Markdown')
        return
    
    data = user_data[user_id]["accounts"]
    total = 0
    for region, accounts in data.items():
        total += len(accounts)
    
    # Send first 20 accounts
    msg = f"📋 *𝙈𝙔 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎*\n\n"
    msg += f"┌─────────────────────┐\n"
    count = 0
    for region, accounts in data.items():
        msg += f"│ 🌍 {region.ljust(8)} : {str(len(accounts)).rjust(3)} Accounts │\n"
        for acc in accounts[:10]:  # Show first 10
            count += 1
            if count <= 20:  # Max 20 accounts show
                msg += f"│    ├ UID: {acc['uid'][:12].ljust(12)} │\n"
    msg += f"├─────────────────────┤\n"
    msg += f"│ 📈 𝙏𝙊𝙏𝘼𝙇      : {str(total).rjust(3)} Accounts │\n"
    msg += "└─────────────────────┘"
    
    if total > 20:
        msg += f"\n\n⚠️ Showing first 20 accounts out of {total}"
    
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())

# ============== NEW BUTTON: HELP ==============
@bot.message_handler(func=lambda message: message.text == "🔴 𝙃𝙀𝙇𝙋")
def help_command(message):
    help_text = """📖 *𝙃𝙀𝙇𝙋 𝙂𝙐𝙄𝘿𝙀*

┌─────────────────────────────┐
│ 📌 *HOW TO USE THIS BOT*     │
├─────────────────────────────┤
│                              │
│ 🔴 *TOKEN ADD*               │
│ → Add accounts by region     │
│ → Upload JSON/TXT file       │
│ → Auto validate accounts     │
│                              │
│ 🔴 *FOLLOW SEND*             │
│ → Enter target UID           │
│ → Select region              │
│ → Choose follow count        │
│ → Auto send followers        │
│                              │
│ 🔴 *TOKEN CHK*               │
│ → View all your accounts     │
│ → Region wise summary        │
│                              │
│ 🔴 *MY ACCOUNTS*             │
│ → View saved accounts list   │
│                              │
│ 🔴 *DELETE ALL*              │
│ → Delete all saved accounts  │
│                              │
│ 🔴 *ABOUT*                   │
│ → Bot information            │
└─────────────────────────────┘

📄 *SUPPORTED FILE FORMATS:*
JSON: [{"uid":"123","password":"pass"}]
TXT: uid:password (one per line)

⚡ *THREADING:*
• Check: 10 threads
• Follow: 5 threads"""
    
    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============== NEW BUTTON: ABOUT ==============
@bot.message_handler(func=lambda message: message.text == "🔴 𝘼𝘽𝙊𝙐𝙏")
def about_command(message):
    about_text = """🤖 *𝘼𝘽𝙊𝙐𝙏 𝙏𝙃𝙄𝙎 𝘽𝙊𝙏*

┌─────────────────────────────┐
│                              │
│ 🔥 *FF MAX FOLLOW BOT*      │
│                              │
│ 📌 Version: 2.0.0           │
│ 📌 Language: Python         │
│ 📌 Library: PyTelegramBotAPI│
│ 📌 API: FF MAX API          │
│                              │
│ ⚡ *FEATURES*               │
│ • Multi-Thread Support      │
│ • Live Progress Update      │
│ • Auto Account Validation   │
│ • Bulk Follow Sending       │
│ • Region Selection          │
│ • File Upload Support       │
│                              │
│ 👨‍💻 *DEVELOPER*             │
│ • Telegram: @YourUsername   │
│ • GitHub: YourGitHub        │
│                              │
│ ⚠️ *WARNING*                │
│ Use at your own risk!       │
└─────────────────────────────┘"""
    
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============== HANDLE REGION SELECTION ==============
@bot.message_handler(func=lambda message: message.text in ["🇮🇳 𝙄𝙉𝘿", "🇧🇩 𝘽𝘿", "🇵🇰 𝙋𝙆", "🇸🇬 𝙎𝙂", "🇪🇺 𝙀𝙐", "🇺🇸 𝙐𝙎", "🇮🇩 𝙄𝘿", "🇹🇭 𝙏𝙃", "🇻🇳 𝙑𝙉"])
def region_selected(message):
    user_id = message.chat.id
    
    region_map = {
        "🇮🇳 𝙄𝙉𝘿": "IND",
        "🇧🇩 𝘽𝘿": "BD",
        "🇵🇰 𝙋𝙆": "PK",
        "🇸🇬 𝙎𝙂": "SG",
        "🇪🇺 𝙀𝙐": "EU",
        "🇺🇸 𝙐𝙎": "US",
        "🇮🇩 𝙄𝘿": "ID",
        "🇹🇭 𝙏𝙃": "TH",
        "🇻🇳 𝙑𝙉": "VN"
    }
    
    region = region_map[message.text]
    user_data[user_id]["region"] = region
    user_data[user_id]["state"] = "waiting_file"
    
    msg = f"""📤 *𝙐𝙋𝙇𝙊𝘼𝘿 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎*

┌─────────────────────┐
│ 🌍 Region : {region.ljust(12)} │
└─────────────────────┘

📄 *𝙎𝙐𝙋𝙋𝙊𝙍𝙏𝙀𝘿 𝙁𝙊𝙍𝙈𝘼𝙏𝙎:*
├ JSON: [{{"uid":"123","password":"pass"}}]
├ TXT: uid:password (one per line)
└ TXT: uid|password (one per line)

 𝗡𝗢𝗧𝗘 : 𝗪𝗔𝗛𝗜 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦 𝗔𝗗𝗗 𝗛𝗢𝗡𝗚𝗘 𝗝𝗜𝗦 𝗜𝗗 𝗦𝗘 3 𝗗𝗜𝗙𝗥𝗘𝗡𝗧 𝗖𝗥𝗔𝗙𝗧𝗟𝗔𝗡𝗗 𝗠𝗔𝗣𝗦 𝗞𝗛𝗘𝗟𝗔 𝗛𝗨𝗔 𝗛𝗢

📎 *𝙎𝙀𝙉𝘿 𝙁𝙄𝙇𝙀 𝘼𝙎 𝘿𝙊𝘾𝙐𝙈𝙀𝙉𝙏 𝙊𝙍 𝙏𝙀𝙓𝙏*"""
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("🔙 𝘽𝘼𝘾𝙆")
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=keyboard)

# ============== HANDLE BACK BUTTON ==============
@bot.message_handler(func=lambda message: message.text == "🔙 𝘽𝘼𝘾𝙆")
def back_button(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id]["state"] = None
    bot.reply_to(message, "🔙 *𝘽𝘼𝘾𝙆 𝙏𝙊 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐*", 
                parse_mode='Markdown', reply_markup=main_keyboard())

# ============== HANDLE FILE UPLOAD ==============
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id].get("state") != "waiting_file":
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        file_content = bot.download_file(file_info.file_path).decode('utf-8')
        process_accounts(message, file_content)
    except Exception as e:
        bot.reply_to(message, f"❌ *𝙀𝙍𝙍𝙊𝙍 𝙍𝙀𝘼𝘿𝙄𝙉𝙂 𝙁𝙄𝙇𝙀!*\n\n⚠️ {str(e)}", parse_mode='Markdown')

# ============== HANDLE TEXT FOR ACCOUNTS ==============
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    
    if user_id not in user_data:
        return
    
    state = user_data[user_id].get("state")
    
    # Handle file upload via text
    if state == "waiting_file" and message.text != "🔙 𝘽𝘼𝘾𝙆":
        process_accounts(message, message.text)
        return
    
    # Handle target UID
    if state == "follow_send" and message.text != "🔙 𝘽𝘼𝘾𝙆":
        target_uid = message.text.strip()
        if not target_uid.isdigit():
            bot.reply_to(message, "❌ *𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙐𝙄𝘿!*\n\n⚠️ Please send a numeric UID.", parse_mode='Markdown')
            return
        
        user_data[user_id]["target"] = target_uid
        user_data[user_id]["state"] = "waiting_follow_region"
        
        regions = list(user_data[user_id]["accounts"].keys())
        msg = f"🎯 *𝙏𝘼𝙍𝙂𝙀𝙏 𝙐𝙄𝘿:* {target_uid}\n\n📥 *𝙎𝙀𝙇𝙀𝘾𝙏 𝙍𝙀𝙂𝙄𝙊𝙉:*"
        bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=follow_region_keyboard(regions))
        return
    
    # Handle follow region
    if state == "waiting_follow_region":
        if message.text == "🔙 𝘽𝘼𝘾𝙆":
            user_data[user_id]["state"] = None
            bot.reply_to(message, "🔙 *𝘽𝘼𝘾𝙆 𝙏𝙊 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐*", parse_mode='Markdown', reply_markup=main_keyboard())
            return
        
        region = message.text.replace("🌍 ", "").strip()
        if region not in user_data[user_id]["accounts"]:
            bot.reply_to(message, f"❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿 𝙁𝙊𝙍 {region}!*", parse_mode='Markdown')
            return
        
        user_data[user_id]["follow_region"] = region
        user_data[user_id]["state"] = "waiting_count"
        
        accounts = user_data[user_id]["accounts"][region]
        msg = f"""📤 *𝙁𝙊𝙇𝙇𝙊𝙒 𝙎𝙀𝙏𝙐𝙋*

┌─────────────────────┐
│ 🌍 Region  : {region.ljust(12)} │
│ 👤 Target  : {user_data[user_id]['target'].ljust(12)} │
│ 📊 Accounts: {str(len(accounts)).rjust(3)} Available │
└─────────────────────┘

📝 *𝙎𝙀𝙇𝙀𝘾𝙏 𝙁𝙊𝙇𝙇𝙊𝙒 𝘾𝙊𝙐𝙉𝙏:*"""
        
        bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=follow_count_keyboard(len(accounts)))
        return
    
    # Handle follow count
    if state == "waiting_count":
        if message.text == "🔙 𝘽𝘼𝘾𝙆":
            user_data[user_id]["state"] = None
            bot.reply_to(message, "🔙 *𝘽𝘼𝘾𝙆 𝙏𝙊 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐*", parse_mode='Markdown', reply_markup=main_keyboard())
            return
        
        if message.text == "📤 𝙎𝙀𝙉𝘿 𝘼𝙇𝙇":
            region = user_data[user_id]["follow_region"]
            count = len(user_data[user_id]["accounts"][region])
        else:
            match = re.search(r'(\d+)', message.text)
            if not match:
                bot.reply_to(message, "❌ *𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙉𝙐𝙈𝘽𝙀𝙍!*\n\n⚠️ Please select from keyboard or send a number.", parse_mode='Markdown')
                return
            count = int(match.group(0))
        
        process_follow_request(message, count)

# ============== PROCESS ACCOUNTS ==============
def process_accounts(message, content):
    user_id = message.chat.id
    region = user_data[user_id]["region"]
    
    accounts = parse_accounts(content)
    
    if not accounts:
        bot.reply_to(message, "❌ *𝙉𝙊 𝙑𝘼𝙇𝙄𝘿 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝙁𝙊𝙐𝙉𝘿!*\n\n⚠️ Please check file format.", parse_mode='Markdown')
        return
    
    status_msg = bot.reply_to(message, 
        f"""🔄 *𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎...*

┌─────────────────────┐
│ 📊 Total: {str(len(accounts)).rjust(3)} Accounts │
│ 🌍 Region: {region.ljust(12)} │
└─────────────────────┘

⏳ *𝙋𝙇𝙀𝘼𝙎𝙀 𝙒𝘼𝙄𝙏...*""", parse_mode='Markdown')
    
    # Check accounts with threading
    results = check_accounts_with_threads(accounts, region, status_msg, message)
    
    # ONLY valid accounts (follow sent successfully) - NOT already followed
    valid_accounts = [r for r in results if r["valid"] and r.get("followed", False)]
    invalid_accounts = [r for r in results if not r["valid"] or not r.get("followed", False)]
    
    # Store valid accounts (only those who successfully sent follow)
    if "accounts" not in user_data[user_id]:
        user_data[user_id]["accounts"] = {}
    if region not in user_data[user_id]["accounts"]:
        user_data[user_id]["accounts"][region] = []
    
    for acc in valid_accounts:
        user_data[user_id]["accounts"][region].append({
            "uid": acc["uid"],
            "password": acc["password"]
        })
    
    response_msg = f"""✅ *𝙑𝙀𝙍𝙄𝙁𝙄𝘾𝘼𝙏𝙄𝙊𝙉 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀!*

┌─────────────────────┐
│ ✅ Valid   : {str(len(valid_accounts)).rjust(3)} Accounts │
│ ❌ Invalid : {str(len(invalid_accounts)).rjust(3)} Accounts │
│ 🌍 Region  : {region.ljust(12)} │
├─────────────────────┤
│ 💾 Total Saved: {str(len(user_data[user_id]['accounts'][region])).rjust(3)} │
└─────────────────────┘

𝗡𝗢𝗧𝗘 : 𝗪𝗔𝗛𝗜 𝗔𝗖𝗖𝗢𝗨𝗡𝗧𝗦 𝗔𝗗𝗗 𝗛𝗢𝗡𝗚𝗘 𝗝𝗜𝗦 𝗜𝗗 𝗦𝗘 3 𝗗𝗜𝗙𝗥𝗘𝗡𝗧 𝗖𝗥𝗔𝗙𝗧𝗟𝗔𝗡𝗗 𝗠𝗔𝗣𝗦 𝗞𝗛𝗘𝗟𝗔 𝗛𝗨𝗔 𝗛𝗢

📋 *𝙉𝙊𝙏𝙀:* Only accounts that successfully sent follow are saved!"""
    
    bot.edit_message_text(response_msg, status_msg.chat.id, status_msg.message_id, parse_mode='Markdown')
    user_data[user_id]["state"] = None
    bot.send_message(message.chat.id, "📋 *𝙍𝙀𝘼𝘿𝙔 𝙁𝙊𝙍 𝙉𝙀𝙓𝙏 𝘼𝘾𝙏𝙄𝙊𝙉*", parse_mode='Markdown', reply_markup=main_keyboard())

# ============== CHECK ACCOUNTS WITH THREADS ==============
def check_accounts_with_threads(accounts, region, status_msg, message):
    results = []
    chunks = list(chunk_array(accounts, 10))
    processed = 0
    
    for chunk in chunks:
        threads = []
        chunk_results = []
        
        def check_account(acc):
            try:
                response = requests.get(API_URL, params={
                    "api_key": "FFMAX",
                    "target": "2133907304",
                    "uid": acc["uid"],
                    "password": acc["password"],
                    "region": region
                }, timeout=15)
                
                data = response.json()
                if data.get("status") == "success":
                    followed = data.get("data", {}).get("followed", False)
                    # Only valid if follow was sent successfully (not already followed)
                    if followed:
                        return {**acc, "valid": True, "followed": True}
                    else:
                        return {**acc, "valid": False, "followed": False, "reason": "Already followed or error"}
                else:
                    return {**acc, "valid": False, "followed": False, "reason": data.get("message", "Unknown error")}
            except Exception as e:
                return {**acc, "valid": False, "followed": False, "reason": str(e)}
        
        # Run threads
        for acc in chunk:
            thread = threading.Thread(target=lambda a=acc: chunk_results.append(check_account(a)))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        results.extend(chunk_results)
        processed += len(chunk_results)
        
        valid_count = len([r for r in results if r.get("valid", False) and r.get("followed", False)])
        
        # Update progress
        try:
            bot.edit_message_text(
                f"""🔄 *𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎...*

┌─────────────────────┐
│ ⏳ Progress: {processed}/{len(accounts)} │
│ ✅ Valid  : {str(valid_count).rjust(3)} Found │
│ 🌍 Region: {region.ljust(12)} │
└─────────────────────┘

⏳ *𝙎𝘾𝘼𝙉𝙉𝙄𝙉𝙂... {int(processed/len(accounts)*100)}%*""",
                status_msg.chat.id, status_msg.message_id, parse_mode='Markdown'
            )
        except:
            pass
    
    return results

# ============== PROCESS FOLLOW REQUEST ==============
def process_follow_request(message, count):
    user_id = message.chat.id
    region = user_data[user_id]["follow_region"]
    target_uid = user_data[user_id]["target"]
    accounts = user_data[user_id]["accounts"][region]
    
    selected_accounts = accounts[:min(count, len(accounts))]
    
    if not selected_accounts:
        bot.reply_to(message, "❌ *𝙉𝙊 𝘼𝘾𝘾𝙊𝙐𝙉𝙏𝙎 𝘼𝙑𝘼𝙄𝙇𝘼𝘽𝙇𝙀!*", parse_mode='Markdown')
        return
    
    status_msg = bot.reply_to(message,
        f"""🚀 *𝙎𝙀𝙉𝘿𝙄𝙉𝙂 𝙁𝙊𝙇𝙇𝙊𝙒𝙀𝙍𝙎...*

┌─────────────────────┐
│ 👤 Target : {target_uid.ljust(12)} │
│ 🌍 Region : {region.ljust(12)} │
│ 📊 Total  : {str(len(selected_accounts)).rjust(3)} │
└─────────────────────┘

⏳ *𝙋𝙍𝙊𝘾𝙀𝙎𝙎𝙄𝙉𝙂... 0%*""", parse_mode='Markdown')
    
    # Process with threads
    results = process_follow_batch(selected_accounts, target_uid, region, status_msg, message)
    
    success = [r for r in results if r.get("followed", False)]
    already = [r for r in results if r.get("already", False)]
    failed = [r for r in results if not r.get("followed", False) and not r.get("already", False)]
    
    result_msg = f"""✅ *𝙁𝙊𝙇𝙇𝙊𝙒 𝙋𝙍𝙊𝘾𝙀𝙎𝙎 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀!*

┌─────────────────────┐
│ ✅ Success : {str(len(success)).rjust(3)} │
│ ⏳ Already: {str(len(already)).rjust(3)} │
│ ❌ Failed : {str(len(failed)).rjust(3)} │
├─────────────────────┤
│ 👤 Target : {target_uid.ljust(12)} │
│ 🌍 Region : {region.ljust(12)} │
│ ⏱️  Speed  : ~{len(results) * 1.5:.0f}s │
└─────────────────────┘"""
    
    if success:
        result_msg += "\n\n📋 *𝙎𝙐𝘾𝘾𝙀𝙎𝙎 𝘿𝙀𝙏𝘼𝙄𝙇𝙎:*\n"
        for i, r in enumerate(success[:10], 1):
            result_msg += f"{i}. UID: {r['uid']} | Speed: {r.get('speed', 'N/A')}\n"
        if len(success) > 10:
            result_msg += f"\n... and {len(success) - 10} more"
    
    bot.edit_message_text(result_msg, status_msg.chat.id, status_msg.message_id, parse_mode='Markdown')
    user_data[user_id]["state"] = None
    bot.send_message(message.chat.id, "📋 *𝙍𝙀𝘼𝘿𝙔 𝙁𝙊𝙍 𝙉𝙀𝙓𝙏 𝘼𝘾𝙏𝙄𝙊𝙉*", parse_mode='Markdown', reply_markup=main_keyboard())

# ============== PROCESS FOLLOW BATCH WITH THREADS ==============
def process_follow_batch(accounts, target_uid, region, status_msg, message):
    results = []
    chunks = list(chunk_array(accounts, 5))
    processed = 0
    
    for chunk in chunks:
        threads = []
        chunk_results = []
        
        def follow_account(acc):
            try:
                response = requests.get(API_URL, params={
                    "api_key": "FFMAX",
                    "target": target_uid,
                    "uid": acc["uid"],
                    "password": acc["password"],
                    "region": region
                }, timeout=15)
                
                data = response.json()
                result = {
                    "uid": acc["uid"],
                    "password": acc["password"],
                    "followed": data.get("data", {}).get("followed", False),
                    "already": not data.get("data", {}).get("followed", False) and "already" in data.get("message", ""),
                    "speed": data.get("data", {}).get("speed", "N/A"),
                    "name": data.get("data", {}).get("target_name", "Unknown")
                }
                return result
            except:
                return {"uid": acc["uid"], "password": acc["password"], "followed": False, "already": False}
        
        # Run threads
        for acc in chunk:
            thread = threading.Thread(target=lambda a=acc: chunk_results.append(follow_account(a)))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        results.extend(chunk_results)
        processed += len(chunk_results)
        
        success_count = len([r for r in results if r.get("followed", False)])
        already_count = len([r for r in results if r.get("already", False)])
        failed_count = len([r for r in results if not r.get("followed", False) and not r.get("already", False)])
        percent = int(processed / len(accounts) * 100)
        
        # Update progress
        try:
            bot.edit_message_text(
                f"""🚀 *𝙎𝙀𝙉𝘿𝙄𝙉𝙂 𝙁𝙊𝙇𝙇𝙊𝙒𝙀𝙍𝙎...*

┌─────────────────────┐
│ ⏳ Progress: {processed}/{len(accounts)} ({percent}%) │
│ ✅ Done   : {str(success_count).rjust(3)} │
│ ⏳ Already: {str(already_count).rjust(3)} │
│ ❌ Failed : {str(failed_count).rjust(3)} │
├─────────────────────┤
│ 👤 Target : {target_uid.ljust(12)} │
│ 🌍 Region : {region.ljust(12)} │
└─────────────────────┘

⏳ *𝙋𝙍𝙊𝘾𝙀𝙎𝙎𝙄𝙉𝙂... {percent}%*""",
                status_msg.chat.id, status_msg.message_id, parse_mode='Markdown'
            )
        except:
            pass
    
    return results
# ============= UNFOLLOW FEATURE =============
@bot.message_handler(func=lambda message: message.text == "🔴 UNFOLLOW SEND")
def unfollow_send(message):
    user_id = message.chat.id
    if user_id not in user_data or "accounts" not in user_data[user_id]:
        bot.reply_to(
            message, 
            "❌ *NO ACCOUNTS FOUND!*\n\n⚠️ Please add accounts first using:\n🔴 TOKEN ADD", 
            parse_mode='Markdown', 
            reply_markup=main_keyboard()
        )
        return

    user_data[user_id]["state"] = "awaiting_unfollow_uid"
    bot.reply_to(
        message, 
        "🔻 *UNFOLLOW SETUP*\n\n📝 *Send Target UID to Unfollow:*", 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("state") == "awaiting_unfollow_uid")
def process_unfollow_target(message):
    user_id = message.chat.id
    target_uid = message.text.strip()
    
    if not target_uid.isdigit():
        bot.reply_to(message, "❌ *Invalid UID!* Please send a valid numeric UID.")
        return

    user_data[user_id]["state"] = None
    status_msg = bot.reply_to(message, "⏳ *Processing Unfollow Request...*", parse_mode='Markdown')

    all_accounts = []
    for region, acc_list in user_data[user_data[user_id]["accounts"].keys() if "accounts" in user_data[user_id] else []]:
        pass

    all_accounts = []
    for region, acc_list in user_data[user_id]["accounts"].items():
        all_accounts.extend(acc_list)

    success = 0
    failed = 0

    for acc in all_accounts:
        try:
            payload = {
                "uid": acc.get("uid"),
                "password": acc.get("password"),
                "target_uid": target_uid
            }
            res = requests.post(UNFOLLOW_API_URL, json=payload, timeout=10)
            if res.status_code == 200:
                success += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    result_text = f"""
✅ *UNFOLLOW COMPLETED!*

🎯 *Target UID:* `{target_uid}`
🟢 *Successful:* `{success}`
🔴 *Failed:* `{failed}`
📊 *Total Tokens Used:* `{len(all_accounts)}`
"""
    bot.edit_message_text(
        result_text, 
        chat_id=user_id, 
        message_id=status_msg.message_id, 
        parse_mode='Markdown'
    )
    
# ============== ERROR HANDLER ==============
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    if message.text and not message.text.startswith("/"):
        # Already handled in main handler
        pass

# ============= WEB SERVER & START BOT =============
@app.route('/status')
@app.route('/')
def bot_ping_status():
    return "Bot is active and running!", 200

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.polling(non_stop=True, skip_pending=True)
        except Exception as e:
            print(f"Error in bot polling: {e}")
            import time
            time.sleep(3)

if __name__ == "__main__":
    print("🚀 Bot started successfully!")
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
