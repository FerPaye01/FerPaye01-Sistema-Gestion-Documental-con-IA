"""
Servicio de OCR híbrido para extracción de texto de documentos.
"""
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import structlog
from typing import Optional

logger = structlog.get_logger()


class OCRService:
    """
    Servicio para extraer texto de documentos PDF e imágenes.
    Usa estrategia híbrida: PyMuPDF para PDFs digitales, pytesseract para OCR.
    """
    
    def __init__(self):
        """
        Inicializa el servicio OCR.
        Configura pytesseract para usar idioma español.
        """
        # Configuración de pytesseract para español
        self.tesseract_lang = 'spa'
        self.min_text_threshold = 50  # Mínimo de caracteres para considerar texto válido
    
    def extract_text(self, file_path: str, content_type: str) -> str:
        """
        Extrae texto de un archivo PDF o imagen.
        
        Args:
            file_path: Ruta local del archivo
            content_type: Tipo MIME del archivo (application/pdf o image/jpeg)
        
        Returns:
            Texto extraído del documento
        
        Raises:
            ValueError: Si el tipo de archivo no es soportado
            Exception: Si falla la extracción de texto
        """
        try:
            if content_type == "application/pdf":
                return self._extract_from_pdf(file_path)
            elif content_type in ["image/jpeg", "image/jpg"]:
                return self._extract_from_image(file_path)
            else:
                raise ValueError(f"Tipo de archivo no soportado: {content_type}")
        
        except Exception as exc:
            logger.error(
                "text_extraction_failed",
                file_path=file_path,
                content_type=content_type,
                error=str(exc)
            )
            raise
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae texto de un PDF usando estrategia híbrida.
        Intenta primero con PyMuPDF (rápido, para PDFs digitales).
        Si no extrae suficiente texto, aplica OCR con pytesseract.
        
        Args:
            pdf_path: Ruta del archivo PDF
        
        Returns:
            Texto extraído
        """
        logger.info("extracting_text_from_pdf", pdf_path=pdf_path)
        
        # Intento 1: PyMuPDF (para PDFs digitales)
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            text += page_text
        
        doc.close()
        
        # Verificar si se extrajo suficiente texto
        if len(text.strip()) >= self.min_text_threshold:
            logger.info(
                "text_extracted_with_pymupdf",
                pdf_path=pdf_path,
                text_length=len(text)
            )
            return text
        
        # Intento 2: OCR con pytesseract (para PDFs escaneados)
        logger.info(
            "insufficient_text_applying_ocr",
            pdf_path=pdf_path,
            extracted_length=len(text.strip())
        )
        
        return self._ocr_pdf_pages(pdf_path)
    
    def _ocr_pdf_pages(self, pdf_path: str) -> str:
        """
        Aplica OCR a todas las páginas de un PDF.
        Convierte cada página a imagen y aplica pytesseract.
        
        Args:
            pdf_path: Ruta del archivo PDF
        
        Returns:
            Texto extraído mediante OCR
        """
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Convertir página a imagen con alta resolución (300 DPI)
            pix = page.get_pixmap(dpi=300)
            
            # Convertir pixmap a imagen PIL
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Aplicar OCR
            page_text = pytesseract.image_to_string(img, lang=self.tesseract_lang)
            text += page_text + "\n"
            
            logger.debug(
                "page_ocr_completed",
                page_num=page_num + 1,
                text_length=len(page_text)
            )
        
        doc.close()
        
        logger.info(
            "pdf_ocr_completed",
            pdf_path=pdf_path,
            total_pages=page_num + 1,
            text_length=len(text)
        )
        
        return text
    
    def _extract_from_image(self, img_path: str) -> str:
        """
        Extrae texto de una imagen JPG usando pytesseract.
        
        Args:
            img_path: Ruta del archivo de imagen
        
        Returns:
            Texto extraído
        """
        logger.info("extracting_text_from_image", img_path=img_path)
        
        # Abrir imagen
        img = Image.open(img_path)
        
        # Aplicar OCR directamente
        text = pytesseract.image_to_string(img, lang=self.tesseract_lang)
        
        logger.info(
            "image_ocr_completed",
            img_path=img_path,
            text_length=len(text)
        )
        
        return text
