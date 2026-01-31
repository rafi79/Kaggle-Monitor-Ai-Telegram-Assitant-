"""Test the enhanced knowledge base."""
from worker.knowledge_base import KaggleKnowledgeBase

print("="*60)
print("Testing Enhanced Knowledge Base")
print("="*60)
print()

# Initialize KB
kb = KaggleKnowledgeBase()

# Test cases
test_cases = [
    # EMPTY cases
    ("No sections detected in the right panel", "EMPTY"),
    ("No input attached to this notebook", "EMPTY"),
    ("Code cells visible but not executed", "EMPTY"),
    
    # RUNNING cases
    ("Epoch 3/10 - loss: 0.2750 - accuracy: 0.8523", "RUNNING"),
    ("[450/1500] 30% | < 44:23 | 0.02 it/s", "RUNNING"),
    ("Training... Step 37/100 - GPU: 95%", "RUNNING"),
    
    # COMPLETE cases
    ("Training complete! Final accuracy: 96.8%", "COMPLETE"),
    ("Epoch 10/10 - Model saved to /kaggle/working/model.pth", "COMPLETE"),
    ("100% | All epochs completed successfully", "COMPLETE"),
    
    # ERROR cases
    ("RuntimeError: CUDA out of memory", "ERROR"),
    ("FileNotFoundError: No such file or directory", "ERROR"),
    ("Training failed with exception: ValueError", "ERROR"),
]

print("Running test cases...")
print()

correct = 0
total = len(test_cases)

for text, expected_status in test_cases:
    result = kb.analyze_text(text)
    status = result['status']
    confidence = result['confidence']
    matched = result.get('matched_patterns', 0)
    
    is_correct = status == expected_status
    if is_correct:
        correct += 1
        symbol = "✅"
    else:
        symbol = "❌"
    
    print(f"{symbol} Expected: {expected_status:10} | Got: {status:10} | Confidence: {confidence:6} | Patterns: {matched}")
    print(f"   Text: {text[:70]}")
    print(f"   Details: {result['details'][:80]}")
    
    if result.get('metrics'):
        print(f"   Metrics: {result['metrics']}")
    
    print()

print("="*60)
print(f"Results: {correct}/{total} correct ({correct/total*100:.0f}%)")
print("="*60)
print()

# Show statistics
stats = kb.get_stats()
print("Knowledge Base Statistics:")
print(f"  Total analyses: {stats['total_analyses']}")
print(f"  Pattern matches: {stats['pattern_matches']}")
print(f"  AI fallbacks: {stats['ai_fallbacks']}")
if stats.get('pattern_match_rate'):
    print(f"  Pattern match rate: {stats['pattern_match_rate']}")
print()

# Show pattern counts
print("Pattern Counts:")
print(f"  EMPTY patterns: {len(kb.EMPTY_PATTERNS)}")
print(f"  RUNNING patterns: {len(kb.RUNNING_PATTERNS)}")
print(f"  COMPLETE patterns: {len(kb.COMPLETE_PATTERNS)}")
print(f"  ERROR patterns: {len(kb.ERROR_PATTERNS)}")
print(f"  METRIC patterns: {len(kb.TRAINING_METRICS)}")
print()

print("="*60)
print("Knowledge Base Test Complete!")
print("="*60)
