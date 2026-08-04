# 📰 Telegram AI News Bot & Aggregator

An automated, enterprise-grade Farsi news aggregator, spam filter, and dynamic publisher built in Python. It monitors your selected Telegram source channels, normalizes Persian text using **Hazm NLP**, strips attributions, filters spam and proxy ads, and uses **Google Gemini AI** (hybrid vector embeddings + LLM tie-breaking) to eliminate duplicate news coverage before publishing to your target channel.

---

## ✨ Key Features

* **Hybrid AI Deduplication**:
  * **Fast Lane (Math)**: Calculates cosine similarity using `gemini-embedding-001` vectors.
  * **Smart Lane (LLM)**: Routes uncertain "Gray Zone" posts (0.75 – 0.88 similarity) to `gemini-2.5-flash` to make nuanced decisions on Persian news contexts.
  * **Exponential Backoff**: Built-in retry loops (1s, 2s, 4s) to handle API rate limits (HTTP 429) gracefully.
* **Smart Media Sync**:
  * Automatically waits 3 seconds and re-fetches incoming Telegram posts to ensure heavy attachments (Photos, Videos, GIFs) are fully captured.
  * Respects Telegram's 1024-caption limit by automatically dropping media for long-form articles (>1000 chars) to post the full 4000-char text without truncation.
* **Farsi NLP Optimization**: Uses **Hazm** to normalize Persian character variants, spacing, and grammar.
* **Advanced Ad & Spam Filtering**:
  * Case-insensitive keyword blocking for generic ads, channel promo links, and admin bookings.
  * Specialized filtering for VPN, Proxy, V2Ray, and config sellers.
* **Surgical Attribution Removal**: Automatically strips channel signatures, watermarks, editor credits (`✍🏻`, `🖊`), source links, and `@usernames`.
* **Interactive CLI Management & Backup**: Full-featured terminal menu to add/remove channels, run back-ups, check live logs, and manage systemd services.

---

## 🛠️ Step 1: Obtain Telegram API Credentials

To run a Telegram userbot, you need API credentials from Telegram:

1. Open your browser and go to [my.telegram.org](https://my.telegram.org).
2. Enter your phone number (including your country code, e.g., `+98...` or `+1...`).
3. Enter the confirmation code sent to your official Telegram app.
4. Once logged in, click on **API development tools**.
5. Fill out the application creation form:
   * **App title**: Any name (e.g., `MyNewsBot`).
   * **Short name**: Short identifier (e.g., `mynewsbot`).
   * **Platform**: Select **Desktop**.
6. Click **Create application**.
7. Copy your **`api_id`** (a numeric ID) and **`api_hash`** (a 32-character string).

---

## 🧠 Step 2: Obtain Google Gemini API Key

1. Go to Google AI Studio at [aistudio.google.com](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** in the left sidebar menu.
4. Click **Create API key** and copy your generated key string.

---

## 📥 Step 3: Clone & Configure the Project

1. **Clone the repository to your server or local machine:**
   ```bash
   git clone [https://github.com/armanpier/telegram-news-bot.git](https://github.com/armanpier/telegram-news-bot.git)
   cd telegram-news-bot
