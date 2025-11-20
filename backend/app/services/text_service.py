"""
Servicio de procesamiento y limpieza de texto.
"""
import re
import structlog
from typing import List

logger = structlog.get_logger()


class TextService:
    """
    Servicio para limpiar y fragmentar texto extraído de documentos.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de procesamiento de texto.
        """
        self.chunk_size = 800  # Tamaño máximo de cada fragmento
        self.overlap = 100  # Solapamiento entre fragmentos consecutivos
    
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto eliminando caracteres no imprimibles y normalizando espacios.
        
        Args:
            text: Texto a limpiar
        
        Returns:
            Texto limpio
        """
        if not text:
            return ""
        
        original_length = len(text)
        
        # Eliminar caracteres de control problemáticos (pero mantener espacios, tabs, newlines)
        # Mantener: espacios, tabs, newlines, ASCII imprimibles, caracteres latinos extendidos
        # Rango Unicode: 
        #   - \x20-\x7E: ASCII imprimibles (incluye espacio)
        #   - \u00A0-\u024F: Caracteres latinos extendidos (ñ, acentos, etc.)
        #   - \u1E00-\u1EFF: Caracteres latinos adicionales
        #   - \n\r\t: Saltos de línea y tabs
        text = re.sub(r'[^\x20-\x7E\u00A0-\u024F\u1E00-\u1EFF\n\r\t]', ' ', text)
        
        # Normalizar espacios en blanco (múltiples espacios → un espacio)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalizar saltos de línea (múltiples → uno)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Eliminar espacios al inicio y final de cada línea
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        text = '\n'.join(lines)
        
        # Eliminar espacios al inicio y final del texto completo
        text = text.strip()
        
        logger.debug(
            "text_cleaned",
            original_length=original_length,
            cleaned_length=len(text)
        )
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Fragmenta el texto en chunks con solapamiento.
        
        Args:
            text: Texto a fragmentar
            chunk_size: Tamaño máximo de cada chunk (default: 800)
            overlap: Solapamiento entre chunks (default: 100)
        
        Returns:
            Lista de fragmentos de texto
        
        Raises:
            ValueError: Si chunk_size <= overlap
        """
        if not text:
            return []
        
        # Usar valores por defecto si no se especifican
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap
        
        # Validar parámetros
        if chunk_size <= overlap:
            raise ValueError(
                f"chunk_size ({chunk_size}) debe ser mayor que overlap ({overlap})"
            )
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calcular fin del chunk
            end = min(start + chunk_size, text_length)
            
            # Extraer chunk
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Si ya llegamos al final, terminar
            if end >= text_length:
                break
            
            # Mover el inicio para el siguiente chunk con overlap
            start = end - overlap
        
        logger.info(
            "text_chunked",
            text_length=text_length,
            num_chunks=len(chunks),
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        return chunks
    
    def process_text(self, text: str) -> List[str]:
        """
        Procesa texto completo: limpia y fragmenta.
        
        Args:
            text: Texto a procesar
        
        Returns:
            Lista de fragmentos limpios
        """
        # Limpiar texto
        cleaned_text = self.clean_text(text)
        
        # Si el texto es corto, no fragmentar
        if len(cleaned_text) <= self.chunk_size:
            return [cleaned_text] if cleaned_text else []
        
        # Fragmentar texto largo
        chunks = self.chunk_text(cleaned_text)
        
        return chunks
