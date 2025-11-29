import base64
from pathlib import Path
from typing import List, Dict
from PyPDF2 import PdfReader
from PIL import Image
import io

class DocumentProcessor:
    @staticmethod
    def process_file(file_path: str) -> List[Dict]:
        """Process uploaded file and return content for LLM"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.pdf':
            return DocumentProcessor._process_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
            return DocumentProcessor._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _process_pdf(pdf_path: str) -> List[Dict]:
        """Convert PDF pages to images or extract text"""
        # Try pdf2image first (best quality)
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=200)
            
            content = []
            for i, img in enumerate(images):
                # Resize if too large
                max_size = 2048
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                        "detail": "high"
                    }
                })
            
            return content
            
        except Exception as e:
            # Fallback: extract text only
            print(f"PDF image conversion failed ({e}), using text extraction")
            try:
                reader = PdfReader(pdf_path)
                text_parts = []
                
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"--- Page {i+1} ---\n{page_text}")
                
                if text_parts:
                    full_text = "\n\n".join(text_parts)
                    return [{
                        "type": "text",
                        "text": f"📄 PDF Content (Text Extraction):\n\n{full_text}"
                    }]
                else:
                    return [{
                        "type": "text",
                        "text": "⚠️ Could not extract text from PDF. The document may contain only images or be encrypted."
                    }]
            except Exception as text_error:
                raise ValueError(f"Failed to process PDF: {text_error}")
    
    @staticmethod
    def _process_image(image_path: str) -> List[Dict]:
        """Encode image to base64 with optimization"""
        try:
            # Open and optimize image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Resize if too large
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save optimized
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return [{
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}",
                    "detail": "high"
                }
            }]
        except Exception as e:
            raise ValueError(f"Failed to process image: {e}")
