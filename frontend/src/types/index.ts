// Type definitions for the application
export interface DocumentoMetadata {
  tipo_documento?: string;
  tema_principal?: string;
  fecha_documento?: string;
  entidades_clave?: string[];
  resumen_corto?: string;
}

export interface Documento {
  id: string;
  filename: string;
  minio_url: string;
  tipo_documento?: string;
  tema_principal?: string;
  fecha_documento?: string;
  entidades_clave?: string[];
  resumen_corto?: string;
  file_size_bytes: number;
  content_type: string;
  num_pages?: number;
  upload_timestamp: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
  created_by?: string;
  status: 'processing' | 'completed' | 'error';
  error_message?: string;
}

export interface SearchFilters {
  tipo_documento?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

export interface SearchRequest {
  query: string;
  filters?: SearchFilters;
  page: number;
  page_size: number;
}

export interface SearchResult {
  documento: Documento;
  relevance_score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  total_pages: number;
}
