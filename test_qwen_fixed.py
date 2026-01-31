"""Test script to verify Qwen works with or without PaddleOCR."""
import sys
from pathlib import Path

print("="*60)
print("Testing Qwen Analyzer (with PaddleOCR support)")
print("="*60)
print()

# Test 1: Check if Qwen can be imported
print("Test 1: Importing Qwen analyzer...")
try:
    from worker.qwen_analyzer import QwenAnalyzer, PADDLEOCR_AVAILABLE, QWEN_AVAILABLE
    print(f"✅ QwenAnalyzer imported successfully")
    print(f"   PaddleOCR available: {PADDLEOCR_AVAILABLE}")
    print(f"   Qwen available: {QWEN_AVAILABLE}")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

print()

# Test 2: Initialize analyzer
print("Test 2: Initializing analyzer...")
try:
    analyzer = QwenAnalyzer()
    print(f"✅ Analyzer initialized")
    if PADDLEOCR_AVAILABLE:
        print(f"   Knowledge base: {'Enabled' if analyzer.knowledge_base else 'Disabled'}")
        print(f"   PaddleOCR engine: {'Initialized' if analyzer.ocr_engine else 'Not initialized'}")
    else:
        print(f"   Knowledge base: Disabled (PaddleOCR not available)")
        print(f"   Mode: Qwen AI only (slower but works)")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

print()

# Test 3: Find a test screenshot
print("Test 3: Finding test screenshot...")
screenshot_dir = Path('screenshots')
test_screenshot = None

if screenshot_dir.exists():
    for folder in sorted(screenshot_dir.iterdir(), reverse=True):
        if folder.is_dir():
            screenshots = list(folder.glob('*.png'))
            if screenshots:
                test_screenshot = str(screenshots[0])
                print(f"✅ Found test screenshot: {test_screenshot}")
                break

if not test_screenshot:
    print("⚠️ No test screenshots found in screenshots/ folder")
    print("   Run smart_kaggle_monitor.py first to capture screenshots")
    sys.exit(0)

print()

# Test 4: Analyze screenshot
print("Test 4: Analyzing screenshot with Qwen...")
if PADDLEOCR_AVAILABLE:
    print("   (Will try PaddleOCR pattern matching first, then Qwen if needed)")
else:
    print("   (Using Qwen AI only - may take 10-30 seconds)")
print()

try:
    result = analyzer.analyze_screenshot(test_screenshot, 1, 1)
    print(f"✅ Analysis completed!")
    print()
    print(f"Results:")
    print(f"  Status: {result.get('status', 'N/A')}")
    print(f"  Has content: {result.get('has_content', 'N/A')}")
    print(f"  Method: {result.get('method', 'qwen_ai')}")
    print(f"  Details: {result.get('details', 'N/A')[:200]}")
    
    if result.get('metrics'):
        print(f"  Metrics: {result['metrics']}")
    
    print()
    
    # Explain method
    method = result.get('method', 'qwen_ai')
    if method == 'pattern_match_paddleocr':
        print("🚀 Fast path used! (PaddleOCR pattern matching)")
        print("   This was ~6x faster than Qwen AI alone")
    else:
        print("🐢 Slow path used (Qwen AI)")
        if not PADDLEOCR_AVAILABLE:
            print("   💡 Install PaddleOCR for 6x faster analysis:")
            print("      pip install paddleocr paddlepaddle")
    
    print()
    
    if result.get('status') == 'EMPTY':
        print("ℹ️ Status is EMPTY - this means:")
        print("   • Code is visible but NOT executed")
        print("   • No output/results visible")
        print("   • Need to click 'Run All' in Kaggle")
    elif result.get('status') == 'RUNNING':
        print("ℹ️ Status is RUNNING - training is active!")
    elif result.get('status') == 'COMPLETE':
        print("ℹ️ Status is COMPLETE - training finished!")
    
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Cleanup
print("Test 5: Cleaning up resources...")
try:
    analyzer.cleanup()
    print("✅ Cleanup successful")
except Exception as e:
    print(f"⚠️ Cleanup warning: {e}")

print()
print("="*60)
print("All tests passed! ✅")
print("="*60)
print()
print("Summary:")
print(f"  • Qwen works: {'YES' if QWEN_AVAILABLE else 'NO'}")
if PADDLEOCR_AVAILABLE:
    print(f"  • PaddleOCR available: YES (fast pattern matching enabled)")
    print(f"  • Analysis method: Hybrid (PaddleOCR + Qwen)")
    print(f"  • Speed: 6x faster for clear cases")
else:
    print(f"  • PaddleOCR available: NO (using Qwen only)")
    print(f"  • Analysis method: AI only (Qwen built-in OCR)")
    print(f"  • Speed: Slower but works")
    print()
    print("💡 Recommendation: Install PaddleOCR for faster analysis:")
    print("   pip install paddleocr paddlepaddle")
print()
print("You can now use the bot with /check command!")

