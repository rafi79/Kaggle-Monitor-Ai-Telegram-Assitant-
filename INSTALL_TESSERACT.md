# Install Tesseract OCR (Optional)

Tesseract speeds up text extraction from screenshots. Qwen works without it, but slower.

## Windows Installation:

### Option 1: Download Installer (Easiest)
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`
3. Install to: `C:\Program Files\Tesseract-OCR`
4. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH
   - Add: `C:\Program Files\Tesseract-OCR`
5. Restart terminal

### Option 2: Skip It
Qwen VL model can read text from images directly. Tesseract just makes it faster.

## Test if installed:
```powershell
tesseract --version
```

If you see version info, it's working!

## Without Tesseract:
The system will use Qwen's built-in OCR (slower but works fine).
