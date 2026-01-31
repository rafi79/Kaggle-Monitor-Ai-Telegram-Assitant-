"""Smart Kaggle monitor that scrolls pages and uses ShowUI AI for detection."""
import pyautogui
import pygetwindow as gw
from PIL import Image
import logging
from pathlib import Path
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartKaggleMonitor:
    """Smart monitor that scrolls Kaggle pages and uses AI detection."""
    
    def __init__(self):
        self.screenshot_dir = Path('screenshots')
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def find_kaggle_windows(self):
        """Find only Kaggle browser windows."""
        all_windows = gw.getAllWindows()
        
        kaggle_windows = []
        for window in all_windows:
            title = window.title.lower()
            # Only Kaggle windows
            if 'kaggle' in title and 'chrome' in title:
                if window.width > 400 and window.height > 300:
                    kaggle_windows.append(window)
                    logger.info(f"Found Kaggle window: {window.title}")
        
        return kaggle_windows
    
    def activate_window(self, window):
        """Bring window to front."""
        try:
            # Try to restore if minimized
            try:
                if window.isMinimized:
                    window.restore()
                    time.sleep(0.3)
            except:
                pass
            
            # Try to activate
            try:
                window.activate()
            except:
                # If activate fails, try clicking on it
                try:
                    pyautogui.click(window.left + 100, window.top + 50)
                except:
                    pass
            
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.warning(f"Window activation issue (continuing anyway): {e}")
            return True  # Continue anyway
    
    def take_full_page_screenshots(self, window, output_dir, browser_id):
        """
        Take screenshots in batches of 10, scrolling from TOP to BOTTOM.
        Uses smart duplicate detection to avoid taking same screenshot twice.
        Stops if page is empty or reaches bottom.
        Maximum 60 screenshots per window.
        """
        screenshots = []
        
        # Activate window
        if not self.activate_window(window):
            return screenshots
        
        # Click in the middle of window to focus
        center_x = window.left + window.width // 2
        center_y = window.top + window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        # Scroll to VERY TOP first
        logger.info(f"📍 Scrolling to TOP of page...")
        for _ in range(5):
            pyautogui.press('home')
            time.sleep(0.2)
        time.sleep(1)
        
        # Take screenshots in batches
        screenshot_count = 0
        max_screenshots = 200  # High limit - will stop when reaching bottom
        batch_size = 10
        same_screenshot_count = 0
        last_screenshot_hash = None
        seen_hashes = set()  # Track all seen screenshots to avoid duplicates
        
        logger.info(f"📸 Starting smart screenshot capture (batches of {batch_size})...")
        logger.info(f"🔍 Will scroll until reaching bottom (duplicate detection enabled)")
        
        while True:  # No hard limit - scroll until bottom
            # Take screenshot
            screenshot_path = output_dir / f"{browser_id}_ss_{screenshot_count:03d}.png"
            
            try:
                screenshot = pyautogui.screenshot(region=(
                    window.left,
                    window.top,
                    window.width,
                    window.height
                ))
                
                # Calculate hash to detect duplicates
                import hashlib
                screenshot_hash = hashlib.md5(screenshot.tobytes()).hexdigest()
                
                # Check if this is a duplicate of ANY previous screenshot
                if screenshot_hash in seen_hashes:
                    same_screenshot_count += 1
                    logger.info(f"⚠️ Duplicate screenshot detected ({same_screenshot_count}/5) - skipping")
                    
                    # If we see 5 duplicates in a row, we've truly reached the bottom
                    if same_screenshot_count >= 5:
                        logger.info(f"✅ Reached BOTTOM (5 duplicate screenshots in a row)")
                        break
                    
                    # Try scrolling more aggressively
                    pyautogui.press('pagedown')
                    pyautogui.press('pagedown')  # Double scroll
                    time.sleep(0.8)
                    continue
                
                # New unique screenshot - save it
                screenshot.save(screenshot_path)
                screenshots.append(str(screenshot_path))
                seen_hashes.add(screenshot_hash)
                screenshot_count += 1
                same_screenshot_count = 0  # Reset duplicate counter
                
                logger.info(f"📸 Screenshot {screenshot_count}: {screenshot_path.name} ✓")
                
                last_screenshot_hash = screenshot_hash
                
                # Check if we completed a batch
                if screenshot_count % batch_size == 0:
                    logger.info(f"✅ Completed batch {screenshot_count // batch_size} ({batch_size} unique screenshots)")
                
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")
                break
            
            # Scroll DOWN using Page Down
            pyautogui.press('pagedown')
            time.sleep(0.7)  # Wait for page to scroll
        
        logger.info(f"✅ Captured {len(screenshots)} unique screenshots (skipped {screenshot_count - len(screenshots)} duplicates)")
        return screenshots
    
    def detect_training_status_showui(self, screenshot_paths):
        """Use Qwen to analyze ALL screenshots and create comprehensive detailed summary."""
        analyzer = None
        try:
            from worker.qwen_analyzer import QwenAnalyzer
            
            analyzer = QwenAnalyzer()
            
            logger.info(f"🧠 Analyzing ALL {len(screenshot_paths)} screenshots with Qwen...")
            logger.info(f"⏱️ This will take 5-20 minutes (open-source AI model)")
            
            # Analyze ALL screenshots in batches of 10
            batch_size = 10
            all_analyses = []
            
            for i in range(0, len(screenshot_paths), batch_size):
                batch = screenshot_paths[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(screenshot_paths) + batch_size - 1) // batch_size
                
                logger.info(f"📦 Analyzing batch {batch_num}/{total_batches} ({len(batch)} screenshots)...")
                
                batch_analyses = []
                for j, screenshot_path in enumerate(batch):
                    screenshot_num = i + j + 1
                    analysis = analyzer.analyze_screenshot(screenshot_path, screenshot_num, len(screenshot_paths))
                    batch_analyses.append(analysis)
                    all_analyses.append(analysis)
                
                # Log batch results
                content_count = sum(1 for a in batch_analyses if a.get('has_content', False))
                logger.info(f"Batch {batch_num}: {content_count}/{len(batch)} screenshots have content")
                
                # Continue analyzing ALL batches (don't stop early)
                # We need to see the full picture before making conclusions
            
            logger.info(f"✅ Analyzed ALL {len(all_analyses)} screenshots")
            
            # Create final comprehensive summary
            summary = analyzer.create_summary(all_analyses)
            
            logger.info(f"📊 Final Summary: {summary['summary']}")
            logger.info(f"📝 Detailed Analysis:\n{summary.get('details', '')}")
            
            # Return comprehensive details
            return summary['status'], 'high', summary.get('details', summary['summary'])
                
        except Exception as e:
            logger.warning(f"Qwen analysis failed: {e}")
            return self.detect_training_status_simple(screenshot_paths)
        finally:
            # Clean up Qwen resources
            if analyzer is not None:
                try:
                    analyzer.cleanup()
                except:
                    pass
    
    def detect_training_status_simple(self, screenshot_paths):
        """Simple OCR-based detection."""
        try:
            from simple_detector import detect_from_screenshots
            return detect_from_screenshots(screenshot_paths)
        except Exception as e:
            logger.warning(f"Simple detection failed: {e}")
            return 'UNKNOWN', 'low', f'Detection failed: {str(e)}'
    
    def run_check(self):
        """Run monitoring check on all Kaggle windows."""
        run_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        run_dir = self.screenshot_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        logger.info("="*60)
        logger.info("Finding Kaggle windows...")
        kaggle_windows = self.find_kaggle_windows()
        
        if not kaggle_windows:
            logger.warning("No Kaggle windows found!")
            logger.info("Make sure you have Kaggle tabs open in Chrome")
            return {
                'run_id': run_id,
                'timestamp': datetime.now().isoformat(),
                'results': []
            }
        
        logger.info(f"Found {len(kaggle_windows)} Kaggle window(s)")
        logger.info("="*60)
        
        results = []
        for i, window in enumerate(kaggle_windows):
            browser_id = chr(65 + i)  # A, B, C, D...
            logger.info(f"\n[Browser {browser_id}] Processing: {window.title}")
            
            # Take multiple screenshots while scrolling
            logger.info(f"[Browser {browser_id}] Taking full-page screenshots...")
            screenshot_paths = self.take_full_page_screenshots(window, run_dir, browser_id)
            
            if not screenshot_paths:
                logger.warning(f"[Browser {browser_id}] No screenshots captured")
                continue
            
            logger.info(f"[Browser {browser_id}] Captured {len(screenshot_paths)} screenshots")
            
            # Detect training status using AI
            logger.info(f"[Browser {browser_id}] Analyzing screenshots with AI...")
            status, confidence, details = self.detect_training_status_showui(screenshot_paths)
            
            logger.info(f"[Browser {browser_id}] Status: {status} (confidence: {confidence})")
            logger.info(f"[Browser {browser_id}] Details: {details}")
            
            results.append({
                'browser_id': browser_id,
                'window_title': window.title,
                'screenshots': screenshot_paths,
                'screenshot_count': len(screenshot_paths),
                'status': status,
                'confidence': confidence,
                'details': details
            })
        
        return {
            'run_id': run_id,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }


def main():
    """Test the smart monitor."""
    print("="*60)
    print("Smart Kaggle Monitor with AI Detection")
    print("="*60)
    print()
    
    # Check if ShowUI is available
    try:
        from worker.showui import ShowUIDetector
        print("✅ ShowUI AI available - will use advanced detection")
    except:
        print("⚠️  ShowUI not available - will use simple detection")
        print("   Install with: pip install transformers torch qwen-vl-utils")
    
    print()
    print("Instructions:")
    print("1. Make sure Kaggle tabs are open in Chrome")
    print("2. Windows will flash as they come to front")
    print("3. Each page will be scrolled and captured")
    print("4. AI will analyze all screenshots")
    print()
    input("Press Enter to start monitoring...")
    print()
    
    monitor = SmartKaggleMonitor()
    results = monitor.run_check()
    
    print("\n" + "="*60)
    print("MONITORING RESULTS")
    print("="*60)
    print(f"Run ID: {results['run_id']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Kaggle windows checked: {len(results['results'])}")
    print()
    
    if not results['results']:
        print("⚠️  No Kaggle windows found!")
        print("\nMake sure:")
        print("1. Chrome is open")
        print("2. You have Kaggle notebook tabs open")
        print("3. Windows are not minimized")
    else:
        for result in results['results']:
            print(f"{'='*60}")
            print(f"Browser {result['browser_id']}")
            print(f"{'='*60}")
            print(f"Title: {result['window_title']}")
            print(f"Screenshots taken: {result['screenshot_count']}")
            print(f"Status: {result['status']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Details: {result['details']}")
            print(f"Screenshots:")
            for screenshot in result['screenshots']:
                print(f"  - {screenshot}")
            print()
        
        print(f"✅ All screenshots saved in: screenshots/{results['run_id']}/")
        print()
        
        # Summary
        print("="*60)
        print("SUMMARY")
        print("="*60)
        for result in results['results']:
            status_emoji = {
                'RUNNING': '✅',
                'STOPPED': '❌',
                'ERROR': '⚠️',
                'UNKNOWN': '❓'
            }.get(result['status'], '❓')
            
            print(f"{result['browser_id']}: {status_emoji} {result['status']}")


if __name__ == '__main__':
    main()
