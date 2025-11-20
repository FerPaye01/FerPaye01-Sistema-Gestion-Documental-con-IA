import React, { useState, useRef } from 'react';
import api from '../services/api';

interface UploadComponentProps {
  onUploadSuccess?: (taskId: string) => void;
}

interface TaskStatus {
  status: 'processing' | 'completed' | 'error';
  progress?: number;
  stage?: string;
  documento_id?: string;
  error?: string;
}

const UploadComponent: React.FC<UploadComponentProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
  const ALLOWED_TYPES = ['application/pdf', 'image/jpeg'];

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Solo se permiten archivos PDF o JPG';
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'El archivo no debe superar los 50MB';
    }
    return null;
  };

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const error = validateFile(droppedFile);
      if (error) {
        showNotification('error', error);
      } else {
        setFile(droppedFile);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const error = validateFile(selectedFile);
      if (error) {
        showNotification('error', error);
      } else {
        setFile(selectedFile);
      }
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    try {
      const response = await api.get<TaskStatus>(`/documentos/tasks/${taskId}`);
      setTaskStatus(response.data);

      if (response.data.status === 'completed') {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        showNotification('success', 'Documento procesado exitosamente');
        setUploading(false);
        setFile(null);
        setTaskId(null);
        if (onUploadSuccess && response.data.documento_id) {
          onUploadSuccess(response.data.documento_id);
        }
      } else if (response.data.status === 'error') {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        showNotification('error', `Error al procesar: ${response.data.error || 'Error desconocido'}`);
        setUploading(false);
        setTaskId(null);
      }
    } catch (error) {
      console.error('Error polling task status:', error);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setTaskStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post<{ task_id: string; status: string }>('/documentos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const newTaskId = response.data.task_id;
      setTaskId(newTaskId);
      setTaskStatus({ status: 'processing', progress: 0 });

      // Iniciar polling cada 2 segundos
      pollingIntervalRef.current = setInterval(() => {
        pollTaskStatus(newTaskId);
      }, 2000);

    } catch (error: any) {
      console.error('Error uploading file:', error);
      showNotification('error', error.response?.data?.detail || 'Error al subir el archivo');
      setUploading(false);
    }
  };

  const handleCancel = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setFile(null);
    setUploading(false);
    setTaskId(null);
    setTaskStatus(null);
  };

  React.useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Notification */}
      {notification && (
        <div
          className={`mb-4 p-4 rounded-lg ${
            notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-white hover:border-gray-400'
        } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />

        {!file ? (
          <>
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="mt-2 text-sm text-gray-600">
              Arrastra y suelta un archivo aquí, o{' '}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                selecciona un archivo
              </button>
            </p>
            <p className="mt-1 text-xs text-gray-500">PDF o JPG hasta 50MB</p>
          </>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <svg
                className="h-8 w-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>

            {!uploading && (
              <div className="flex space-x-3 justify-center">
                <button
                  onClick={handleUpload}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Subir Documento
                </button>
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Progress Indicator */}
      {uploading && taskStatus && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              {taskStatus.status === 'processing' ? 'Procesando documento...' : 'Completado'}
            </span>
            {taskStatus.progress !== undefined && (
              <span className="text-sm text-blue-700">{taskStatus.progress}%</span>
            )}
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${taskStatus.progress || 0}%` }}
            />
          </div>
          {taskStatus.stage && (
            <p className="mt-2 text-xs text-blue-700">
              {taskStatus.stage}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadComponent;
