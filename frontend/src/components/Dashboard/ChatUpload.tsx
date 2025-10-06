// src/components/Dashboard/ChatUpload.tsx
import React, { useState, useRef } from 'react';
import { MessageSquare, X, CheckCircle, AlertCircle } from 'lucide-react';
import { documentsAPI } from '../../services/api';

interface UploadedChat {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

const ChatUpload: React.FC = () => {
  const [chats, setChats] = useState<UploadedChat[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files ? Array.from(e.target.files) : [];
    addFiles(selectedFiles);
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const addFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => {
      const validTypes = ['text/plain', 'application/json', 'text/csv'];
      return validTypes.includes(file.type) && file.size <= 10 * 1024 * 1024; // 10MB limit
    });

    const uploadedChats: UploadedChat[] = validFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }));

    setChats(prev => [...prev, ...uploadedChats]);
  };

  const removeChat = (index: number) => {
    setChats(prev => prev.filter((_, i) => i !== index));
  };

  const uploadChat = async (index: number) => {
    const chatUpload = chats[index];
    if (!chatUpload || chatUpload.status === 'uploading') return;

    setChats(prev => prev.map((c, i) => 
      i === index ? { ...c, status: 'uploading', progress: 0 } : c
    ));

    try {
      await documentsAPI.uploadChat(chatUpload.file);

      setChats(prev => prev.map((c, i) => 
        i === index ? { ...c, status: 'success', progress: 100 } : c
      ));
    } catch (error) {
      console.error('Upload error:', error);
      setChats(prev => prev.map((c, i) => 
        i === index ? { 
          ...c, 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Upload failed'
        } : c
      ));
    }
  };

  const uploadAllChats = async () => {
    const pendingChats = chats
      .map((chat, index) => ({ chat, index }))
      .filter(({ chat }) => chat.status === 'pending');

    for (const { index } of pendingChats) {
      await uploadChat(index);
    }
  };

  const getStatusIcon = (status: UploadedChat['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'uploading':
        return <div className="h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <MessageSquare className="h-5 w-5 text-gray-400" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Chat Files</h2>
        <p className="text-gray-600 mb-6">
          Upload chat exports from Discord, Slack, WhatsApp, or other platforms. Supports TXT, JSON, and CSV files.
        </p>

        {/* Platform Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-blue-900 mb-2">💡 How to export chats:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li><strong>Discord:</strong> Use DiscordChatExporter to export channels as JSON or TXT</li>
            <li><strong>WhatsApp:</strong> Go to chat → More → Export chat → Without media</li>
            <li><strong>Slack:</strong> Workspace Admin → Settings → Import/Export → Export Data</li>
            <li><strong>Telegram:</strong> Settings → Advanced → Export Telegram Data</li>
          </ul>
        </div>

        {/* Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Drop chat files here or click to browse
          </h3>
          <p className="text-gray-500 mb-4">
            Supports TXT, JSON, and CSV files up to 10MB
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt,.json,.csv"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Select Chat Files
          </button>
        </div>

        {/* Chat List */}
        {chats.length > 0 && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Chat Files ({chats.length})
              </h3>
              {chats.some(c => c.status === 'pending') && (
                <button
                  onClick={uploadAllChats}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  Upload All
                </button>
              )}
            </div>

            <div className="space-y-3">
              {chats.map((chatUpload, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3 flex-1">
                    {getStatusIcon(chatUpload.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {chatUpload.file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(chatUpload.file.size)}
                      </p>
                      {chatUpload.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${chatUpload.progress}%` }}
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Processing chat data...
                          </p>
                        </div>
                      )}
                      {chatUpload.error && (
                        <p className="text-sm text-red-600 mt-1">
                          {chatUpload.error}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {chatUpload.status === 'pending' && (
                      <button
                        onClick={() => uploadChat(index)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200"
                      >
                        Upload
                      </button>
                    )}
                    {chatUpload.status === 'error' && (
                      <button
                        onClick={() => uploadChat(index)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-orange-700 bg-orange-100 hover:bg-orange-200"
                      >
                        Retry
                      </button>
                    )}
                    <button
                      onClick={() => removeChat(index)}
                      className="inline-flex items-center p-1 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatUpload;