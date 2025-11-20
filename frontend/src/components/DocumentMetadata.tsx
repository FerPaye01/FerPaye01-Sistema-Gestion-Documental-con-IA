import React from 'react';
import { Documento } from '../types';

interface DocumentMetadataProps {
  documento: Documento;
  className?: string;
}

const DocumentMetadata: React.FC<DocumentMetadataProps> = ({ documento, className = '' }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'No disponible';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
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
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getCategoryColor = (categoria?: string) => {
    const colors: Record<string, string> = {
      'Oficio': 'bg-blue-100 text-blue-800',
      'Oficio Múltiple': 'bg-indigo-100 text-indigo-800',
      'Resolución Directorial': 'bg-purple-100 text-purple-800',
      'Informe': 'bg-green-100 text-green-800',
      'Solicitud': 'bg-yellow-100 text-yellow-800',
      'Memorándum': 'bg-orange-100 text-orange-800',
      'Acta': 'bg-red-100 text-red-800',
      'Varios': 'bg-gray-100 text-gray-800'
    };
    
    return colors[categoria || ''] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Información del Documento</h3>
      </div>

      {/* Content */}
      <div className="px-6 py-4 space-y-6">
        {/* Basic Information */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Información Básica</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Nombre del Archivo
              </label>
              <p className="mt-1 text-sm text-gray-900 break-all">{documento.filename}</p>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Tipo de Documento
              </label>
              <div className="mt-1">
                {documento.tipo_documento ? (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(documento.tipo_documento)}`}>
                    {documento.tipo_documento}
                  </span>
                ) : (
                  <span className="text-sm text-gray-500">No clasificado</span>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Tamaño del Archivo
              </label>
              <p className="mt-1 text-sm text-gray-900">{formatFileSize(documento.file_size_bytes)}</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Tipo de Contenido
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {documento.content_type === 'application/pdf' ? 'PDF' : 'Imagen JPG'}
              </p>
            </div>

            {documento.num_pages && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Número de Páginas
                </label>
                <p className="mt-1 text-sm text-gray-900">{documento.num_pages}</p>
              </div>
            )}
          </div>
        </div>

        {/* Document Content */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Contenido del Documento</h4>
          <div className="space-y-4">
            {documento.tema_principal && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Tema Principal
                </label>
                <p className="mt-1 text-sm text-gray-900">{documento.tema_principal}</p>
              </div>
            )}

            {documento.resumen_corto && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Resumen
                </label>
                <p className="mt-1 text-sm text-gray-900 leading-relaxed">{documento.resumen_corto}</p>
              </div>
            )}

            {documento.fecha_documento && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Fecha del Documento
                </label>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(documento.fecha_documento).toLocaleDateString('es-PE', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            )}

            {documento.entidades_clave && documento.entidades_clave.length > 0 && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                  Entidades Clave
                </label>
                <div className="flex flex-wrap gap-2">
                  {documento.entidades_clave.map((entidad, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200"
                    >
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                      {entidad}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* System Information */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Información del Sistema</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Fecha de Subida
              </label>
              <p className="mt-1 text-sm text-gray-900">{formatDate(documento.upload_timestamp)}</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Última Actualización
              </label>
              <p className="mt-1 text-sm text-gray-900">{formatDate(documento.updated_at)}</p>
            </div>

            {documento.processed_at && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Procesado el
                </label>
                <p className="mt-1 text-sm text-gray-900">{formatDate(documento.processed_at)}</p>
              </div>
            )}

            {documento.created_by && (
              <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Subido por
                </label>
                <p className="mt-1 text-sm text-gray-900">{documento.created_by}</p>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                Estado
              </label>
              <div className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  documento.status === 'completed' 
                    ? 'bg-green-100 text-green-800'
                    : documento.status === 'processing'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  <svg className={`w-3 h-3 mr-1 ${
                    documento.status === 'completed' 
                      ? 'text-green-400'
                      : documento.status === 'processing'
                      ? 'text-yellow-400'
                      : 'text-red-400'
                  }`} fill="currentColor" viewBox="0 0 20 20">
                    {documento.status === 'completed' ? (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    ) : documento.status === 'processing' ? (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    ) : (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    )}
                  </svg>
                  {documento.status === 'completed' ? 'Completado' : 
                   documento.status === 'processing' ? 'Procesando' : 'Error'}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide">
                ID del Documento
              </label>
              <p className="mt-1 text-xs text-gray-600 font-mono break-all">{documento.id}</p>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {documento.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-red-800">Error de Procesamiento</h4>
                <p className="mt-1 text-sm text-red-700">{documento.error_message}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentMetadata;