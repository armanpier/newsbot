# 📰 Telegram AI News Bot & Aggregator

An automated, intelligent Farsi news aggregator and filter built in Python. It monitors your selected source channels, cleans up unwanted text/attributions using **Hazm NLP**, filters spam and duplicates using **Google Gemini AI embeddings**, and publishes clean, professional news posts directly to your target Telegram channel.

---

## ✨ Features

* **AI-Powered Deduplication**: Uses Google Gemini embedding models to understand semantic similarity and prevent redundant or duplicate news coverage.
* **Farsi Text Optimization**: Integrates Hazm NLP to normalize and process Persian text.
* **Ad & Spam Filtering**: Automatically filters out advertisements, sponsored posts, and short or irrelevant blurbs.
* **Surgical Attribution Removal**: Strips away original channel watermarks, tags, writer names, and `@usernames` so your channel looks entirely original.
* **Database Backup & Restore**: Built-in snapshot system to back up your vector database and restore it anytime via the CLI menu.
* **Interactive CLI Control Panel**: Easy-to-use menu system to manage sources, run the daemon, check status, and review live logs.

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Get Your Telegram API Credentials
To run a Telegram userbot, you need a pair of API credentials from Telegram:

1. Open your browser and go to [my.telegram.org](https://my.telegram.org).
2. Enter your phone number (including your country code) associated with your Telegram account.
3. Enter the confirmation code sent to your official Telegram app.
4. Once logged in, click on **API development tools**.
5. Fill out the application creation form:
   * **App title**: Give it any name (e.g., `MyNewsBot`).
   * **Short name**: Give it a short identifier (e.g., `mynewsbot`).
   * **Platform**: Select **Desktop**.
6. Click **Create application**.
7. Copy your **`api_id`** (a string of numbers) and **`api_hash`** (a long alphanumeric string) to a safe place.

### Step 2: Get Your Google Gemini API Key
Because this bot uses Google's AI to compare news and filter duplicates, you will need a free API key:

1. Go to Google AI Studio at [aistudio.google.com](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** in the left menu.
4. Create a new key and copy it to a safe place.

---

### Step 3: Installation

Choose **ONE** of the installation methods below. (If you are unsure, use Option B).

#### Option A: One-Line Automated Installation (Linux/VPS)
If you are using an Ubuntu/Linux VPS, you can use the automated script:
```bash
git clone [https://github.com/armanpier/telegram-news-bot.git](https://github.com/armanpier/telegram-news-bot.git) ~/telegram_news_bot
cd ~/telegram_news_bot
chmod +x install.sh
./install.sh
