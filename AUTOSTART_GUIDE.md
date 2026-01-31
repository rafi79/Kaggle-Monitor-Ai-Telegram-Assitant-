# 🚀 Auto-Start Guide

## Make Bot Start Automatically When Windows Starts

### Option 1: Add to Startup Folder (Easiest)

1. **Press `Win + R`** to open Run dialog
2. **Type:** `shell:startup` and press Enter
3. **Copy `auto_start.bat`** to the Startup folder that opens
4. **Done!** Bot will start automatically when Windows boots

Now you never need to manually start the bot - just send `/check` from your phone anytime!

---

### Option 2: Task Scheduler (More Control)

1. **Open Task Scheduler** (search in Start menu)
2. **Click "Create Basic Task"**
3. **Name:** Kaggle Monitor Bot
4. **Trigger:** When I log on
5. **Action:** Start a program
6. **Program:** `python`
7. **Arguments:** `remote_starter.py`
8. **Start in:** `C:\Users\Rafi7\Downloads\Ai Training Agent\kaggle-monitor`
9. **Finish!**

---

### Option 3: Manual Start (Current Method)

Just run this once when you turn on your PC:
```bash
python remote_starter.py
```

Then minimize the window and forget about it!

---

## ✅ After Setup

Once the bot is auto-starting:

1. **Turn on your PC** → Bot starts automatically
2. **Open Telegram on phone** → Send `/check`
3. **Get results!** → No need to touch PC

---

## 🔍 Check if Bot is Running

**From your phone:**
```
/status
```

If bot responds, it's running! If no response, bot is not running.

---

## 💡 Pro Tip

Keep the bot running 24/7:
- Add to Startup folder (Option 1)
- Bot uses minimal resources when idle
- Only does heavy work when you send `/check`
- Check your notebooks anytime from anywhere!

---

## 🆘 Troubleshooting

### Bot doesn't auto-start
- Check Startup folder has `auto_start.bat`
- Make sure path in batch file is correct
- Try running `auto_start.bat` manually first

### Bot stops after a while
- Windows might close it to save resources
- Use Task Scheduler (Option 2) for more reliability
- Or just restart it when needed

---

## 🎯 Current Issue

Looking at your screenshot, the bot IS running and responding to `/check`, but it's showing "UNKNOWN" because:

1. ✅ Bot is running (it responded!)
2. ✅ Monitoring worked (it checked)
3. ❌ Detection failed (you're on "Your Work" page)

**Solution:** Open the actual notebook pages, not "Your Work"!

See [DETECTION_GUIDE.md](DETECTION_GUIDE.md) for details.
