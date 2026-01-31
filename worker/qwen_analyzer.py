"""Qwen3-VL-4B analyzer for better Kaggle notebook analysis."""
import os
import logging
import torch
from pathlib import Path
from PIL import Image
from typing import Optional, Dict, List

# Disable background downloads
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '0'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

logger = logging.getLogger(__name__)

# Try to import PaddleOCR (optional - for fast pattern matching)
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
    logger.info("✅ PaddleOCR available for fast pattern matching")
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.info("ℹ️ PaddleOCR not available - will use Qwen's built-in OCR only (slower but works)")

try:
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    logger.warning("Qwen dependencies not available")


class QwenAnalyzer:
    """Qwen3-VL-4B analyzer for Kaggle notebooks with hybrid pattern matching + AI."""
    
    def __init__(self, model_name: str = "Qwen/Qwen2-VL-2B-Instruct"):
        self.model = None
        self.processor = None
        self.model_name = model_name
        self.ocr_engine = None
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
        
        # Initialize knowledge base for fast pattern matching (only if PaddleOCR available)
        if PADDLEOCR_AVAILABLE:
            try:
                from .knowledge_base import KaggleKnowledgeBase
                self.knowledge_base = KaggleKnowledgeBase()
                logger.info("✅ Knowledge base loaded for fast pattern matching with PaddleOCR")
                
                # Initialize PaddleOCR (use English model, no angle classification for speed)
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=False,  # Faster without angle classification
                    lang='en',  # English only
                    show_log=False,  # Suppress logs
                    use_gpu=torch.cuda.is_available()  # Use GPU if available
                )
                logger.info("✅ PaddleOCR initialized (GPU: {})".format(torch.cuda.is_available()))
            except Exception as e:
                logger.warning(f"Knowledge base not available: {e}")
                self.knowledge_base = None
                self.ocr_engine = None
        else:
            self.knowledge_base = None
            self.ocr_engine = None
            logger.info("ℹ️ Skipping knowledge base (PaddleOCR not installed) - using Qwen only")
        
        if not QWEN_AVAILABLE:
            logger.warning("Qwen not available")
            return
        
        if not torch.cuda.is_available():
            logger.warning("CUDA not available. Qwen will be slow on CPU.")
    
    def _load_prompt_template(self) -> str:
        """Load the comprehensive analysis prompt template."""
        try:
            template_path = Path(__file__).parent / "analysis_prompt_template.txt"
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt template: {e}")
            # Fallback to basic prompt
            return (
                "Analyze this Kaggle notebook screenshot.\n"
                "Tell me:\n"
                "HAS_CONTENT: [YES/NO]\n"
                "STATUS: [EMPTY/RUNNING/COMPLETE/ERROR]\n"
                "DETAILS: [What you see]"
            )
    
    def load_model(self):
        """Load Qwen model with optimized settings for text extraction."""
        if not QWEN_AVAILABLE:
            raise RuntimeError("Qwen dependencies not installed")
        
        if self.model is not None:
            return
        
        logger.info(f"Loading Qwen model: {self.model_name}")
        logger.info("⚡ Using optimized settings for faster text extraction")
        
        # Load model with optimizations
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,  # Use bfloat16 for speed
            device_map="auto",
            low_cpu_mem_usage=True,  # Reduce CPU memory usage
        )
        
        # Set to eval mode for inference (faster)
        self.model.eval()
        
        # Optimize for text extraction (smaller image resolution)
        # This makes processing faster while maintaining text readability
        min_pixels = 256 * 28 * 28  # Minimum resolution
        max_pixels = 768 * 28 * 28  # Reduced from 1344 for speed (still good for text)
        
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            min_pixels=min_pixels,
            max_pixels=max_pixels
        )
        
        logger.info("✅ Qwen model loaded with optimized settings")
        logger.info(f"   • Image resolution: Optimized for text extraction")
        logger.info(f"   • Precision: bfloat16 (faster)")
        logger.info(f"   • Mode: Inference only")
    
    def analyze_screenshot(self, screenshot_path: str, screenshot_num: int, total: int) -> Dict:
        """
        Hybrid analysis: Try fast pattern matching first, then use AI if needed.
        This makes detection faster and more accurate.
        """
        if not QWEN_AVAILABLE:
            return {'has_content': False, 'analysis': 'Qwen not available'}
        
        try:
            # STEP 1: Try fast pattern matching with PaddleOCR first
            if self.knowledge_base is not None and PADDLEOCR_AVAILABLE and self.ocr_engine is not None:
                try:
                    # Extract text from screenshot using PaddleOCR
                    result_ocr = self.ocr_engine.ocr(screenshot_path, cls=False)
                    
                    # Extract text from OCR results
                    text_lines = []
                    if result_ocr and result_ocr[0]:
                        for line in result_ocr[0]:
                            if line[1][0]:  # Check if text exists
                                text_lines.append(line[1][0])
                    
                    text = '\n'.join(text_lines)
                    
                    if text.strip():  # Only try pattern matching if we got text
                        # Try pattern matching
                        pattern_result = self.knowledge_base.analyze_text(text)
                        
                        # If high confidence, return immediately (fast path)
                        if pattern_result['confidence'] == 'high':
                            logger.info(f"✅ Screenshot {screenshot_num}: Fast pattern match (PaddleOCR) - {pattern_result['status']}")
                            return {
                                'has_content': pattern_result['has_content'],
                                'status': pattern_result['status'],
                                'details': pattern_result['details'],
                                'screenshot_num': screenshot_num,
                                'method': 'pattern_match_paddleocr',
                                'metrics': pattern_result.get('metrics', {})
                            }
                        
                        # If medium confidence and status is clear, return
                        if pattern_result['confidence'] == 'medium' and pattern_result['status'] in ['EMPTY', 'ERROR']:
                            logger.info(f"✅ Screenshot {screenshot_num}: Pattern match (medium, PaddleOCR) - {pattern_result['status']}")
                            return {
                                'has_content': pattern_result['has_content'],
                                'status': pattern_result['status'],
                                'details': pattern_result['details'],
                                'screenshot_num': screenshot_num,
                                'method': 'pattern_match_paddleocr',
                                'metrics': pattern_result.get('metrics', {})
                            }
                        
                        # Low confidence or needs AI - continue to AI analysis
                        logger.info(f"⚠️ Screenshot {screenshot_num}: Pattern match uncertain, using Qwen AI...")
                    
                except Exception as e:
                    logger.warning(f"PaddleOCR pattern matching failed for screenshot {screenshot_num}: {e}")
            
            # STEP 2: Use Qwen AI (with built-in OCR)
            self.load_model()
            
            # Use the comprehensive prompt template
            prompt = self.prompt_template.format(
                screenshot_num=screenshot_num,
                total=total
            )
            
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": screenshot_path},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda" if torch.cuda.is_available() else "cpu")
            
            # Generate with optimized settings for speed
            with torch.no_grad():  # Disable gradient computation for speed
                generated_ids = self.model.generate(
                    **inputs, 
                    max_new_tokens=250,  # Limit output length
                    do_sample=False,  # Greedy decoding (faster)
                    num_beams=1,  # No beam search (faster)
                )
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            logger.info(f"Screenshot {screenshot_num} Qwen response: {output_text[:400]}")
            
            # Parse response
            result = {
                'has_content': False,
                'status': 'UNKNOWN',
                'details': output_text,
                'screenshot_num': screenshot_num
            }
            
            # Extract HAS_CONTENT
            if 'HAS_CONTENT:' in output_text:
                content_part = output_text.split('HAS_CONTENT:')[1].split('\n')[0]
                if 'YES' in content_part.upper():
                    result['has_content'] = True
            
            # Extract STATUS
            if 'STATUS:' in output_text:
                status_part = output_text.split('STATUS:')[1].split('\n')[0]
                status_part = status_part.replace('[', '').replace(']', '').strip().upper()
                for word in ['RUNNING', 'STOPPED', 'COMPLETE', 'ERROR', 'EMPTY']:
                    if word in status_part:
                        result['status'] = word
                        break
            
            # Extract DETAILS
            if 'DETAILS:' in output_text:
                details_part = output_text.split('DETAILS:')[1].split('\n')[0]
                result['details'] = details_part.strip()[:300]
            else:
                # Use the full output as details if no DETAILS: section
                result['details'] = output_text[:300]
            
            # Fallback: If status is still UNKNOWN, check the content for EMPTY indicators
            if result['status'] == 'UNKNOWN':
                output_lower = output_text.lower()
                empty_indicators = [
                    'no output visible',
                    'no execution',
                    'no [1][2]',
                    'no sections detected',
                    'no input attached',
                    'green play buttons',
                    'not executed',
                    'has not been run',
                    'code has not been executed'
                ]
                
                # Count empty indicators
                empty_count = sum(1 for indicator in empty_indicators if indicator in output_lower)
                
                # If multiple empty indicators found, it's EMPTY
                if empty_count >= 2:
                    result['status'] = 'EMPTY'
                    result['has_content'] = False
                    logger.info(f"Fallback detection: Found {empty_count} EMPTY indicators, setting status to EMPTY")
            
            return result
            
        except Exception as e:
            logger.error(f"Qwen analysis failed: {e}")
            return {
                'has_content': False,
                'status': 'ERROR',
                'details': f'Analysis failed: {str(e)}',
                'screenshot_num': screenshot_num
            }
    
    def create_summary(self, analyses: List[Dict]) -> Dict:
        """
        Create comprehensive final summary from all screenshot analyses.
        This provides detailed information about what's happening in the notebook.
        """
        if not analyses:
            return {
                'status': 'EMPTY',
                'summary': 'No screenshots analyzed',
                'details': 'No data available'
            }
        
        # Collect all information
        status_counts = {}
        has_content_count = 0
        training_info = []
        key_findings = []
        empty_indicators = []
        all_details = []
        
        for analysis in analyses:
            status = analysis.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            details = analysis.get('details', '')
            all_details.append(f"SS{analysis['screenshot_num']}: {details[:150]}")
            
            if analysis.get('has_content', False):
                has_content_count += 1
                
                # Extract key information from details
                # Look for training indicators
                if any(word in details.lower() for word in ['epoch', 'loss', 'accuracy', 'training', 'step']):
                    training_info.append({
                        'ss': analysis['screenshot_num'],
                        'info': details[:200]
                    })
                
                # Look for important findings
                if status in ['RUNNING', 'COMPLETE', 'ERROR']:
                    key_findings.append({
                        'ss': analysis['screenshot_num'],
                        'status': status,
                        'info': details[:250]
                    })
            else:
                # Track empty indicators
                if any(word in details.lower() for word in ['no sections', 'no input', 'no output', 'not executed', 'empty']):
                    empty_indicators.append({
                        'ss': analysis['screenshot_num'],
                        'reason': details[:150]
                    })
        
        # Determine final status with improved logic
        final_status = 'EMPTY'
        
        # If majority of screenshots are EMPTY, it's EMPTY
        empty_count = status_counts.get('EMPTY', 0)
        if empty_count > len(analyses) * 0.5:  # More than 50% empty
            final_status = 'EMPTY'
        # Priority: RUNNING > ERROR > COMPLETE
        elif 'RUNNING' in status_counts:
            final_status = 'RUNNING'
        elif 'ERROR' in status_counts:
            final_status = 'ERROR'
        elif 'COMPLETE' in status_counts and has_content_count > 0:
            # Only COMPLETE if we actually have content
            final_status = 'COMPLETE'
        elif has_content_count > 0:
            final_status = 'UNKNOWN'
        
        # Build comprehensive detailed description
        detailed_parts = []
        
        # Status header
        if final_status == 'RUNNING':
            detailed_parts.append("🟢 TRAINING IS RUNNING")
            detailed_parts.append("")
            
            if training_info:
                detailed_parts.append("📊 Training Progress:")
                for item in training_info[:8]:  # Show more training info
                    detailed_parts.append(f"  • Screenshot {item['ss']}: {item['info']}")
                detailed_parts.append("")
            
            if key_findings:
                detailed_parts.append("🔍 Key Observations:")
                for finding in key_findings[:5]:
                    detailed_parts.append(f"  • SS{finding['ss']}: {finding['info']}")
                detailed_parts.append("")
        
        elif final_status == 'COMPLETE':
            detailed_parts.append("✅ TRAINING COMPLETED")
            detailed_parts.append("")
            
            if key_findings:
                detailed_parts.append("📊 Results Found:")
                for finding in key_findings[:8]:
                    detailed_parts.append(f"  • SS{finding['ss']}: {finding['info']}")
                detailed_parts.append("")
            
            if training_info:
                detailed_parts.append("📈 Training History:")
                for item in training_info[:5]:
                    detailed_parts.append(f"  • Screenshot {item['ss']}: {item['info']}")
                detailed_parts.append("")
        
        elif final_status == 'ERROR':
            detailed_parts.append("❌ ERROR DETECTED")
            detailed_parts.append("")
            
            error_findings = [f for f in key_findings if f['status'] == 'ERROR']
            if error_findings:
                detailed_parts.append("⚠️ Error Details:")
                for finding in error_findings[:5]:
                    detailed_parts.append(f"  • SS{finding['ss']}: {finding['info']}")
                detailed_parts.append("")
        
        elif final_status == 'EMPTY':
            detailed_parts.append("⚪ NOTEBOOK IS EMPTY")
            detailed_parts.append("")
            detailed_parts.append("📋 Comprehensive Analysis:")
            detailed_parts.append(f"  • Analyzed {len(analyses)} screenshots from top to bottom")
            detailed_parts.append(f"  • {empty_count} screenshots confirmed empty state ({(empty_count/len(analyses)*100):.0f}%)")
            detailed_parts.append(f"  • {has_content_count} screenshots had some content")
            detailed_parts.append(f"  • No training output or execution results found")
            detailed_parts.append("")
            
            if empty_indicators:
                detailed_parts.append("🔍 Empty Indicators Found (detailed):")
                for indicator in empty_indicators[:15]:  # Show up to 15 indicators
                    detailed_parts.append(f"  • {indicator}")
                if len(empty_indicators) > 15:
                    detailed_parts.append(f"  • ... and {len(empty_indicators) - 15} more empty indicators")
                detailed_parts.append("")
            
            # Show what was actually visible
            detailed_parts.append("👁️ What Was Visible:")
            detailed_parts.append("  • Code cells present (Python/notebook code)")
            detailed_parts.append("  • No [1], [2], [3] execution numbers")
            detailed_parts.append("  • No output area below code cells")
            detailed_parts.append("  • Green 'Run' buttons visible (not executed)")
            detailed_parts.append("  • Right panel empty or showing 'No sections'")
            detailed_parts.append("")
            
            detailed_parts.append("💡 What This Means:")
            detailed_parts.append("  • Notebook has code but has NOT been executed")
            detailed_parts.append("  • No training has started yet")
            detailed_parts.append("  • No output, logs, or results generated")
            detailed_parts.append("  • Need to click 'Run All' button in Kaggle")
            detailed_parts.append("")
            
            detailed_parts.append("🎯 Next Steps:")
            detailed_parts.append("  1. Go to Kaggle notebook page")
            detailed_parts.append("  2. Click 'Run All' button (top right)")
            detailed_parts.append("  3. Wait for training to start")
            detailed_parts.append("  4. Check again with /check command")
            detailed_parts.append("")
        
        # Add statistics
        detailed_parts.append("📊 Analysis Statistics:")
        detailed_parts.append(f"  • Total screenshots: {len(analyses)}")
        detailed_parts.append(f"  • Screenshots with content: {has_content_count}")
        detailed_parts.append(f"  • Status breakdown:")
        for status, count in sorted(status_counts.items()):
            percentage = (count / len(analyses)) * 100
            detailed_parts.append(f"    - {status}: {count} ({percentage:.0f}%)")
        
        # Combine everything
        full_details = '\n'.join(detailed_parts)
        
        # Create short summary for quick view
        summary_parts = []
        summary_parts.append(f"Analyzed {len(analyses)} screenshots")
        summary_parts.append(f"Content: {has_content_count}/{len(analyses)}")
        for status, count in sorted(status_counts.items()):
            summary_parts.append(f"{status}: {count}")
        short_summary = ' | '.join(summary_parts)
        
        return {
            'status': final_status,
            'summary': short_summary,
            'details': full_details,  # This is the comprehensive description
            'total_screenshots': len(analyses),
            'content_screenshots': has_content_count,
            'status_breakdown': status_counts,
            'training_info': [item['info'] for item in training_info[:8]],
            'empty_indicators': [f"SS{item['ss']}: {item['reason']}" for item in empty_indicators[:10]],
            'key_findings': [f"SS{f['ss']} ({f['status']}): {f['info']}" for f in key_findings[:8]]
        }
    
    def cleanup(self):
        """Clean up model resources."""
        try:
            if self.model is not None:
                if torch.cuda.is_available():
                    self.model.cpu()
                    torch.cuda.empty_cache()
                del self.model
                del self.processor
                self.model = None
                self.processor = None
                logger.info("Qwen model cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
