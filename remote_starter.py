"""Remote starter - Always-on lightweight bot that can start the monitoring bot."""
import asyncio
import subprocess
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yaml
import psutil
import os

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load config
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

# Track running process
monitoring_process = None


def check_auth(func):
    """Decorator to check if user is authorized."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != CONFIG['owner_user_id']:
            await update.message.reply_text("❌ Unauthorized. This bot is private.")
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        return await func(update, context)
    return wrapper


def is_monitoring_running():
    """Check if monitoring bot is already running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and 'python' in str(cmdline).lower() and 'bot_oneshot.py' in str(cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


@check_auth
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    help_text = """
🤖 Remote Kaggle Monitor Starter

This lightweight bot is always running and can start monitoring from your phone!

Commands:
/check - Start monitoring now (runs bot_oneshot.py)
/status - Check if monitoring is running
/help - Show this help

How it works:
1. This bot is always running (lightweight)
2. Send /check from your phone
3. It starts the monitoring bot on your PC
4. You get results in Telegram

Note: Each /check runs a fresh monitoring session.
"""
    await update.message.reply_text(help_text)


@check_auth
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check command - start monitoring."""
    global monitoring_process
    
    # Check if already running
    if is_monitoring_running():
        await update.message.reply_text(
            "⚠️ Monitoring is already running!\n\n"
            "Please wait for it to complete."
        )
        return
    
    await update.message.reply_text(
        "🚀 Starting monitoring on your PC...\n\n"
        "⏱️ This will take 5-20 minutes.\n"
        "(Using open-source AI model for accurate analysis)\n\n"
        "Results will be sent when ready!"
    )
    
    try:
        # Start bot_oneshot.py as subprocess
        logger.info("Starting bot_oneshot.py...")
        
        # Run in background
        if os.name == 'nt':  # Windows
            # Use CREATE_NEW_CONSOLE to run in separate window
            monitoring_process = subprocess.Popen(
                ['python', 'bot_oneshot.py'],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=Path(__file__).parent
            )
        else:  # Linux/Mac
            monitoring_process = subprocess.Popen(
                ['python', 'bot_oneshot.py'],
                cwd=Path(__file__).parent
            )
        
        logger.info(f"Monitoring started with PID: {monitoring_process.pid}")
        
        await update.message.reply_text(
            "✅ Monitoring started!\n\n"
            "Windows will flash on your PC as it checks.\n"
            "Results coming soon..."
        )
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error starting monitoring:\n{str(e)}\n\n"
            "Make sure bot_oneshot.py exists in the same folder."
        )


@check_auth
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    if is_monitoring_running():
        status_text = "✅ Monitoring is currently RUNNING\n\nPlease wait for results..."
    else:
        status_text = "❌ Monitoring is NOT running\n\nSend /check to start monitoring."
    
    await update.message.reply_text(status_text)


def main():
    """Start the remote starter bot."""
    logger.info("="*60)
    logger.info("Remote Starter Bot Starting")
    logger.info("="*60)
    logger.info("This lightweight bot can start monitoring from your phone!")
    logger.info(f"Owner user ID: {CONFIG['owner_user_id']}")
    logger.info("Send /check from Telegram to start monitoring")
    logger.info("="*60)
    
    # Create application
    application = Application.builder().token(CONFIG['bot_token']).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', start_command))
    application.add_handler(CommandHandler('check', check_command))
    application.add_handler(CommandHandler('status', status_command))
    
    # Start bot
    logger.info("Bot is ready! Waiting for commands from your phone...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
