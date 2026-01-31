# 🤖 Kaggle Monitor AI Telegram Assistant

Monitor multiple Kaggle training notebooks and get AI-powered status updates via Telegram!

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Qwen2-VL for accurate notebook status detection
- 📱 **Phone Control** - Monitor from anywhere with Telegram commands
- ⚡ **Fast Pattern Matching** - 100+ patterns with PaddleOCR (6x faster)
- 🔍 **Comprehensive Details** - Get detailed analysis of all screenshots
- 🚀 **Auto-Start** - Runs automatically on Windows boot
- 📊 **Smart Detection** - Distinguishes EMPTY, RUNNING, COMPLETE, ERROR states
- 🎯 **No Browser Setup** - Works with your already-open Chrome tabs

## 🎬 Demo

```
You: /check

Bot: 🚀 Starting monitoring on your PC...
     ⏱️ This will take 5-20 minutes.
     (Using open-source AI model for accurate analysis)

Bot: 🧠 Kaggle Monitor — Run #2026-02-01_15-30-00

     A: 🟢 RUNNING
     📓 my_training_notebook
     📸 58 screenshots analyzed
     
     🟢 TRAINING IS RUNNING
     
     📊 Training Progress:
       • Screenshot 12: Epoch 3/10, Loss: 0.27, Acc: 85%
       • Screenshot 18: Step 450/1500, 30% done
       • Screenshot 24: GPU: 5.2GB/6GB
       [... detailed analysis ...]
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant.git
cd Kaggle-Monitor-Ai-Telegram-Assitant/kaggle-monitor
pip install -r requirements.txt
```

### 2. Setup Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy your bot token
4. Get your user ID from [@userinfobot](https://t.me/userinfobot)

### 3. Configure

```bash
copy config.yaml.example config.yaml
```

Edit `config.yaml`:
```yaml
bot_token: "YOUR_BOT_TOKEN_HERE"
owner_user_id: YOUR_USER_ID_HERE
```

### 4. Run

```bash
python remote_starter.py
```

### 5. Use from Phone

Open Telegram → Find your bot → Send `/check`

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[INSTALL_PADDLEOCR.md](INSTALL_PADDLEOCR.md)** - Install PaddleOCR for 6x faster analysis
- **[AUTOSTART_GUIDE.md](AUTOSTART_GUIDE.md)** - Auto-start on Windows boot
- **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)** - Pattern matching system (100+ patterns)
- **[FINAL_IMPROVEMENTS.md](FINAL_IMPROVEMENTS.md)** - Latest features and improvements

## 🎯 How It Works

1. **Screenshot Capture** - Scrolls Kaggle pages top to bottom, captures all content
2. **Text Extraction** - Uses PaddleOCR (optional) for fast text extraction
3. **Pattern Matching** - 100+ patterns detect common states instantly
4. **AI Analysis** - Qwen2-VL analyzes uncertain cases with high accuracy
5. **Comprehensive Summary** - Aggregates findings into detailed report
6. **Telegram Delivery** - Sends results to your phone

## 📊 Performance

| Method | Speed | Accuracy |
|--------|-------|----------|
| **PaddleOCR + Patterns** | **0.4s/screenshot** | **95%+** |
| Qwen AI only | 2.5s/screenshot | 95%+ |
| Tesseract + Patterns | 1.3s/screenshot | 80% |

**With PaddleOCR**: 70-80% of screenshots use fast path (0.4s each)

## 🔧 Requirements

- Python 3.8+
- Windows OS (for auto-start features)
- 6GB+ GPU (for Qwen AI)
- 32GB+ RAM recommended
- Chrome browser

## 📦 Installation

### Basic (Required)
```bash
pip install -r requirements.txt
```

### Optional (Recommended - 6x faster)
```bash
pip install paddleocr paddlepaddle
```

### Optional (GPU acceleration)
```bash
pip install paddlepaddle-gpu
```

## 🎮 Commands

- `/start` - Show help
- `/check` - Start monitoring now
- `/status` - Check if monitoring is running

## 🔒 Security

⚠️ **Important**: Never commit `config.yaml` to GitHub!

The `.gitignore` file excludes:
- `config.yaml` (your bot token and user ID)
- `state.json` (bot state)
- `logs/` (log files)
- `screenshots/` (captured images)

Always use `config.yaml.example` as a template.

## 🐛 Troubleshooting

### "No Kaggle windows found"
- Open Chrome with Kaggle notebook tabs
- Don't minimize windows
- Make sure tabs are visible

### Bot doesn't respond
- Check `config.yaml` has correct bot token
- Check user ID is a number (no quotes)
- Restart bot: `Ctrl+C` then `python remote_starter.py`

### Analysis is slow
- Install PaddleOCR: `pip install paddleocr paddlepaddle`
- Use GPU version: `pip install paddlepaddle-gpu`

## 📁 Project Structure

```
kaggle-monitor/
├── remote_starter.py              # Always-on bot (listens for /check)
├── bot_oneshot.py                 # One-shot monitoring script
├── smart_kaggle_monitor.py        # Screenshot & analysis logic
├── config.yaml.example            # Configuration template
├── requirements.txt               # Python dependencies
├── worker/
│   ├── qwen_analyzer.py          # Qwen AI analyzer
│   ├── knowledge_base.py         # Pattern matching (100+ patterns)
│   └── analysis_prompt_template.txt
├── auto_start.bat                 # Auto-start script
├── start_hidden.vbs               # Hidden start script
└── docs/                          # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Qwen2-VL](https://github.com/QwenLM/Qwen-VL) - Vision-Language model
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Fast OCR
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot framework

## 📞 Support

- 📖 Read the [documentation](SETUP.md)
- 🐛 [Open an issue](https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant/issues)
- 💬 Check existing issues for solutions

---

Made with ❤️ for Kaggle enthusiasts

**Star ⭐ this repo if you find it helpful!**
