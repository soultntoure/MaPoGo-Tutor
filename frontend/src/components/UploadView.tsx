import React, { useState, useRef } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';
interface UploadViewProps {
  onUploadSuccess: () => void;
}
const UploadView: React.FC<UploadViewProps> = ({
  onUploadSuccess
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const handleFileSelect = (file: File) => {
    if (file.type === 'application/pdf') {
      setSelectedFile(file);
      setStatusMessage('');
      setIsError(false);
    } else {
      setStatusMessage('Please select a PDF file only.');
      setIsError(true);
    }
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };
  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setStatusMessage('');
    setIsError(false);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (response.ok) {
        setStatusMessage('PDF uploaded and processed successfully!');
        setTimeout(() => {
          onUploadSuccess();
        }, 1000);
      } else {
        setStatusMessage(data.error || 'Upload failed. Please try again.');
        setIsError(true);
      }
    } catch (error) {
      setStatusMessage('Network error. Please check if the server is running.');
      setIsError(true);
    } finally {
      setIsUploading(false);
    }
  };
  return <div className="flex flex-col items-center justify-center min-h-[400px] space-y-6 animate-fade-in">
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-bold mb-2 text-blue-500">
          MaPoGo Tutor
        </h1>
        <p className="text-lg text-gray-600 max-w-md">
          Transform your PDF documents into interactive learning sessions. Upload a file to get started.
        </p>
      </div>

      <div className={`
          relative w-full max-w-md p-8 border-2 border-dashed rounded-lg cursor-pointer
          transition-all duration-200 ease-in-out
          ${dragOver ? 'dropzone-hover' : 'border-gray-300 hover:border-primary hover:bg-blue-50'}
          ${selectedFile ? 'border-green-400 bg-green-50' : ''}
        `} onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onClick={() => fileInputRef.current?.click()}>
        <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleFileInputChange} className="hidden" />
        
        <div className="flex flex-col items-center space-y-3">
          {selectedFile ? <>
              <FileText className="w-12 h-12 text-green-500" />
              <div className="text-center">
                <p className="font-medium text-green-700">{selectedFile.name}</p>
                <p className="text-sm text-green-600">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </> : <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div className="text-center">
                <p className="font-medium text-gray-700">
                  Drag & Drop a PDF here
                </p>
                <p className="text-sm text-gray-500">
                  or click to select a file
                </p>
              </div>
            </>}
        </div>
      </div>

      <button onClick={handleUpload} disabled={!selectedFile || isUploading} className={`
          px-8 py-3 rounded-lg font-medium transition-all duration-200
          ${!selectedFile || isUploading ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-primary text-white hover:bg-blue-600 hover:shadow-md transform hover:scale-105'}
        `}>
        {isUploading ? <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processing...</span>
          </div> : 'Upload & Process PDF'}
      </button>

      {statusMessage && <div className={`
          p-3 rounded-lg text-sm font-medium
          ${isError ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-green-100 text-green-700 border border-green-200'}
        `}>
          {statusMessage}
        </div>}
    </div>;
};
export default UploadView;