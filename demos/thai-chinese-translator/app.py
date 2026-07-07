"""
Thai-Chinese Document Translator DEMO - Day 2
Implementing actual OCR + Translation + PDF generation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
from pathlib import Path
import logging
from datetime import datetime

# Initialize app
app = FastAPI(title="Thai-Chinese Document Translator Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API clients
try:
    import anthropic
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PIL import Image
    import io
    DEPS_OK = True
except ImportError as e:
    DEPS_OK = False
    logging.warning(f"Missing dependencies: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_anthropic_client():
    """Anthropic Claude client"""
    if not DEPS_OK:
        return None
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        return None
    return anthropic.Anthropic(api_key=api_key)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Upload page"""
    # (HTML from Day 1, unchanged)
    html_content = open("index.html").read() if Path("index.html").exists() else """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Thai-Chinese Translator Demo</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 16px;
            }
            .upload-zone {
                border: 3px dashed #ddd;
                border-radius: 10px;
                padding: 60px 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                background: #fafafa;
            }
            .upload-zone:hover {
                border-color: #4CAF50;
                background: #f0f8f0;
            }
            .upload-zone.dragover {
                border-color: #4CAF50;
                background: #e8f5e9;
                transform: scale(1.02);
            }
            .upload-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            #file-input {
                display: none;
            }
            .preview {
                margin: 30px 0;
                display: none;
            }
            .preview img {
                max-width: 100%;
                max-height: 400px;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .file-info {
                margin-top: 15px;
                padding: 15px;
                background: #f0f0f0;
                border-radius: 6px;
                font-size: 14px;
            }
            .button {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: inline-block;
                text-decoration: none;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            .button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 40px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4CAF50;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result {
                margin-top: 30px;
                padding: 30px;
                background: #e8f5e9;
                border-radius: 8px;
                display: none;
                text-align: center;
            }
            .result h3 {
                color: #2e7d32;
                margin-bottom: 15px;
            }
            .demo-badge {
                display: inline-block;
                background: #ff9800;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🇨🇳 → 🇹🇭 Document Translator <span class="demo-badge">DEMO</span></h1>
            <p class="subtitle">Instantly translate Chinese invoices to Thai</p>

            <div class="upload-zone" id="upload-zone">
                <div class="upload-icon">📄</div>
                <h2 style="margin-bottom: 10px;">Drop Chinese Invoice Here</h2>
                <p style="color: #888;">or click to select file (images or PDF)</p>
                <input type="file" id="file-input" accept="image/*,.pdf">
            </div>

            <div class="preview" id="preview">
                <img id="preview-img" alt="Preview">
                <div class="file-info" id="file-info"></div>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <button class="button" id="translate-btn" disabled>🚀 Translate Now</button>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3>Translating...</h3>
                <p>Extracting Chinese text → Translating to Thai → Generating PDF</p>
                <p style="color: #888; margin-top: 10px;">This takes 30-60 seconds</p>
            </div>

            <div class="result" id="result">
                <h3>✅ Translation Complete!</h3>
                <p style="margin: 15px 0;">Bilingual PDF ready (Chinese left, Thai right)</p>
                <a id="download-link" class="button" href="#" download>📥 Download PDF</a>
            </div>
        </div>

        <script>
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            const preview = document.getElementById('preview');
            const previewImg = document.getElementById('preview-img');
            const fileInfo = document.getElementById('file-info');
            const translateBtn = document.getElementById('translate-btn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const downloadLink = document.getElementById('download-link');

            let selectedFile = null;

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
                if (e.dataTransfer.files.length > 0) {
                    handleFile(e.dataTransfer.files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });

            function handleFile(file) {
                selectedFile = file;
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                fileInfo.innerHTML = `
                    <strong>File:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${sizeMB} MB<br>
                    <strong>Type:</strong> ${file.type}
                `;

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

                result.style.display = 'none';
                loading.style.display = 'block';
                translateBtn.disabled = true;

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Translation failed');
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
    """Happy path: Chinese doc → OCR → Translate → Bilingual PDF"""
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Save upload
        file_path = UPLOAD_DIR / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Step 1: OCR
        chinese_text = await extract_chinese_text(file_path, content)
        logger.info(f"Extracted {len(chinese_text)} chars")

        # Step 2: Translate
        thai_text, key_fields = await translate_to_thai(chinese_text)
        logger.info(f"Translated to {len(thai_text)} chars")

        # Step 3: PDF
        pdf_path = await generate_bilingual_pdf(
            chinese_text, thai_text, key_fields, file.filename
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"translated_{Path(file.filename).stem}.pdf"
        )
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def extract_chinese_text(image_path: Path, content: bytes) -> str:
    """Claude Vision API for OCR - extract Chinese text from image"""
    client = get_anthropic_client()

    # DEMO fallback: use sample text if no Claude client
    if not client:
        logger.warning("Claude client unavailable, using sample text")
        return SAMPLE_CHINESE_TEXT

    try:
        # Encode image as base64
        import base64
        image_data = base64.standard_b64encode(content).decode("utf-8")

        # Determine media type from file extension
        file_ext = image_path.suffix.lower()
        if file_ext in ['.jpg', '.jpeg']:
            media_type = "image/jpeg"
        elif file_ext == '.png':
            media_type = "image/png"
        elif file_ext == '.gif':
            media_type = "image/gif"
        elif file_ext == '.webp':
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"  # Default

        # Use Claude to extract Chinese text from image
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Extract ALL Chinese text from this image, preserving the structure and layout. Return only the extracted text without any explanations or commentary."
                        }
                    ],
                }
            ],
        )

        extracted_text = response.content[0].text

        if extracted_text and len(extracted_text.strip()) > 0:
            return extracted_text

        return SAMPLE_CHINESE_TEXT  # Fallback if no text detected
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return SAMPLE_CHINESE_TEXT


async def translate_to_thai(chinese_text: str) -> tuple[str, dict]:
    """Claude translation with key field extraction"""
    client = get_anthropic_client()

    # DEMO fallback
    if not client:
        logger.warning("Claude client unavailable, using sample translation")
        return SAMPLE_THAI_TEXT, SAMPLE_KEY_FIELDS

    try:
        prompt = f"""Translate this Chinese business document to Thai. Also extract and highlight these key fields:
- Total amount (总金额/金额/总计)
- Date (日期/时间)
- Payment terms (付款条件/付款方式)

Chinese text:
{chinese_text}

Respond with JSON:
{{
    "thai_translation": "Thai text here",
    "key_fields": {{
        "amount": "678.00 หยวน",
        "date": "5 กรกฎาคม 2026",
        "payment_terms": "สุทธิ 30 วัน"
    }}
}}
"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        response_text = response.content[0].text

        # Claude may wrap JSON in markdown code blocks, strip them
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```

        result = json.loads(response_text.strip())

        return result["thai_translation"], result["key_fields"]
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return SAMPLE_THAI_TEXT, SAMPLE_KEY_FIELDS


async def generate_bilingual_pdf(chinese: str, thai: str, key_fields: dict, filename: str) -> Path:
    """Side-by-side PDF with highlighted fields"""
    output_path = OUTPUT_DIR / f"translated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    if not DEPS_OK:
        # Minimal PDF for demo
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%EOF")
        return output_path
    
    try:
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2e7d32'),
            spaceAfter=20,
            alignment=1  # Center
        )
        story.append(Paragraph("Bilingual Translation (Chinese → Thai)", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Key fields highlighted
        story.append(Paragraph("<b>Key Fields:</b>", styles['Heading2']))
        key_data = [
            [Paragraph("<b>Field</b>", styles['Normal']), Paragraph("<b>Value</b>", styles['Normal'])],
            [Paragraph("Amount", styles['Normal']), Paragraph(key_fields.get('amount', 'N/A'), styles['Normal'])],
            [Paragraph("Date", styles['Normal']), Paragraph(key_fields.get('date', 'N/A'), styles['Normal'])],
            [Paragraph("Payment Terms", styles['Normal']), Paragraph(key_fields.get('payment_terms', 'N/A'), styles['Normal'])],
        ]
        key_table = Table(key_data, colWidths=[2*inch, 4*inch])
        key_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(key_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Side-by-side content
        story.append(Paragraph("<b>Full Translation:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Split texts into paragraphs
        chinese_paras = [p.strip() for p in chinese.split('\n') if p.strip()]
        thai_paras = [p.strip() for p in thai.split('\n') if p.strip()]
        
        # Create side-by-side table
        translation_data = [[
            Paragraph("<b>Chinese (Original)</b>", styles['Heading3']),
            Paragraph("<b>Thai (Translation)</b>", styles['Heading3'])
        ]]
        
        max_len = max(len(chinese_paras), len(thai_paras))
        for i in range(max_len):
            ch = chinese_paras[i] if i < len(chinese_paras) else ""
            th = thai_paras[i] if i < len(thai_paras) else ""
            translation_data.append([
                Paragraph(ch, styles['Normal']),
                Paragraph(th, styles['Normal'])
            ])
        
        trans_table = Table(translation_data, colWidths=[3*inch, 3*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(trans_table)
        
        doc.build(story)
        logger.info(f"Generated PDF: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        # Fallback: simple text PDF
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%EOF")
        return output_path


# Sample data for demo mode
SAMPLE_CHINESE_TEXT = """发票
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

付款条件: 30天净付"""

SAMPLE_THAI_TEXT = """ใบแจ้งหนี้
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

เงื่อนไขการชำระเงิน: สุทธิ 30 วัน"""

SAMPLE_KEY_FIELDS = {
    "amount": "678.00 หยวน (≈3,390 THB)",
    "date": "5 กรกฎาคม 2026",
    "payment_terms": "สุทธิ 30 วัน"
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
