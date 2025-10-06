// src/components/Dashboard/DocumentList.tsx
import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Search, Calendar, Filter } from 'lucide-react';
import { documentsAPI } from '../../services/api';
import type { Document } from '../../types';

const DocumentList: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'upload_date' | 'size'>('upload_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    filterAndSortDocuments();
  }, [documents, searchTerm, sortBy, sortOrder, selectedType]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.list();
      setDocuments(response);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortDocuments = () => {
    let filtered = documents.filter(doc => 
      doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.content_preview?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (selectedType !== 'all') {
      filtered = filtered.filter(doc => 
        doc.type?.toLowerCase() === selectedType.toLowerCase()
      );
    }

    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.filename.localeCompare(b.filename);
          break;
        case 'upload_date':
          comparison = new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime();
          break;
        case 'size':
          comparison = a.file_size - b.file_size;
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredDocuments(filtered);
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await documentsAPI.delete(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Failed to delete document. Please try again.');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFileIcon = () => {
    return <FileText className="h-5 w-5 text-blue-500" />;
  };

  const getUniqueFileTypes = () => {
    const types = new Set(documents.map(doc => doc.type).filter(Boolean));
    return Array.from(types);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading documents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border">
        {/* Header */}
        <div className="border-b p-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">My Documents</h2>
          
          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* File Type Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="pl-10 pr-8 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="all">All Types</option>
                {getUniqueFileTypes().map(type => (
                  <option key={type} value={type}>{type?.toUpperCase()}</option>
                ))}
              </select>
            </div>

            {/* Sort Options */}
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'upload_date' | 'size')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="upload_date">Date</option>
                <option value="name">Name</option>
                <option value="size">Size</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                title={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>

        {/* Documents List */}
        <div className="p-4">
          {filteredDocuments.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {documents.length === 0 ? 'No documents uploaded' : 'No documents match your search'}
              </h3>
              <p className="text-gray-500">
                {documents.length === 0 
                  ? 'Upload your first document to get started'
                  : 'Try adjusting your search terms or filters'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredDocuments.map((document) => (
                <div
                  key={document.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-4 flex-1 min-w-0">
                    {getFileIcon()}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {document.filename}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(document.upload_date)}
                        </span>
                        <span>{formatFileSize(document.file_size)}</span>
                        {document.type && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                            {document.type.toUpperCase()}
                          </span>
                        )}
                      </div>
                      {document.content_preview && (
                        <p className="text-sm text-gray-600 mt-1 truncate">
                          {document.content_preview}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDelete(document.id)}
                      className="inline-flex items-center p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md"
                      title="Delete document"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {filteredDocuments.length > 0 && (
          <div className="border-t p-4 text-sm text-gray-500">
            Showing {filteredDocuments.length} of {documents.length} documents
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentList;