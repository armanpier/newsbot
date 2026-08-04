#!/bin/bash
set -e

echo "=============================================="
echo "    Installing Telegram AI News Bot Setup     "
echo "=============================================="

# 1. Update system & install dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv sqlite3 git

# 2. Setup project directory
INSTALL_DIR="/root/telegram_news_bot"
sudo mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy or clone files (Assuming script is run from local repo or cloned)
if [ ! -f "newsbot.py" ]; then
    echo "Please clone your repository into $INSTALL_DIR first."
    exit 1
fi

# 3. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Prompt for Configuration Keys securely
echo "----------------------------------------------"
read -p "Enter your Telegram API_ID: " TG_API_ID
read -p "Enter your Telegram API_HASH: " TG_API_HASH
read -p "Enter your Google Gemini API Key: " GEMINI_API_KEY
read -p "Enter Target Channel Username (without @): " TARGET_CHANNEL

# Inject keys into python script templates or environment
sed -i "s/YOUR_API_ID/$TG_API_ID/" newsbot.py
sed -i "s/YOUR_API_HASH/$TG_API_HASH/" newsbot.py
sed -i "s/YOUR_GEMINI_API_KEY/$GEMINI_API_KEY/" newsbot.py
sed -i "s/khabaravalai/$TARGET_CHANNEL/" newsbot.py

# 5. Create Global CLI Shortcut
sudo bash -c 'cat > /usr/local/bin/newsbot << 'EOF'
#!/bin/bash
cd /root/telegram_news_bot
source venv/bin/activate
python -P newsbot.py "$@"
EOF'
sudo chmod +x /usr/local/bin/newsbot

# 6. Create Systemd Service
sudo bash -c 'cat > /etc/systemd/system/newsbot.service << 'EOF'
[Unit]
Description=Telegram AI News Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram_news_bot
ExecStart=/root/telegram_news_bot/venv/bin/python -P /root/telegram_news_bot/newsbot.py run
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable newsbot

echo "----------------------------------------------"
echo "[SUCCESS] Installation complete!"
echo "Next step: Run 'newsbot login' to authorize your Telegram account."
echo "=============================================="
