# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Windows OS (for auto-start features)
- Telegram account
- Kaggle account(s)

## Step 1: Clone Repository

```bash
git clone https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant.git
cd Kaggle-Monitor-Ai-Telegram-Assitant/kaggle-monitor
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Optional but Recommended** (for 6x faster analysis):
```bash
pip install paddleocr paddlepaddle
```

## Step 3: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Send a message to your bot
6. Get your **user ID** by messaging **@userinfobot**

## Step 4: Configure Bot

1. Copy the example config:
   ```bash
   copy config.yaml.example config.yaml
   ```

2. Edit `config.yaml`:
   ```yaml
   bot_token: "YOUR_BOT_TOKEN_HERE"  # Paste your bot token
   owner_user_id: YOUR_USER_ID_HERE  # Paste your user ID (number only)
   ```

3. Save the file

## Step 5: Test the Bot

```bash
python remote_starter.py
```

You should see:
```
============================================================
Remote Starter Bot Starting
============================================================
Bot is ready! Waiting for commands from your phone...
```

## Step 6: Test from Phone

1. Open Telegram on your phone
2. Find your bot
3. Send: `/start`
4. Send: `/check`

The bot should respond and start monitoring!

## Step 7: Auto-Start (Optional)

To start the bot automatically when Windows boots:

1. Press `Win + R`
2. Type: `shell:startup`
3. Copy `start_hidden.vbs` to the Startup folder

Or run:
```bash
copy start_hidden.vbs "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
```

## Troubleshooting

### "No module named 'telegram'"
```bash
pip install python-telegram-bot
```

### "No Kaggle windows found"
- Make sure Chrome is open
- Open Kaggle notebook tabs
- Don't minimize windows

### Bot doesn't respond
- Check bot token in `config.yaml`
- Check user ID is correct (number only, no quotes)
- Restart bot: `Ctrl+C` then `python remote_starter.py`

## Next Steps

- Read [README.md](README.md) for usage instructions
- See [INSTALL_PADDLEOCR.md](INSTALL_PADDLEOCR.md) for faster analysis
- Check [AUTOSTART_GUIDE.md](AUTOSTART_GUIDE.md) for auto-start details

## Security Note

⚠️ **Never commit `config.yaml` to GitHub!**

The `.gitignore` file is configured to exclude:
- `config.yaml` (your sensitive config)
- `state.json` (bot state)
- `logs/` (log files)
- `screenshots/` (screenshot folders)

Always use `config.yaml.example` as a template.

## Support

If you encounter issues:
1. Check logs in `logs/app.log`
2. Read documentation files
3. Open an issue on GitHub

Happy monitoring! 🚀
