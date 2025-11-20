"""
Servicio de IA para extracción de metadatos y generación de embeddings.
"""
import json
import time
import google.generativeai as genai
import structlog
from typing import List, Dict, Optional
from google.api_core import exceptions as google_exceptions

from app.config import settings

logger = structlog.get_logger()


class AIService:
    """
    Servicio para interactuar con Google Generative AI.
    Maneja extracción de metadatos con Gemini y generación de embeddings.
    """
    
    # Categorías permitidas según requirements 1.1, 5.1, 6.1
    ALLOWED_CATEGORIES = [
        'Oficio',
        'Oficio Múltiple', 
        'Resolución Directorial',
        'Informe',
        'Solicitud',
        'Memorándum',
        'Acta',
        'Varios'
    ]
    
    def __init__(self):
        """
        Inicializa el servicio de IA con la API key de Google.
        """
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Usar modelo configurado en .env (gemini-1.5-flash por defecto)
        gemini_model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        self.gemini_model = genai.GenerativeModel(gemini_model_name)
        self.embedding_model = 'models/text-embedding-004'
        
        # Configuración de rate limiting
        self.max_retries = 3
        self.retry_delay = 2  # segundos
    
    def extract_metadata(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrae metadatos completos de un documento usando Gemini LLM.
        Implementa el prompt mejorado según Steering 1 y requirements 2.1, 2.2, 2.4.
        
        Args:
            text: Texto del documento (se trunca a 4000 caracteres)
        
        Returns:
            Diccionario con metadatos extraídos y validados:
            - tipo_documento: str (categoría validada)
            - tema_principal: str (título descriptivo)
            - fecha_documento: str (formato YYYY-MM-DD)
            - entidades_clave: List[str] (nombres, oficinas, colegios)
            - resumen_corto: str (resumen de 2 frases)
        
        Raises:
            Exception: Si falla la extracción después de reintentos
        """
        # Truncar y sanitizar texto para evitar límites de tokens
        text_truncated = self._sanitize_text_for_llm(text[:4000])
        
        # Log del texto que se envía a Gemini para debugging
        logger.info(
            "text_for_metadata_extraction",
            text_length=len(text_truncated),
            text_preview=text_truncated[:200] if text_truncated else "EMPTY"
        )
        
        # Prompt mejorado según Steering 1 con clasificación estricta
        # Requirements 1.1, 1.2, 5.1, 6.1, 6.3
        prompt = f"""Eres un asistente experto en la clasificación de documentos administrativos de la UGEL Ilo, Perú. Tu tarea es leer el siguiente texto extraído de un documento y devolver ÚNICAMENTE un objeto JSON. No incluyas 'json' ni saltos de línea antes o después del objeto.

CATEGORÍAS PERMITIDAS (SOLO estas 8):
- Oficio
- Oficio Múltiple  
- Resolución Directorial
- Informe
- Solicitud
- Memorándum
- Acta
- Varios (SOLO si no encaja en ninguna anterior)

PROHIBIDO crear nuevas categorías como "Declaración Jurada", "Documento de Estudio", "Trabajo académico" o cualquier otra.
Si no puedes clasificar con certeza en las primeras 7 categorías, usa "Varios".

El objeto JSON debe tener la siguiente estructura exacta:
{{
  "tipo_documento": "String (SOLO una de las 8 categorías listadas arriba)",
  "tema_principal": "String (Un título corto y descriptivo del contenido)",
  "fecha_documento": "String (Formato YYYY-MM-DD, si se encuentra)",
  "entidades_clave": ["Array de strings (Nombres de personas, oficinas o colegios mencionados)"],
  "resumen_corto": "String (Un resumen de 2 frases del propósito del documento)"
}}

Si un campo no se puede determinar, devuelve 'null' para ese campo.

Texto del documento para analizar:
---
{text_truncated}
---
"""
        
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    "extracting_metadata_with_gemini",
                    attempt=attempt + 1,
                    text_length=len(text_truncated)
                )
                
                response = self.gemini_model.generate_content(prompt)
                metadata_json = response.text.strip()
                
                # Intentar parsear JSON
                metadata = self._parse_metadata_json(metadata_json)
                
                logger.info(
                    "metadata_extracted_successfully",
                    metadata=metadata
                )
                
                return metadata
                
            except google_exceptions.ResourceExhausted as exc:
                # Rate limit excedido
                logger.warning(
                    "rate_limit_exceeded",
                    attempt=attempt + 1,
                    error=str(exc)
                )
                
                if attempt < self.max_retries - 1:
                    # Esperar antes de reintentar (backoff exponencial)
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    raise
            
            except Exception as exc:
                logger.error(
                    "metadata_extraction_failed",
                    attempt=attempt + 1,
                    error=str(exc),
                    error_type=type(exc).__name__
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        
        # Si llegamos aquí, todos los reintentos fallaron
        raise Exception("Failed to extract metadata after all retries")
    
    def validate_category(self, category: str) -> str:
        """
        Valida que la categoría esté en la lista permitida.
        Implementa fallback automático a "Varios" según requirements 1.3, 5.4, 6.4.
        
        Args:
            category: Categoría a validar
        
        Returns:
            Categoría validada (original si es válida, "Varios" si no)
        """
        if not category or category not in self.ALLOWED_CATEGORIES:
            if category:
                logger.warning(
                    "invalid_category_rejected",
                    invalid_category=category,
                    fallback_category="Varios"
                )
            return "Varios"
        
        return category
    
    def _sanitize_text_for_llm(self, text: str) -> str:
        """
        Sanitiza el texto antes de enviarlo a Gemini LLM.
        Remueve caracteres problemáticos y normaliza el contenido.
        
        Args:
            text: Texto a sanitizar
        
        Returns:
            Texto sanitizado y seguro para el LLM
        """
        if not text:
            return ""
        
        import re
        
        # Remover solo caracteres de control problemáticos (mantener todo lo demás)
        # Remover: caracteres de control ASCII (0x00-0x1F excepto \n\r\t), DEL (0x7F)
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', text)
        
        # Normalizar espacios múltiples
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        
        # Normalizar saltos de línea (múltiples → uno)
        sanitized = re.sub(r'\n\s*\n+', '\n\n', sanitized)
        
        # Remover líneas excesivamente largas (posibles errores de OCR)
        lines = sanitized.split('\n')
        filtered_lines = [line.strip() for line in lines if line.strip() and len(line) < 500]
        
        return '\n'.join(filtered_lines).strip()
    
    def _parse_metadata_json(self, json_text: str) -> Dict[str, Optional[str]]:
        """
        Parsea y valida el JSON de metadatos devuelto por Gemini.
        Aplica validación completa según requirements 1.3, 2.1, 2.2, 5.4, 6.4.
        
        Args:
            json_text: Texto JSON a parsear
        
        Returns:
            Diccionario con metadatos validados y sanitizados
        
        Raises:
            json.JSONDecodeError: Si el JSON es inválido
        """
        # Log de la respuesta de Gemini para debugging
        logger.info(
            "gemini_response_received",
            response_length=len(json_text),
            response_preview=json_text[:300] if json_text else "EMPTY"
        )
        
        try:
            # Intentar parsear directamente
            metadata = json.loads(json_text)
        except json.JSONDecodeError:
            # Intentar limpiar respuesta si tiene markdown o formato incorrecto
            logger.debug("attempting_to_clean_json_response", raw_response=json_text[:200])
            
            # Remover bloques de código markdown y caracteres problemáticos
            cleaned = json_text.replace('```json', '').replace('```', '').strip()
            
            # Buscar el objeto JSON en la respuesta
            import re
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
            
            # Intentar parsear de nuevo
            metadata = json.loads(cleaned)
        
        # Validar y sanitizar todos los campos
        validated_metadata = self._validate_and_sanitize_metadata(metadata)
        
        return validated_metadata
    
    def _validate_and_sanitize_metadata(self, metadata: dict) -> Dict[str, Optional[str]]:
        """
        Valida y sanitiza todos los campos de metadatos extraídos.
        Implementa requirements 2.1, 2.2, 2.4.
        
        Args:
            metadata: Diccionario con metadatos sin validar
        
        Returns:
            Diccionario con metadatos validados y sanitizados
        """
        validated = {}
        
        # 1. Validar tipo_documento (requirement 1.3, 5.4, 6.4)
        tipo_documento = metadata.get('tipo_documento')
        validated['tipo_documento'] = self.validate_category(tipo_documento)
        
        # 2. Sanitizar tema_principal
        tema_principal = metadata.get('tema_principal')
        if tema_principal and isinstance(tema_principal, str):
            # Limitar longitud y remover caracteres problemáticos
            validated['tema_principal'] = tema_principal.strip()[:200]
        else:
            validated['tema_principal'] = None
        
        # 3. Validar fecha_documento (formato YYYY-MM-DD)
        fecha_documento = metadata.get('fecha_documento')
        validated['fecha_documento'] = self._validate_date_format(fecha_documento)
        
        # 4. Validar y sanitizar entidades_clave
        entidades_clave = metadata.get('entidades_clave')
        validated['entidades_clave'] = self._validate_entities_list(entidades_clave)
        
        # 5. Sanitizar resumen_corto
        resumen_corto = metadata.get('resumen_corto')
        if resumen_corto and isinstance(resumen_corto, str):
            # Limitar longitud y limpiar
            validated['resumen_corto'] = resumen_corto.strip()[:500]
        else:
            validated['resumen_corto'] = None
        
        # Log de validación si hubo cambios
        if metadata != validated:
            logger.info(
                "metadata_validated_and_sanitized",
                original_fields=list(metadata.keys()),
                validated_fields=list(validated.keys()),
                category_validated=validated['tipo_documento']
            )
        
        return validated
    
    def _validate_date_format(self, date_str: Optional[str]) -> Optional[str]:
        """
        Valida que la fecha esté en formato YYYY-MM-DD.
        
        Args:
            date_str: Cadena de fecha a validar
        
        Returns:
            Fecha validada en formato YYYY-MM-DD o None si es inválida
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        # Intentar parsear fecha en formato ISO
        import re
        from datetime import datetime
        
        # Buscar patrón YYYY-MM-DD
        date_pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
        match = re.search(date_pattern, date_str)
        
        if match:
            year, month, day = match.groups()
            try:
                # Validar que sea una fecha real
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                logger.warning("invalid_date_format", date_str=date_str)
                return None
        
        return None
    
    def _validate_entities_list(self, entities: Optional[list]) -> Optional[list]:
        """
        Valida y sanitiza la lista de entidades clave.
        
        Args:
            entities: Lista de entidades a validar
        
        Returns:
            Lista validada de entidades o None si es inválida
        """
        if not entities or not isinstance(entities, list):
            return None
        
        # Filtrar y sanitizar entidades
        validated_entities = []
        for entity in entities:
            if isinstance(entity, str) and entity.strip():
                # Limpiar y limitar longitud
                clean_entity = entity.strip()[:100]
                if len(clean_entity) >= 2:  # Mínimo 2 caracteres
                    validated_entities.append(clean_entity)
        
        # Limitar número máximo de entidades
        return validated_entities[:10] if validated_entities else None
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding vectorial para un fragmento de texto.
        Usa el modelo text-embedding-004 con task_type="retrieval_document".
        
        Args:
            text: Texto a convertir en embedding
        
        Returns:
            Vector de 768 dimensiones
        
        Raises:
            Exception: Si falla la generación después de reintentos
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    "generating_embedding",
                    attempt=attempt + 1,
                    text_length=len(text)
                )
                
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                
                embedding = result['embedding']
                
                logger.debug(
                    "embedding_generated",
                    embedding_dimensions=len(embedding)
                )
                
                return embedding
                
            except google_exceptions.ResourceExhausted as exc:
                logger.warning(
                    "rate_limit_exceeded_embedding",
                    attempt=attempt + 1,
                    error=str(exc)
                )
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    raise
            
            except Exception as exc:
                logger.error(
                    "embedding_generation_failed",
                    attempt=attempt + 1,
                    error=str(exc),
                    error_type=type(exc).__name__
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        
        raise Exception("Failed to generate embedding after all retries")
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Genera un embedding optimizado para queries de búsqueda.
        Usa task_type="retrieval_query" para mejor rendimiento en búsquedas.
        
        Args:
            query: Texto de la consulta de búsqueda
        
        Returns:
            Vector de 768 dimensiones
        
        Raises:
            Exception: Si falla la generación después de reintentos
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    "generating_query_embedding",
                    attempt=attempt + 1,
                    query_length=len(query)
                )
                
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=query,
                    task_type="retrieval_query"
                )
                
                embedding = result['embedding']
                
                logger.debug(
                    "query_embedding_generated",
                    embedding_dimensions=len(embedding)
                )
                
                return embedding
                
            except google_exceptions.ResourceExhausted as exc:
                logger.warning(
                    "rate_limit_exceeded_query_embedding",
                    attempt=attempt + 1,
                    error=str(exc)
                )
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    raise
            
            except Exception as exc:
                logger.error(
                    "query_embedding_generation_failed",
                    attempt=attempt + 1,
                    error=str(exc),
                    error_type=type(exc).__name__
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        
        raise Exception("Failed to generate query embedding after all retries")
