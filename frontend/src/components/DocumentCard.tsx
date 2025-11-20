import React from 'react';
import { Documento } from '../types';

interface DocumentCardProps {
  documento: Documento;
  onSelect?: (documento: Documento) => void;
  onEdit?: (documento: Documento) => void;
  onDelete?: (documento: Documento) => void;
  showActions?: boolean;
  relevanceScore?: number;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ 
  documento, 
  onSelect, 
  onEdit, 
  onDelete, 
  showActions = false,
  relevanceScore 
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Fecha no disponible';
    try {
      return new Date(dateString).toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getCategoryColor = (categoria?: string) => {
    const colors: Record<string, string> = {
      'Oficio': 'bg-blue-100 text-blue-800 border-blue-200',
      'Oficio Múltiple': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'Resolución Directorial': 'bg-purple-100 text-purple-800 border-purple-200',
      'Informe': 'bg-green-100 text-green-800 border-green-200',
      'Solicitud': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Memorándum': 'bg-orange-100 text-orange-800 border-orange-200',
      'Acta': 'bg-red-100 text-red-800 border-red-200',
      'Varios': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    
    return colors[categoria || ''] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getRelevanceColor = (score?: number) => {
    if (!score) return '';
    // Score más bajo = más relevante (similitud de coseno)
    if (score < 0.3) return 'text-green-600';
    if (score < 0.5) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getRelevanceLabel = (score?: number) => {
    if (!score) return '';
    if (score < 0.3) return 'Alta';
    if (score < 0.5) return 'Media';
    return 'Baja';
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Prevent card click when clicking on action buttons
    if ((e.target as HTMLElement).closest('.action-button')) {
      return;
    }
    onSelect?.(documento);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(documento);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(documento);
  };

  return (
    <div
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 cursor-pointer group"
      onClick={handleCardClick}
    >
      {/* Header with category and actions */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center space-x-2 flex-1">
          {/* Category Badge */}
          {documento.tipo_documento && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getCategoryColor(documento.tipo_documento)}`}>
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              {documento.tipo_documento}
            </span>
          )}
          
          {/* Relevance Score */}
          {relevanceScore !== undefined && (
            <span className={`text-xs font-medium ${getRelevanceColor(relevanceScore)}`}>
              Relevancia: {getRelevanceLabel(relevanceScore)}
            </span>
          )}
        </div>

        {/* Quick Actions */}
        {showActions && (
          <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onEdit && (
              <button
                onClick={handleEdit}
                className="action-button p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                title="Editar documento"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
            {onDelete && (
              <button
                onClick={handleDelete}
                className="action-button p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                title="Eliminar documento"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H8a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        )}
      </div>

      {/* Document Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
        {documento.tema_principal || documento.filename}
      </h3>

      {/* Document Summary */}
      {documento.resumen_corto && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {documento.resumen_corto}
        </p>
      )}

      {/* Key Entities */}
      {documento.entidades_clave && documento.entidades_clave.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {documento.entidades_clave.slice(0, 3).map((entidad, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200"
              >
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
                {entidad}
              </span>
            ))}
            {documento.entidades_clave.length > 3 && (
              <span className="text-xs text-gray-500 px-2 py-0.5">
                +{documento.entidades_clave.length - 3} más
              </span>
            )}
          </div>
        </div>
      )}

      {/* Metadata Footer */}
      <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-3 border-t border-gray-100">
        {/* Upload Timestamp */}
        <div className="flex items-center">
          <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span className="font-medium">Subido:</span>
          <span className="ml-1">{formatDate(documento.upload_timestamp)}</span>
        </div>
        
        {/* Document Date */}
        {documento.fecha_documento && (
          <div className="flex items-center">
            <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="font-medium">Fecha doc:</span>
            <span className="ml-1">{formatDate(documento.fecha_documento)}</span>
          </div>
        )}
        
        {/* File Size */}
        <div className="flex items-center">
          <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{formatFileSize(documento.file_size_bytes)}</span>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center">
          <div className={`w-2 h-2 rounded-full mr-2 ${
            documento.status === 'completed' 
              ? 'bg-green-400'
              : documento.status === 'processing'
              ? 'bg-yellow-400'
              : 'bg-red-400'
          }`}></div>
          <span className="capitalize">
            {documento.status === 'completed' ? 'Completado' : 
             documento.status === 'processing' ? 'Procesando' : 'Error'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DocumentCard;