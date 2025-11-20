import React, { useState, useEffect } from 'react';
import { Documento } from '../types';
import api from '../services/api';

interface DocumentEditorProps {
  documento: Documento;
  onSave: (updatedDocument: Documento) => void;
  onCancel: () => void;
  onDelete?: (documentId: string) => void;
}

// Categorías permitidas según el diseño
const ALLOWED_CATEGORIES = [
  'Oficio',
  'Oficio Múltiple', 
  'Resolución Directorial',
  'Informe',
  'Solicitud',
  'Memorándum',
  'Acta',
  'Varios'
] as const;

const DocumentEditor: React.FC<DocumentEditorProps> = ({ 
  documento, 
  onSave, 
  onCancel, 
  onDelete 
}) => {
  const [formData, setFormData] = useState({
    tipo_documento: documento.tipo_documento || '',
    tema_principal: documento.tema_principal || '',
    fecha_documento: documento.fecha_documento || '',
    entidades_clave: documento.entidades_clave || [],
    resumen_corto: documento.resumen_corto || ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Detectar cambios en el formulario
  useEffect(() => {
    const hasFormChanges = 
      formData.tipo_documento !== (documento.tipo_documento || '') ||
      formData.tema_principal !== (documento.tema_principal || '') ||
      formData.fecha_documento !== (documento.fecha_documento || '') ||
      formData.resumen_corto !== (documento.resumen_corto || '') ||
      JSON.stringify(formData.entidades_clave) !== JSON.stringify(documento.entidades_clave || []);
    
    setHasChanges(hasFormChanges);
  }, [formData, documento]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Validar categoría
    if (!formData.tipo_documento) {
      newErrors.tipo_documento = 'La categoría es requerida';
    } else if (!ALLOWED_CATEGORIES.includes(formData.tipo_documento as any)) {
      newErrors.tipo_documento = 'Categoría no válida';
    }

    // Validar tema principal
    if (!formData.tema_principal.trim()) {
      newErrors.tema_principal = 'El tema principal es requerido';
    }

    // Validar fecha si se proporciona
    if (formData.fecha_documento && !isValidDate(formData.fecha_documento)) {
      newErrors.fecha_documento = 'Formato de fecha inválido (YYYY-MM-DD)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidDate = (dateString: string) => {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date.getTime());
  };

  const handleInputChange = (field: string, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleEntidadesChange = (value: string) => {
    // Convertir string separado por comas a array
    const entidades = value
      .split(',')
      .map(e => e.trim())
      .filter(e => e.length > 0);
    
    handleInputChange('entidades_clave', entidades);
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      // Preparar datos para envío, convirtiendo strings vacíos a null
      const dataToSend = {
        ...formData,
        fecha_documento: formData.fecha_documento || null,
        tema_principal: formData.tema_principal.trim() || null,
        resumen_corto: formData.resumen_corto.trim() || null,
        tipo_documento: formData.tipo_documento || null
      };

      const response = await api.put(`/documentos/${documento.id}`, dataToSend);
      const updatedDocument = { ...documento, ...response.data };
      onSave(updatedDocument);
    } catch (error) {
      console.error('Error updating document:', error);
      setErrors({ general: 'Error al guardar los cambios. Intente nuevamente.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;

    setIsLoading(true);
    try {
      await api.delete(`/documentos/${documento.id}?confirm=true`);
      onDelete(documento.id);
    } catch (error) {
      console.error('Error deleting document:', error);
      setErrors({ general: 'Error al eliminar el documento. Intente nuevamente.' });
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleCancel = () => {
    if (hasChanges) {
      const confirmDiscard = window.confirm(
        '¿Está seguro de que desea cancelar? Se perderán todos los cambios no guardados.'
      );
      if (!confirmDiscard) return;
    }
    onCancel();
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Editar Documento</h3>
        <p className="text-sm text-gray-500 mt-1">{documento.filename}</p>
      </div>

      {/* Form */}
      <div className="px-6 py-4 space-y-6">
        {/* Error general */}
        {errors.general && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <p className="text-sm text-red-700">{errors.general}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tipo de Documento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Documento *
          </label>
          <select
            value={formData.tipo_documento}
            onChange={(e) => handleInputChange('tipo_documento', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.tipo_documento ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Seleccionar categoría...</option>
            {ALLOWED_CATEGORIES.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          {errors.tipo_documento && (
            <p className="mt-1 text-sm text-red-600">{errors.tipo_documento}</p>
          )}
        </div>

        {/* Tema Principal */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tema Principal *
          </label>
          <input
            type="text"
            value={formData.tema_principal}
            onChange={(e) => handleInputChange('tema_principal', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.tema_principal ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Ingrese el tema principal del documento"
          />
          {errors.tema_principal && (
            <p className="mt-1 text-sm text-red-600">{errors.tema_principal}</p>
          )}
        </div>

        {/* Fecha del Documento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha del Documento
          </label>
          <input
            type="date"
            value={formData.fecha_documento}
            onChange={(e) => handleInputChange('fecha_documento', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.fecha_documento ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.fecha_documento && (
            <p className="mt-1 text-sm text-red-600">{errors.fecha_documento}</p>
          )}
        </div>

        {/* Entidades Clave */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Entidades Clave
          </label>
          <input
            type="text"
            value={formData.entidades_clave.join(', ')}
            onChange={(e) => handleEntidadesChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Separar entidades con comas (ej: UGEL Ilo, Director, Juan Pérez)"
          />
          <p className="mt-1 text-sm text-gray-500">
            Ingrese nombres de personas, oficinas o instituciones mencionadas en el documento
          </p>
        </div>

        {/* Resumen Corto */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resumen
          </label>
          <textarea
            value={formData.resumen_corto}
            onChange={(e) => handleInputChange('resumen_corto', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Breve resumen del contenido del documento"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
        <div>
          {onDelete && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-300 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Eliminar
            </button>
          )}
        </div>

        <div className="flex space-x-3">
          <button
            onClick={handleCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading || !hasChanges}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Guardando...' : 'Aceptar Cambios'}
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4">
              <div className="flex items-center">
                <svg className="h-6 w-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900">Confirmar Eliminación</h3>
              </div>
              
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  ¿Está seguro de que desea eliminar este documento? Esta acción no se puede deshacer.
                </p>
                
                <div className="mt-4 p-3 bg-gray-50 rounded-md">
                  <p className="text-sm font-medium text-gray-900">{documento.filename}</p>
                  <p className="text-sm text-gray-600">{documento.tema_principal}</p>
                  <p className="text-sm text-gray-500">Tipo: {documento.tipo_documento}</p>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {isLoading ? 'Eliminando...' : 'Eliminar Documento'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentEditor;