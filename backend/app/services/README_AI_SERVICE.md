# AIService - Servicio de IA para SGD UGEL Ilo

## Descripción

El `AIService` es el componente responsable de la integración con Google Generative AI para:
1. **Extracción de metadatos** usando Gemini LLM
2. **Generación de embeddings** usando text-embedding-004

## Requisitos Implementados

### Requirement 3: Extracción Automática de Metadatos

#### 3.1 - Envío de texto a Gemini LLM
✅ **Implementado en**: `extract_metadata(text: str)`
- Envía el texto completo al Gemini LLM con el prompt definido en Steering 1
- Trunca el texto a 4000 caracteres para evitar límites de tokens
- Usa el modelo `gemini-pro`

#### 3.2 - Respuesta JSON estructurada
✅ **Implementado en**: `extract_metadata(text: str)`
- Gemini devuelve un objeto JSON con los campos:
  - `tipo_documento`: String (Ej: Oficio Múltiple, Resolución Directoral)
  - `tema_principal`: String (Título descriptivo del contenido)
  - `fecha_documento`: String (Formato YYYY-MM-DD)
  - `entidades_clave`: Array de strings (Nombres de personas, oficinas, colegios)
  - `resumen_corto`: String (Resumen de 2 frases)

#### 3.3 - Manejo de campos nulos
✅ **Implementado en**: `extract_metadata(text: str)`
- Si Gemini no puede determinar un campo, devuelve `null` para ese campo
- El parsing JSON maneja correctamente valores nulos

### Requirement 4: Generación de Embeddings

#### 4.1 - Generación de embeddings para fragmentos
✅ **Implementado en**: `generate_embedding(text: str)`
- Llama al modelo `text-embedding-004`
- Genera vectores de 768 dimensiones
- Usa `task_type="retrieval_document"` para documentos

#### 4.4 - Generación de embeddings para queries
✅ **Implementado en**: `generate_query_embedding(query: str)`
- Convierte el texto de búsqueda en un vector
- Usa `task_type="retrieval_query"` para optimizar búsquedas
- Genera vectores de 768 dimensiones compatibles con pgvector

## Características Implementadas

### 1. Configuración de Google API
```python
genai.configure(api_key=settings.GOOGLE_API_KEY)
self.gemini_model = genai.GenerativeModel('gemini-pro')
self.embedding_model = 'models/text-embedding-004'
```

### 2. Prompt según Steering 1
El prompt sigue exactamente la especificación de Steering 1:
- Instruye a Gemini como experto en documentos administrativos de UGEL Ilo
- Solicita ÚNICAMENTE un objeto JSON (sin markdown)
- Define la estructura exacta del JSON esperado
- Indica que campos no determinables deben ser `null`

### 3. Parsing y Validación de JSON
```python
def _parse_metadata_json(self, json_text: str) -> Dict[str, Optional[str]]:
    try:
        # Intento directo
        metadata = json.loads(json_text)
        return metadata
    except json.JSONDecodeError:
        # Limpieza de markdown si es necesario
        cleaned = json_text.replace('```json', '').replace('```', '').strip()
        metadata = json.loads(cleaned)
        return metadata
```

### 4. Manejo de Errores y Rate Limiting

#### Rate Limiting
- **Max retries**: 3 intentos
- **Backoff exponencial**: 2s, 4s, 8s
- **Detección**: Captura `google_exceptions.ResourceExhausted`

#### Logging Estructurado
Usa `structlog` para logging detallado:
```python
logger.info("extracting_metadata_with_gemini", attempt=1, text_length=4000)
logger.warning("rate_limit_exceeded", attempt=2, error=str(exc))
logger.error("metadata_extraction_failed", error_type="JSONDecodeError")
```

#### Manejo de Excepciones
- **ResourceExhausted**: Rate limit de Google API → Reintento con backoff
- **JSONDecodeError**: JSON inválido → Intenta limpiar markdown
- **Exception genérica**: Error inesperado → Reintento con delay fijo

## Uso

### Extracción de Metadatos
```python
from app.services.ai_service import AIService

ai_service = AIService()

# Texto extraído por OCR
text = "OFICIO MÚLTIPLE N° 045-2024-UGEL-ILO..."

# Extraer metadatos
metadata = ai_service.extract_metadata(text)

print(metadata)
# {
#   "tipo_documento": "Oficio Múltiple",
#   "tema_principal": "Convocatoria a Reunión de Coordinación",
#   "fecha_documento": "2024-03-15",
#   "entidades_clave": ["UGEL Ilo", "Prof. Juan Pérez García"],
#   "resumen_corto": "Convocatoria a reunión de directores..."
# }
```

### Generación de Embeddings para Documentos
```python
# Fragmento de texto
chunk = "Convocatoria a reunión de coordinación para directores..."

# Generar embedding
embedding = ai_service.generate_embedding(chunk)

print(len(embedding))  # 768
print(embedding[:5])   # [0.123, -0.456, 0.789, ...]
```

### Generación de Embeddings para Búsquedas
```python
# Query de usuario
query = "reunión directores instituciones educativas"

# Generar query embedding
query_embedding = ai_service.generate_query_embedding(query)

print(len(query_embedding))  # 768
```

## Configuración

### Variables de Entorno
Asegúrate de configurar en `.env`:
```bash
GOOGLE_API_KEY=tu_api_key_de_google_aqui
```

### Obtener API Key
1. Visita [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un nuevo proyecto o selecciona uno existente
3. Genera una API key
4. Copia la key al archivo `.env`

## Verificación

Ejecuta el script de verificación:
```bash
cd backend
python verify_ai_service.py
```

Este script prueba:
1. ✅ Extracción de metadatos con Gemini
2. ✅ Generación de embeddings para documentos
3. ✅ Generación de embeddings para queries

## Limitaciones y Consideraciones

### Rate Limits de Google API
- **Gemini**: ~60 requests/minuto (varía según plan)
- **Embeddings**: ~1500 requests/minuto
- El servicio implementa reintentos automáticos con backoff exponencial

### Tamaño de Texto
- **Gemini**: Se trunca a 4000 caracteres para evitar límites de tokens
- **Embeddings**: Sin límite explícito, pero se recomienda < 2000 caracteres

### Costos
- **Gemini**: Gratis hasta cierto límite, luego pago por token
- **Embeddings**: Gratis hasta cierto límite, luego pago por request
- Consulta [Google AI Pricing](https://ai.google.dev/pricing) para detalles

## Dependencias

```
google-generativeai==0.3.1
structlog==23.2.0
pydantic-settings==2.1.0
```

## Testing

### Unit Tests
```python
# tests/services/test_ai_service.py
def test_extract_metadata():
    service = AIService()
    text = "OFICIO MÚLTIPLE N° 045-2024..."
    metadata = service.extract_metadata(text)
    
    assert metadata['tipo_documento'] is not None
    assert metadata['tema_principal'] is not None
    assert isinstance(metadata['entidades_clave'], list)

def test_generate_embedding():
    service = AIService()
    text = "Convocatoria a reunión..."
    embedding = service.generate_embedding(text)
    
    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)
```

## Troubleshooting

### Error: "API key not valid"
- Verifica que `GOOGLE_API_KEY` esté configurada en `.env`
- Verifica que la API key sea válida en Google AI Studio

### Error: "Resource exhausted"
- Has excedido el rate limit de Google API
- El servicio reintentará automáticamente con backoff
- Considera reducir la concurrencia de workers

### Error: "JSONDecodeError"
- Gemini devolvió una respuesta no JSON
- El servicio intenta limpiar markdown automáticamente
- Si persiste, revisa el prompt en Steering 1

## Referencias

- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Text Embedding Guide](https://ai.google.dev/docs/embeddings_guide)
- [Steering Rules](.kiro/steering/steering.js.md)
