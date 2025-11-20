import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { SearchResponse, SearchFilters, Documento } from '../types';
import DocumentCard from './DocumentCard';

interface SearchComponentProps {
  onDocumentSelect?: (documento: Documento) => void;
}

const SearchComponent: React.FC<SearchComponentProps> = ({ onDocumentSelect }) => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const PAGE_SIZE = 10;

  // Debounce search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Perform search when debounced query or filters change
  useEffect(() => {
    if (debouncedQuery.trim().length >= 3) {
      performSearch(1);
    } else {
      setResults(null);
    }
  }, [debouncedQuery, filters]);

  const performSearch = async (pageNum: number) => {
    if (debouncedQuery.trim().length < 3) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.post<SearchResponse>('/documentos/search', {
        query: debouncedQuery,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        page: pageNum,
        page_size: PAGE_SIZE,
      });

      setResults(response.data);
      setPage(pageNum);
    } catch (err: any) {
      console.error('Error searching documents:', err);
      setError(err.response?.data?.detail || 'Error al buscar documentos');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    performSearch(newPage);
  };

  const handleFilterChange = (filterKey: keyof SearchFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [filterKey]: value || undefined,
    }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({});
    setPage(1);
  };



  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Search Input */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar documentos por contenido, tema o descripción..."
            className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg
            className="absolute left-4 top-3.5 h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        {query.length > 0 && query.length < 3 && (
          <p className="mt-1 text-sm text-gray-500">Escribe al menos 3 caracteres para buscar</p>
        )}
      </div>

      {/* Filters */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-700">Filtros</h3>
          {Object.keys(filters).length > 0 && (
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Limpiar filtros
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Documento
            </label>
            <select
              value={filters.tipo_documento || ''}
              onChange={(e) => handleFilterChange('tipo_documento', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="Oficio">Oficio</option>
              <option value="Oficio Múltiple">Oficio Múltiple</option>
              <option value="Resolución Directorial">Resolución Directorial</option>
              <option value="Informe">Informe</option>
              <option value="Solicitud">Solicitud</option>
              <option value="Memorándum">Memorándum</option>
              <option value="Acta">Acta</option>
              <option value="Varios">Varios</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Desde
            </label>
            <input
              type="date"
              value={filters.fecha_desde || ''}
              onChange={(e) => handleFilterChange('fecha_desde', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Hasta
            </label>
            <input
              type="date"
              value={filters.fecha_hasta || ''}
              onChange={(e) => handleFilterChange('fecha_hasta', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Buscando documentos...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {!loading && results && (
        <>
          <div className="mb-4 text-sm text-gray-600">
            {results.total} resultado{results.total !== 1 ? 's' : ''} encontrado{results.total !== 1 ? 's' : ''}
          </div>

          <div className="space-y-4">
            {results.results.map((result) => (
              <DocumentCard
                key={result.documento.id}
                documento={result.documento}
                onSelect={onDocumentSelect}
                relevanceScore={result.relevance_score}
                showActions={false}
              />
            ))}
          </div>

          {/* Pagination */}
          {results.total_pages > 1 && (
            <div className="mt-6 flex justify-center items-center space-x-2">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Anterior
              </button>
              <span className="text-sm text-gray-600">
                Página {page} de {results.total_pages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === results.total_pages}
                className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}

      {/* No Results */}
      {!loading && results && results.results.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-2">No se encontraron documentos que coincidan con tu búsqueda</p>
        </div>
      )}
    </div>
  );
};

export default SearchComponent;
