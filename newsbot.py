import os
import sys
import re
import argparse
import sqlite3
import logging
import asyncio
import shutil
import subprocess
import numpy as np
import requests
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.functions.contacts import SearchRequest

# ==========================================
# 1. CONFIGURATION (EDIT THESE)
# ==========================================
API_ID = 1234567 
API_HASH = "your_api_hash_here" 
TARGET_CHANNEL = "YourChannelUsername" # Without the @
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

SIMILARITY_THRESHOLD = 0.82
DB_FILE = "news_bot.db"
DOWNLOAD_DIR = "downloads/"
BACKUP_DIR = "backups/"

# Ensure required directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

# ==========================================
# 2. INITIALIZATION & DATABASE
# ==========================================
def get_db():
    return sqlite3.connect(DB_FILE, timeout=15.0)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sources (username TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts 
                 (id INTEGER PRIMARY KEY, msg_id INTEGER, text TEXT, 
                 vector BLOB, word_count INTEGER, timestamp REAL)''')
    conn.commit()
    conn.close()

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# ==========================================
# 3. SPAM FILTER, AI & NLP
# ==========================================
AD_ADMIN_KEYWORDS = [
    "تبلیغات", "جهت رزرو", "پست موقت", "عضو شوید", "لینک زیر", 
    "کلیک کنید", "joinchat", "t.me/+", "خرید و فروش", "اسپانسر",
    "ارتباط با ما", "ارتباط با ادمین", "تخفیف ویژه", "هم اکنون بپیوندید",
    "ثبت سفارش", "فروش ویژه", "قیمت استثنایی", "ادمین", "تبادل",
    "کانال در حال بروزرسانی", "رزرو تبلیغ"
]

def is_valid_news(text):
    if not text: return False
    for keyword in AD_ADMIN_KEYWORDS:
        if keyword in text:
            return False
    return True

def init_ai():
    global normalizer, word_tokenize
    if 'normalizer' not in globals():
        from hazm import Normalizer, word_tokenize
        logging.info("Loading Hazm NLP for Farsi text cleaning...")
        normalizer = Normalizer()
        logging.info("Ready to use Google Gemini Cloud API for embeddings.")

def process_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    return normalizer.normalize(text).strip()

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text}]}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['embedding']['values']
    except Exception as e:
        logging.error(f"Cloud API Error: {e}")
        return None

# ==========================================
# 4. CORE DECISION ENGINE
# ==========================================
def analyze_and_decide(text, chat_username):
    if not is_valid_news(text):
        return {"type": "IGNORE"}
        
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT username FROM sources WHERE username = ?", (chat_username.lower(),))
    if not c.fetchone():
        conn.close()
        return {"type": "IGNORE"}

    clean_text = process_text(text)
    words = word_tokenize(clean_text)
    word_count = len(words)

    if word_count < 8:
        conn.close()
        return {"type": "IGNORE"}

    raw_vector = get_embedding(clean_text)
    if not raw_vector:
        conn.close()
        return {"type": "IGNORE"}
        
    vector = np.array(raw_vector, dtype=np.float32)
    two_days_ago = (datetime.now() - timedelta(days=2)).timestamp()
    
    c.execute("SELECT id, msg_id, vector, word_count FROM posts WHERE timestamp > ?", (two_days_ago,))
    best_match = {"id": None, "msg_id": None, "score": 0, "words": 0}
    
    for row in c.fetchall():
        db_id, msg_id, db_vector_blob, db_word_count = row
        db_vector = np.frombuffer(db_vector_blob, dtype=np.float32)
        score = cosine_similarity(vector, db_vector)
        
        if score > best_match["score"]:
            best_match.update({"id": db_id, "msg_id": msg_id, "score": score, "words": db_word_count})

    action = {"type": "IGNORE"}

    if best_match["score"] >= SIMILARITY_THRESHOLD:
        if word_count > best_match["words"]:
            action = {"type": "EDIT", "msg_id": best_match["msg_id"], "db_id": best_match["id"], "vector": vector, "words": word_count}
        else:
            logging.info(f"Ignored duplicate redundant news. (Score: {best_match['score']:.2f}).")
    else:
        action = {"type": "POST", "vector": vector, "words": word_count}

    conn.close()
    return action

# ==========================================
# 5. ADMINISTRATIVE TOOLS (Backups & Management)
# ==========================================
def backup_system():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"newsbot_backup_{timestamp}.sqlite")
    
    if os.path.exists(DB_FILE):
        shutil.copy2(DB_FILE, backup_file)
        print(f"\n[SUCCESS] Database backup saved to: {backup_file}")
    else:
        print("\n[ERROR] No database file found to backup.")

def update_dependencies():
    print("\n[INFO] Updating Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "requests", "telethon", "hazm", "numpy"])
    print("[SUCCESS] All dependencies updated.")

def uninstall_app():
    confirm = input("\n[WARNING] This will stop the daemon and remove the newsbot setup. Continue? (y/N): ")
    if confirm.lower() == 'y':
        print("[INFO] Stopping systemd service...")
        subprocess.run(["sudo", "systemctl", "stop", "newsbot"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "disable", "newsbot"], stderr=subprocess.DEVNULL)
        
        service_path = "/etc/systemd/system/newsbot.service"
        if os.path.exists(service_path):
            subprocess.run(["sudo", "rm", service_path])
            subprocess.run(["sudo", "systemctl", "daemon-reload"])
            
        cmd_path = "/usr/local/bin/newsbot"
        if os.path.exists(cmd_path):
            subprocess.run(["sudo", "rm", cmd_path])

        print("\n[SUCCESS] Systemd service and CLI command uninstalled.")
        print("Note: Your project directory (~/telegram_news_bot) was kept safe. You can remove it manually if desired.")
        sys.exit(0)

# ==========================================
# 6. INTERACTIVE CLI MENU
# ==========================================
def interactive_menu():
    while True:
        print("\n==============================================")
        print("           📰 TELEGRAM NEWS BOT MENU           ")
        print("==============================================")
        print(" [1]  📊 Check Service Status")
        print(" [2]  ▶️  Start Background Daemon")
        print(" [3]  ⏹️  Stop Background Daemon")
        print(" [4]  🔄 Restart Daemon")
        print(" [5]  📜 View Live Logs")
        print("----------------------------------------------")
        print(" [6]  ➕ Add Source Channel")
        print(" [7]  ➖ Remove Source Channel")
        print(" [8]  📋 List Source Channels")
        print(" [9]  🔍 Search Telegram for Channels")
        print("----------------------------------------------")
        print(" [10] 💾 Backup Database")
        print(" [11] 📦 Update Dependencies")
        print(" [12] ⚠️  Uninstall System Service")
        print(" [0]  ❌ Exit")
        print("==============================================")
        
        choice = input("Select an option [0-12]: ").strip()
        
        if choice == "1":
            subprocess.run(["sudo", "systemctl", "status", "newsbot"])
        elif choice == "2":
            subprocess.run(["sudo", "systemctl", "start", "newsbot"])
            print("[INFO] Service started.")
        elif choice == "3":
            subprocess.run(["sudo", "systemctl", "stop", "newsbot"])
            print("[INFO] Service stopped.")
        elif choice == "4":
            subprocess.run(["sudo", "systemctl", "restart", "newsbot"])
            print("[INFO] Service restarted.")
        elif choice == "5":
            print("\n--- Press Ctrl+C to exit logs ---")
            try:
                subprocess.run(["tail", "-f", "bot.log"])
            except KeyboardInterrupt:
                pass
        elif choice == "6":
            ch = input("Enter channel username (without @): ").strip()
            if ch:
                conn = get_db()
                try:
                    conn.execute("INSERT INTO sources (username) VALUES (?)", (ch.replace("@", "").lower(),))
                    conn.commit()
                    print(f"[SUCCESS] Added @{ch}")
                except sqlite3.IntegrityError:
                    print(f"[NOTICE] @{ch} is already in the list.")
                conn.close()
        elif choice == "7":
            ch = input("Enter channel username to remove (without @): ").strip()
            if ch:
                conn = get_db()
                conn.execute("DELETE FROM sources WHERE username=?", (ch.replace("@", "").lower(),))
                conn.commit()
                conn.close()
                print(f"[SUCCESS] Removed @{ch}")
        elif choice == "8":
            conn = get_db()
            print("\n--- Monitored Channels ---")
            for row in conn.execute("SELECT username FROM sources").fetchall():
                print(f" - @{row[0]}")
            conn.close()
        elif choice == "9":
            kw = input("Enter keyword to search (e.g., اخبار): ").strip()
            if kw:
                subprocess.run([sys.executable, __file__, "search", "--keyword", kw])
        elif choice == "10":
            backup_system()
        elif choice == "11":
            update_dependencies()
        elif choice == "12":
            uninstall_app()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid selection, try again.")

# ==========================================
# 7. MAIN ENTRYPOINT
# ==========================================
def main():
    init_db()
    parser = argparse.ArgumentParser(description="Telegram AI News Bot CLI")
    parser.add_argument("command", nargs="?", default="menu", 
                        choices=["menu", "login", "run", "add", "remove", "list", "search", "backup"], 
                        help="Command to execute")
    parser.add_argument("--channel", type=str, help="Channel username (without @)")
    parser.add_argument("--keyword", type=str, help="Keyword for auto-search")
    
    args = parser.parse_args()

    if args.command == "menu":
        interactive_menu()

    elif args.command == "login":
        print("\n--- Initializing Telegram Login ---")
        client = TelegramClient('news_session', API_ID, API_HASH)
        client.start()
        print("\n[SUCCESS] Session saved. You can now run the bot.")
        client.disconnect()

    elif args.command == "search":
        if not args.keyword:
            return print("Error: Provide a keyword using --keyword")
        async def do_search():
            await client.connect()
            result = await client(SearchRequest(q=args.keyword, limit=5))
            conn = get_db()
            print(f"\n--- Top 5 Channels Found for '{args.keyword}' ---")
            for chat in result.chats:
                if getattr(chat, 'username', None):
                    try:
                        conn.execute("INSERT INTO sources (username) VALUES (?)", (chat.username.lower(),))
                        print(f"[ADDED] @{chat.username} - {chat.title}")
                    except sqlite3.IntegrityError:
                        print(f"[EXISTS] @{chat.username} is already in database.")
            conn.commit()
            conn.close()
        client = TelegramClient('news_session', API_ID, API_HASH)
        client.loop.run_until_complete(do_search())

    elif args.command == "run":
        init_ai()
        client = TelegramClient('news_session', API_ID, API_HASH)

        @client.on(events.NewMessage)
        async def news_handler(event):
            text = event.message.text or event.message.caption
            if not text: return
            
            chat = await event.get_chat()
            chat_username = getattr(chat, 'username', None)
            if not chat_username: return

            action = await asyncio.to_thread(analyze_and_decide, text, chat_username)
            if action["type"] == "IGNORE": return

            media_path = None
            try:
                if event.message.photo:
                    media_path = await event.message.download_media(file=DOWNLOAD_DIR)
                elif event.message.media and hasattr(event.message.media, 'webpage'):
                    pass 
            except Exception as med_err:
                logging.warning(f"Could not download media: {med_err}")

            char_limit = 1000 if media_path else 4090
            safe_text = text[:char_limit] + "..." if len(text) > char_limit else text

            conn = get_db()

            try:
                if action["type"] == "POST":
                    msg = await client.send_message(TARGET_CHANNEL, safe_text, file=media_path)
                    conn.execute("INSERT INTO posts (msg_id, text, vector, word_count, timestamp) VALUES (?, ?, ?, ?, ?)",
                              (msg.id, safe_text, action["vector"].tobytes(), action["words"], datetime.now().timestamp()))
                    logging.info(f"POSTED new news (Has Photo: {bool(media_path)}) from @{chat_username}")
                        
                elif action["type"] == "EDIT":
                    await client.edit_message(TARGET_CHANNEL, action["msg_id"], safe_text, file=media_path)
                    conn.execute("UPDATE posts SET text=?, vector=?, word_count=?, timestamp=? WHERE id=?", 
                              (safe_text, action["vector"].tobytes(), action["words"], datetime.now().timestamp(), action["db_id"]))
                    logging.info(f"EDITED message {action['msg_id']} with better text (Has Photo: {bool(media_path)})")
                
                conn.commit()
            except Exception as e:
                logging.error(f"Telegram API Error: {e}")
            finally:
                conn.close()
                if media_path and os.path.exists(media_path):
                    os.remove(media_path)

        logging.info("Bot is listening for news and photos...")
        client.start()
        client.run_until_disconnected()

    elif args.command == "backup":
        backup_system()

if __name__ == '__main__':
    main()
