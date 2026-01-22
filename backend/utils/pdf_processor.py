import pdfplumber
from loguru import logger

class PDFProcessor:
    def extract_text(self, file) -> str:
        try:
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise