import React, { lazy, Suspense, useState } from 'react';
import { Documento } from './types';

// Lazy loading de componentes pesados
const UploadComponent = lazy(() => import('./components/UploadComponent'));
const SearchComponent = lazy(() => import('./components/SearchComponent'));
const DocumentViewer = lazy(() => import('./components/DocumentViewer'));

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'search'>('upload');
  const [selectedDocument, setSelectedDocument] = useState<Documento | null>(null);

  const handleDocumentSelect = (documento: Documento) => {
    setSelectedDocument(documento);
  };

  const handleCloseViewer = () => {
    setSelectedDocument(null);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 sm:py-6">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold">
            Sistema de Gestión Documental
          </h1>
          <p className="text-blue-100 text-sm mt-1 hidden sm:block">
            Búsqueda inteligente de documentos administrativos
          </p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1 sm:space-x-4">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-3 text-sm sm:text-base font-medium border-b-2 transition-colors ${
                activeTab === 'upload'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <span className="flex items-center space-x-2">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="hidden sm:inline">Subir Documentos</span>
                <span className="sm:hidden">Subir</span>
              </span>
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`px-4 py-3 text-sm sm:text-base font-medium border-b-2 transition-colors ${
                activeTab === 'search'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <span className="flex items-center space-x-2">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="hidden sm:inline">Buscar Documentos</span>
                <span className="sm:hidden">Buscar</span>
              </span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        <Suspense
          fallback={
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">Cargando...</p>
              </div>
            </div>
          }
        >
          {activeTab === 'upload' && (
            <div className="max-w-4xl mx-auto">
              <div className="mb-6">
                <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 mb-2">
                  Cargar Nuevo Documento
                </h2>
                <p className="text-sm sm:text-base text-gray-600">
                  Sube documentos PDF o JPG para procesamiento automático con OCR y extracción de metadatos
                </p>
              </div>
              <UploadComponent
                onUploadSuccess={() => {
                  // Cambiar a la pestaña de búsqueda después de subir exitosamente
                  setTimeout(() => setActiveTab('search'), 2000);
                }}
              />
            </div>
          )}

          {activeTab === 'search' && (
            <div>
              <div className="mb-6">
                <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 mb-2">
                  Búsqueda Semántica
                </h2>
                <p className="text-sm sm:text-base text-gray-600">
                  Encuentra documentos por contenido, tema o descripción usando búsqueda inteligente
                </p>
              </div>
              <SearchComponent onDocumentSelect={handleDocumentSelect} />
            </div>
          )}
        </Suspense>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-600">
            © 2024 Sistema de Gestión Documental
          </p>
        </div>
      </footer>

      {/* Document Viewer Modal */}
      {selectedDocument && (
        <Suspense fallback={null}>
          <DocumentViewer 
            documento={selectedDocument} 
            onClose={handleCloseViewer}
            onDocumentUpdate={(updatedDoc) => {
              // Update the selected document with new data
              setSelectedDocument(updatedDoc);
            }}
            onDocumentDelete={(documentId) => {
              // Close viewer when document is deleted
              setSelectedDocument(null);
            }}
          />
        </Suspense>
      )}
    </div>
  );
}

export default App;
