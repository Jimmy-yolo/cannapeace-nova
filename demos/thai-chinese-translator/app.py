"""
Thai-Chinese Document Translator DEMO
Build: Day 1-2 (2026-07-08 to 2026-07-09)
Mode: DEMO - Happy path only, sample data
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import base64
from pathlib import Path
import logging

# API clients (will be initialized with env vars)
try:
    from google.cloud import vision
    from openai import OpenAI
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    logging.warning("Dependencies not installed yet - install phase")

app = FastAPI(title="Thai-Chinese Document Translator Demo")

# Configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize clients (requires env vars)
def get_vision_client():
    """Google Cloud Vision client for OCR"""
    if not DEPS_AVAILABLE:
        raise HTTPException(500, "Dependencies not installed")
    # TODO: Set GOOGLE_APPLICATION_CREDENTIALS env var
    return vision.ImageAnnotatorClient()

def get_openai_client():
    """OpenAI client for translation"""
    if not DEPS_AVAILABLE:
        raise HTTPException(500, "Dependencies not installed")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Upload page (single file drag & drop)"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thai-Chinese Translator Demo</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .upload-zone {
                border: 3px dashed #ccc;
                border-radius: 10px;
                padding: 50px;
                text-align: center;
                cursor: pointer;
                margin: 30px 0;
            }
            .upload-zone.dragover {
                border-color: #4CAF50;
                background: #f0f0f0;
            }
            #file-input {
                display: none;
            }
            .preview {
                margin-top: 20px;
                display: none;
            }
            .preview img {
                max-width: 100%;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .button {
                background: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
            }
            .button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 5px;
                display: none;
            }
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>🇨🇳 → 🇹🇭 Thai-Chinese Document Translator</h1>
        <p><strong>DEMO:</strong> Upload Chinese invoice/document → Get bilingual PDF</p>

        <div class="upload-zone" id="upload-zone">
            <h2>📄 Drag & Drop Chinese Invoice</h2>
            <p>or click to select file</p>
            <input type="file" id="file-input" accept="image/*,.pdf">
        </div>

        <div class="preview" id="preview">
            <h3>Preview:</h3>
            <img id="preview-img" alt="Preview">
            <p id="file-name"></p>
        </div>

        <button class="button" id="translate-btn" disabled>Translate Now</button>

        <div class="loading" id="loading">
            <h3>⏳ Translating... (30-60 seconds)</h3>
            <p>Extracting Chinese text → Translating to Thai → Generating PDF...</p>
        </div>

        <div class="result" id="result">
            <h3>✅ Translation Complete!</h3>
            <p>Bilingual PDF ready (Chinese left, Thai right)</p>
            <a id="download-link" class="button" href="#" download>Download PDF</a>
        </div>

        <script>
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            const preview = document.getElementById('preview');
            const previewImg = document.getElementById('preview-img');
            const fileName = document.getElementById('file-name');
            const translateBtn = document.getElementById('translate-btn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const downloadLink = document.getElementById('download-link');

            let selectedFile = null;

            // Drag & drop handlers
            uploadZone.addEventListener('click', () => fileInput.click());
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });
            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('dragover');
            });
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFile(files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });

            function handleFile(file) {
                selectedFile = file;
                fileName.textContent = `File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

                // Show preview
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    preview.style.display = 'block';
                    translateBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }

            translateBtn.addEventListener('click', async () => {
                if (!selectedFile) return;

                // Hide previous results
                result.style.display = 'none';
                loading.style.display = 'block';
                translateBtn.disabled = true;

                // Upload and translate
                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Translation failed');
                    }

                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);

                    downloadLink.href = url;
                    downloadLink.download = 'translated_' + selectedFile.name.replace(/\.[^/.]+$/, '') + '.pdf';

                    loading.style.display = 'none';
                    result.style.display = 'block';
                } catch (error) {
                    alert('Translation failed: ' + error.message);
                    loading.style.display = 'none';
                    translateBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/translate")
async def translate_document(file: UploadFile = File(...)):
    """
    Happy path: Chinese invoice → OCR → Translate → Bilingual PDF
    Demo version: Simplified, no error handling
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Step 1: OCR - Extract Chinese text
        chinese_text = await extract_chinese_text(file_path)

        # Step 2: Translate - Chinese → Thai
        thai_text, key_fields = await translate_to_thai(chinese_text)

        # Step 3: Generate bilingual PDF
        pdf_path = await generate_bilingual_pdf(chinese_text, thai_text, key_fields)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"translated_{file.filename}.pdf"
        )
    except Exception as e:
        logging.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def extract_chinese_text(image_path: Path) -> str:
    """Use Google Cloud Vision to extract Chinese text"""
    # TODO: Implement OCR
    # For now, return sample Chinese text
    return """
    发票
    公司名称: 上海供应商有限公司
    地址: 上海市浦东新区XX路123号

    发票号: INV-2026-001234
    日期: 2026年7月5日

    产品清单:
    1. 不锈钢螺丝 M6 x 20mm - 数量: 1000个 - 单价: 0.50元 - 小计: 500.00元
    2. 塑料垫片 - 数量: 500个 - 单价: 0.20元 - 小计: 100.00元

    小计: 600.00元
    税金 (13%): 78.00元
    总金额: 678.00元

    付款条件: 30天净付
    """


async def translate_to_thai(chinese_text: str) -> tuple[str, dict]:
    """Use GPT-4 to translate Chinese → Thai and extract key fields"""
    # TODO: Implement GPT-4 translation
    # For now, return sample Thai translation
    thai_text = """
    ใบแจ้งหนี้
    ชื่อบริษัท: บริษัท ซัพพลายเออร์เซี่ยงไฮ้ จำกัด
    ที่อยู่: เลขที่ 123 ถนน XX เขตผู่ตง เซี่ยงไฮ้

    เลขที่ใบแจ้งหนี้: INV-2026-001234
    วันที่: 5 กรกฎาคม 2026

    รายการสินค้า:
    1. สกรูสแตนเลส M6 x 20mm - จำนวน: 1,000 ชิ้น - ราคาต่อหน่วย: 0.50 หยวน - รวม: 500.00 หยวน
    2. แผ่นพลาสติกรองรับ - จำนวน: 500 ชิ้น - ราคาต่อหน่วย: 0.20 หยวน - รวม: 100.00 หยวน

    ยอดรวม: 600.00 หยวน
    ภาษี (13%): 78.00 หยวน
    จำนวนเงินทั้งหมด: 678.00 หยวน

    เงื่อนไขการชำระเงิน: สุทธิ 30 วัน
    """

    key_fields = {
        "amount": "678.00 หยวน",
        "date": "5 กรกฎาคม 2026",
        "payment_terms": "สุทธิ 30 วัน"
    }

    return thai_text, key_fields


async def generate_bilingual_pdf(chinese: str, thai: str, key_fields: dict) -> Path:
    """Generate side-by-side Chinese-Thai PDF with highlighted key fields"""
    # TODO: Implement PDF generation with ReportLab
    # For now, create a placeholder PDF path
    output_path = OUTPUT_DIR / "translated_demo.pdf"

    # Placeholder - will implement tomorrow
    with open(output_path, "wb") as f:
        f.write(b"%PDF-1.4\n")  # Minimal PDF header

    return output_path


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
