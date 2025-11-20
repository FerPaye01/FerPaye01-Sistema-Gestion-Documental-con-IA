import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Documento } from '../types';
import DocumentMetadata from './DocumentMetadata';
import DocumentEditor from './DocumentEditor';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface DocumentViewerProps {
  documento: Documento;
  onClose?: () => void;
  onDocumentUpdate?: (updatedDocument: Documento) => void;
  onDocumentDelete?: (documentId: string) => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ 
  documento, 
  onClose, 
  onDocumentUpdate, 
  onDocumentDelete 
}) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showMetadata, setShowMetadata] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [currentDocument, setCurrentDocument] = useState<Documento>(documento);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error);
    setError('Error al cargar el documento. Por favor, intenta nuevamente.');
    setLoading(false);
  };

  const goToPrevPage = () => {
    setPageNumber((prev) => Math.max(prev - 1, 1));
  };

  const goToNextPage = () => {
    setPageNumber((prev) => Math.min(prev + 1, numPages));
  };

  const zoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 3.0));
  };

  const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const fitToWidth = () => {
    setScale(1.0);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = currentDocument.minio_url;
    link.download = currentDocument.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDocumentSave = (updatedDocument: Documento) => {
    setCurrentDocument(updatedDocument);
    setIsEditing(false);
    if (onDocumentUpdate) {
      onDocumentUpdate(updatedDocument);
    }
  };

  const handleDocumentDelete = (documentId: string) => {
    if (onDocumentDelete) {
      onDocumentDelete(documentId);
    }
    if (onClose) {
      onClose();
    }
  };

  const handleEditCancel = () => {
    setIsEditing(false);
  };

  const isPDF = currentDocument.filename.toLowerCase().endsWith('.pdf');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold text-gray-900 truncate">
              {currentDocument.tema_principal || currentDocument.filename}
            </h2>
            {currentDocument.tipo_documento && (
              <p className="text-sm text-gray-500">{currentDocument.tipo_documento}</p>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {/* Mode Toggle Buttons */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => {
                  setIsEditing(false);
                  setShowMetadata(true);
                }}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  !isEditing && showMetadata
                    ? 'bg-white text-blue-700 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Modo visualización"
              >
                <svg className="h-4 w-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Ver
              </button>
              <button
                onClick={() => {
                  setIsEditing(true);
                  setShowMetadata(false);
                }}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  isEditing
                    ? 'bg-white text-green-700 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="Modo edición"
              >
                <svg className="h-4 w-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </button>
            </div>

            {/* Info Toggle (only when not editing) */}
            {!isEditing && (
              <button
                onClick={() => setShowMetadata(!showMetadata)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  showMetadata 
                    ? 'bg-blue-50 border-blue-200 text-blue-700' 
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                title="Mostrar/ocultar información detallada"
              >
                <svg className="h-4 w-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {showMetadata ? 'Ocultar Info' : 'Mostrar Info'}
              </button>
            )}

            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Toolbar */}
        {isPDF && (
          <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-gray-50">
            {/* Navigation Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={goToPrevPage}
                disabled={pageNumber <= 1}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                title="Página anterior"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <span className="text-sm text-gray-700 min-w-[100px] text-center">
                Página {pageNumber} de {numPages}
              </span>
              <button
                onClick={goToNextPage}
                disabled={pageNumber >= numPages}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                title="Página siguiente"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={zoomOut}
                disabled={scale <= 0.5}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                title="Alejar"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                </svg>
              </button>
              <span className="text-sm text-gray-700 min-w-[60px] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={zoomIn}
                disabled={scale >= 3.0}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                title="Acercar"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                </svg>
              </button>
              <button
                onClick={fitToWidth}
                className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100"
                title="Ajustar al ancho"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownload}
                className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                title="Descargar"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span>Descargar</span>
              </button>
              <button
                onClick={handlePrint}
                className="px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center space-x-1"
                title="Imprimir"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                <span>Imprimir</span>
              </button>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Document Content */}
          <div className={`flex-1 overflow-auto bg-gray-100 p-4 transition-all duration-300 ${
            showMetadata || isEditing ? 'mr-0' : ''
          }`}>
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">Cargando documento...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center p-6 bg-red-50 rounded-lg">
                <svg className="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="mt-2 text-red-800">{error}</p>
              </div>
            </div>
          )}

          {isPDF ? (
            <div className="flex justify-center">
              <Document
                file={currentDocument.minio_url}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={onDocumentLoadError}
                loading=""
                error=""
              >
                <Page
                  pageNumber={pageNumber}
                  scale={scale}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  className="shadow-lg"
                />
              </Document>
            </div>
          ) : (
            // For JPG images
            <div className="flex justify-center">
              <img
                src={currentDocument.minio_url}
                alt={currentDocument.filename}
                className="max-w-full h-auto shadow-lg"
                style={{ transform: `scale(${scale})` }}
                onLoad={() => setLoading(false)}
                onError={() => {
                  setError('Error al cargar la imagen');
                  setLoading(false);
                }}
              />
            </div>
          )}
          </div>

          {/* Editor Sidebar */}
          {isEditing && (
            <div className="w-96 border-l border-gray-200 bg-gray-50 overflow-auto">
              <DocumentEditor 
                documento={currentDocument}
                onSave={handleDocumentSave}
                onCancel={handleEditCancel}
                onDelete={onDocumentDelete ? handleDocumentDelete : undefined}
              />
            </div>
          )}

          {/* Enhanced Metadata Sidebar */}
          {showMetadata && !isEditing && (
            <div className="w-96 border-l border-gray-200 bg-white overflow-auto">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Información del Documento</h3>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                    title="Editar metadatos"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                </div>
                <DocumentMetadata documento={currentDocument} />
              </div>
            </div>
          )}
        </div>

        {/* Enhanced Compact Footer with metadata when sidebar is closed */}
        {!showMetadata && !isEditing && (
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Left Column */}
              <div className="space-y-2">
                {currentDocument.resumen_corto && (
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Resumen:</span> {currentDocument.resumen_corto}
                  </p>
                )}
                {currentDocument.entidades_clave && currentDocument.entidades_clave.length > 0 && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Entidades:</span> {currentDocument.entidades_clave.slice(0, 3).join(', ')}
                    {currentDocument.entidades_clave.length > 3 && '...'}
                  </p>
                )}
              </div>
              
              {/* Right Column */}
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Subido:</span>
                  <span>{new Date(currentDocument.upload_timestamp).toLocaleDateString('es-PE')}</span>
                </div>
                {currentDocument.fecha_documento && (
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Fecha doc:</span>
                    <span>{new Date(currentDocument.fecha_documento).toLocaleDateString('es-PE')}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="font-medium">Estado:</span>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    currentDocument.status === 'completed' 
                      ? 'bg-green-100 text-green-800'
                      : currentDocument.status === 'processing'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {currentDocument.status === 'completed' ? 'Completado' : 
                     currentDocument.status === 'processing' ? 'Procesando' : 'Error'}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Quick action to show full metadata */}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <button
                onClick={() => setShowMetadata(true)}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Ver información completa →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;
