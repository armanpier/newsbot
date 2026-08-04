# 📰 Telegram AI News Bot & Aggregator

An automated, enterprise-grade Farsi news aggregator, spam filter, and dynamic publisher built in Python. It monitors your selected Telegram source channels, normalizes Persian text using **Hazm NLP**, strips attributions, filters spam and proxy ads, and uses **Google Gemini AI** (hybrid vector embeddings + LLM tie-breaking) to eliminate duplicate news coverage before publishing to your target channel.

---

## ✨ Key Features

- **Hybrid AI Deduplication**
  - **Fast Lane (Math):** Calculates cosine similarity using `gemini-embedding-001` vectors.
  - **Smart Lane (LLM):** Routes uncertain "Gray Zone" posts (0.75–0.88 similarity) to `gemini-2.5-flash` for nuanced duplicate detection.
  - **Exponential Backoff:** Built-in retry logic (1s, 2s, 4s) gracefully handles API rate limits (HTTP 429).

- **Smart Media Sync**
  - Waits 3 seconds before re-fetching Telegram posts to ensure heavy attachments (photos, videos, GIFs) are fully available.
  - Automatically removes media from posts exceeding Telegram's 1024-character caption limit so the full article (up to ~4000 characters) is published without truncation.

- **Farsi NLP Optimization**
  - Uses **Hazm** to normalize Persian character variants, spacing, and grammar.

- **Advanced Ad & Spam Filtering**
  - Case-insensitive keyword blocking for advertisements, channel promotions, and admin booking messages.
  - Specialized filtering for VPN, Proxy, V2Ray, and configuration sellers.

- **Surgical Attribution Removal**
  - Automatically removes channel signatures, watermarks, editor credits (`✍🏻`, `🖊`), source links, and `@usernames`.

- **Interactive CLI Management**
  - Add/remove channels, create backups, monitor logs, and manage systemd services from an interactive terminal menu.

---

# 🚀 Installation

## 🛠️ Step 1: Obtain Telegram API Credentials

To run the bot, you'll need Telegram API credentials.

1. Visit **https://my.telegram.org**
2. Log in using your Telegram phone number.
3. Click **API Development Tools**.
4. Create a new application:
   - **App title:** Any name (e.g. `MyNewsBot`)
   - **Short name:** Any identifier (e.g. `mynewsbot`)
   - **Platform:** Desktop
5. Click **Create Application**.
6. Copy your:
   - `api_id`
   - `api_hash`

---

## 🧠 Step 2: Obtain a Google Gemini API Key

1. Visit **https://aistudio.google.com/**
2. Sign in with your Google account.
3. Click **Get API Key**.
4. Create a new API key.
5. Copy the generated key.

---

## 📦 Step 3: Install System Prerequisites (Ubuntu/Debian)

For a fresh VPS:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3 python3-pip python3-venv sqlite3 -y
```

---

## 📥 Step 4: Clone & Configure the Project

Clone the repository:

```bash
git clone https://github.com/armanpier/telegram-news-bot.git
cd telegram-news-bot
```

Open the configuration file:

```bash
nano newsbot.py
```

Edit the configuration variables:

```python
# ==========================================
# 1. CONFIGURATION (EDIT THESE)
# ==========================================

API_ID = 1234567
API_HASH = "your_api_hash_here"
TARGET_CHANNEL = "YourChannelUsername"   # WITHOUT @
GEMINI_API_KEY = "YOUR_GEMINI_KEY"
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

# 🚀 Step 5: Installation Options

Choose **one** of the following installation methods.

## Option A — Automated Installation (Recommended for VPS)

Ideal for Ubuntu/Linux servers using **systemd**.

```bash
chmod +x install.sh
./install.sh
```

This script will:

- Create a Python virtual environment
- Install all dependencies
- Configure the bot as a systemd service
- Enable background execution

---

## Option B — Manual Virtual Environment

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows (Command Prompt)

```cmd
venv\Scripts\activate.bat
```

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Option C — Global Installation

If you're using Docker or an isolated environment:

```bash
pip install telethon hazm numpy requests nltk==3.9.4
```

---

## 📄 requirements.txt

```text
telethon
hazm
numpy
requests
nltk==3.9.4
```

---

# 🎮 Step 6: Telegram Authentication & CLI

## First Login

Generate your Telegram session file.

### Automated Installation

```bash
newsbot login
```

### Manual Installation

```bash
python3 newsbot.py login
```

Follow the prompts to enter:

- Phone number
- Telegram verification code

---

## Interactive Control Panel

### Automated Installation

```bash
newsbot
```

### Manual Installation

```bash
python3 newsbot.py menu
```

Example:

```text
==============================================
           📰 TELEGRAM NEWS BOT MENU
==============================================
 [1]  📊 Check Service Status
 [2]  ▶️  Start Background Daemon
 [3]  ⏹️  Stop Background Daemon
 [4]  🔄 Restart Daemon
 [5]  📜 View Live Logs
----------------------------------------------
 [6]  ➕ Add Source Channel
 [7]  ➖ Remove Source Channel
 [8]  📋 List Source Channels
 [9]  🔍 Search Telegram for Channels
----------------------------------------------
 [10] 💾 Backup Database
 [11] 📦 Update Dependencies
 [12] ⚠️  Uninstall System Service
 [0]  ❌ Exit
==============================================
```

- Select **[6]** to add source channels (without `@`).
- Select **[2]** to start the background daemon.

Alternatively, run directly:

```bash
python3 newsbot.py run
```

---

# 📁 Database & Backups

The bot stores duplicate detection data and embedding vectors in a local SQLite database:

```text
news_bot.db
```

Create a backup using:

### CLI Menu

```
Option [10]
```

### Command Line

```bash
python3 newsbot.py backup
```

Backups are stored in:

```text
backups/
```

---

# ❓ Troubleshooting

## How does media handling work?

Telegram limits media captions to **1024 characters**.

If a post contains media and exceeds **1000 characters**, the bot automatically removes the attachment and publishes the full text (up to ~4000 characters).

---

## What happens if Google Gemini returns HTTP 429?

The bot automatically retries using exponential backoff:

- 1 second
- 2 seconds
- 4 seconds

If all retries fail, the post is treated as new content to ensure breaking news is never skipped.

---

## How do I monitor activity?

From the CLI menu:

```
Option [5]
```

Or directly:

```bash
tail -f bot.log
```

---

# 📜 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.
