"""One-shot Telegram bot - runs once, sends results, then stops."""
import asyncio
import json
import logging
import sys
import gc
import re
from pathlib import Path
from datetime import datetime
from telegram import Bot
import yaml

from smart_kaggle_monitor import SmartKaggleMonitor

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load config
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

STATE_FILE = Path('state.json')


def load_state():
    """Load monitoring state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        'last_run_time': None,
        'last_results': {},
        'run_count': 0
    }


def save_state(state):
    """Save monitoring state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def format_status_emoji(status: str) -> str:
    """Get emoji for status."""
    emoji_map = {
        'RUNNING': '✅',
        'STOPPED': '❌',
        'ERROR': '⚠️',
        'UNKNOWN': '❓'
    }
    return emoji_map.get(status, '❓')


async def send_results_to_telegram(bot: Bot, results: dict):
    """Send detailed monitoring results to Telegram."""
    chat_id = CONFIG['owner_user_id']
    run_id = results['run_id']
    
    # Build detailed summary message
    summary_lines = [f"🧠 Kaggle Monitor — Run #{run_id}\n"]
    
    for result in results['results']:
        browser_id = result['browser_id']
        status = result['status']
        emoji = format_status_emoji(status)
        
        # Extract notebook name from title
        title = result['window_title'].replace(' | Kaggle - Google Chrome', '')
        title = title.replace(' - Google Chrome', '')
        if len(title) > 60:
            title = title[:60] + '...'
        
        # Header with status
        summary_lines.append(f"\n{'='*40}")
        summary_lines.append(f"{browser_id}: {emoji} {status}")
        summary_lines.append(f"📓 {title}")
        summary_lines.append(f"📸 {result['screenshot_count']} screenshots analyzed")
        
        # Detailed information based on status
        details = result.get('details', '')
        
        if status == 'EMPTY':
            summary_lines.append(f"\n⚪ NOTEBOOK IS EMPTY")
            summary_lines.append(f"• Code is visible but NOT executed")
            summary_lines.append(f"• No training output or results found")
            summary_lines.append(f"• Click 'Run All' in Kaggle to start")
            
            # Show specific empty indicators if available
            if 'No sections detected' in details:
                summary_lines.append(f"• Right panel shows 'No sections detected'")
            if 'No input attached' in details:
                summary_lines.append(f"• Message: 'No input attached'")
            if 'no output' in details.lower():
                summary_lines.append(f"• No output area visible below code")
        
        elif status == 'RUNNING':
            summary_lines.append(f"\n🟢 TRAINING IS RUNNING")
            
            # Extract training metrics from details
            if 'Epoch' in details:
                # Find epoch info
                import re
                epoch_match = re.search(r'Epoch\s+(\d+)/(\d+)', details)
                if epoch_match:
                    current, total = epoch_match.groups()
                    progress = int(current) / int(total) * 100
                    summary_lines.append(f"• Progress: Epoch {current}/{total} ({progress:.0f}%)")
            
            if 'loss' in details.lower():
                loss_match = re.search(r'loss[:\s]+(\d+\.\d+)', details, re.IGNORECASE)
                if loss_match:
                    summary_lines.append(f"• Loss: {loss_match.group(1)}")
            
            if 'accuracy' in details.lower():
                acc_match = re.search(r'accuracy[:\s]+(\d+\.\d+)', details, re.IGNORECASE)
                if acc_match:
                    summary_lines.append(f"• Accuracy: {acc_match.group(1)}")
            
            # Show raw details if no metrics extracted
            if len(summary_lines) == len([l for l in summary_lines if browser_id in l]) + 5:
                # No metrics found, show raw details
                detail_preview = details[:200]
                if len(details) > 200:
                    detail_preview += '...'
                summary_lines.append(f"• Details: {detail_preview}")
        
        elif status == 'COMPLETE':
            summary_lines.append(f"\n✅ TRAINING COMPLETED")
            summary_lines.append(f"• Training finished successfully")
            
            # Extract final metrics
            if 'accuracy' in details.lower():
                acc_match = re.search(r'accuracy[:\s]+(\d+\.\d+)', details, re.IGNORECASE)
                if acc_match:
                    summary_lines.append(f"• Final Accuracy: {acc_match.group(1)}")
            
            if 'loss' in details.lower():
                loss_match = re.search(r'loss[:\s]+(\d+\.\d+)', details, re.IGNORECASE)
                if loss_match:
                    summary_lines.append(f"• Final Loss: {loss_match.group(1)}")
            
            if 'saved' in details.lower():
                summary_lines.append(f"• Model saved successfully")
            
            # Show completion details
            detail_preview = details[:200]
            if len(details) > 200:
                detail_preview += '...'
            summary_lines.append(f"• Details: {detail_preview}")
        
        elif status == 'ERROR':
            summary_lines.append(f"\n❌ ERROR DETECTED")
            summary_lines.append(f"• Training failed with error")
            
            # Show error details
            error_preview = details[:250]
            if len(details) > 250:
                error_preview += '...'
            summary_lines.append(f"• Error: {error_preview}")
        
        else:  # UNKNOWN
            summary_lines.append(f"\n❓ STATUS UNKNOWN")
            detail_preview = details[:200]
            if len(details) > 200:
                detail_preview += '...'
            summary_lines.append(f"• Details: {detail_preview}")
    
    # Add footer
    summary_lines.append(f"\n{'='*40}")
    summary_lines.append(f"✅ Analysis complete!")
    summary_lines.append(f"📁 Screenshots saved in: screenshots/{run_id}/")
    
    summary = "\n".join(summary_lines)
    
    # Split message if too long (Telegram limit is 4096 chars)
    if len(summary) > 4000:
        # Send in chunks
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in summary_lines:
            line_length = len(line) + 1  # +1 for newline
            if current_length + line_length > 4000:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        # Send chunks
        for i, chunk in enumerate(chunks):
            await bot.send_message(chat_id=chat_id, text=chunk)
            if i < len(chunks) - 1:
                await asyncio.sleep(0.5)  # Small delay between messages
    else:
        await bot.send_message(chat_id=chat_id, text=summary)
    
    # Send first screenshot of each browser as visual reference
    for result in results['results']:
        if result['screenshots']:
            first_screenshot = result['screenshots'][0]
            if Path(first_screenshot).exists():
                try:
                    with open(first_screenshot, 'rb') as photo:
                        caption = f"{result['browser_id']} - {result['status']} - {result['window_title'][:50]}"
                        await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
                except Exception as e:
                    logger.error(f"Error sending screenshot: {e}")


async def main():
    """Run monitoring once and send to Telegram."""
    logger.info("="*60)
    logger.info("One-Shot Kaggle Monitor Starting")
    logger.info("="*60)
    
    # Create bot
    bot = Bot(token=CONFIG['bot_token'])
    
    # Send starting message
    await bot.send_message(
        chat_id=CONFIG['owner_user_id'],
        text="🔍 Starting Kaggle monitoring...\n\nWindows will flash as I check them."
    )
    
    try:
        # Run monitoring
        monitor = SmartKaggleMonitor()
        results = monitor.run_check()
        
        if not results['results']:
            await bot.send_message(
                chat_id=CONFIG['owner_user_id'],
                text="❌ No Kaggle windows found!\n\n"
                     "Make sure:\n"
                     "1. Chrome is open\n"
                     "2. You have Kaggle notebook tabs open\n"
                     "3. Windows are not minimized"
            )
            return
        
        # Update state
        state = load_state()
        state['last_run_time'] = results['timestamp']
        state['last_results'] = results
        state['run_count'] += 1
        save_state(state)
        
        # Send results
        await send_results_to_telegram(bot, results)
        
        logger.info("✅ Results sent to Telegram")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await bot.send_message(
            chat_id=CONFIG['owner_user_id'],
            text=f"❌ Error during monitoring:\n{str(e)}"
        )
    finally:
        # Force cleanup
        logger.info("Cleaning up resources...")
        
        # Clean up CUDA if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
        
        # Force garbage collection
        gc.collect()
        
        logger.info("="*60)
        logger.info("Monitoring Complete - Bot Stopping")
        logger.info("="*60)
        
        # Give a moment for final cleanup
        await asyncio.sleep(0.5)


if __name__ == '__main__':
    # Create directories
    Path('logs').mkdir(exist_ok=True)
    Path('screenshots').mkdir(exist_ok=True)
    
    try:
        # Run once and exit
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        logger.info("Exiting...")
        sys.exit(0)
