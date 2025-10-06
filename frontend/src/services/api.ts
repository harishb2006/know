// src/services/api.ts
import axios from 'axios';
import type { AuthResponse, UploadResponse, AskResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (username: string, email: string, password: string): Promise<void> => {
    await api.post('/register', { username, email, password });
  },

  login: async (username: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/login', { username, password });
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  upload: (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  uploadDocument: (formData: FormData, onUploadProgress?: (progressEvent: { loaded: number; total?: number }) => void): Promise<UploadResponse> => {
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },

  uploadChat: (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload-chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  list: (): Promise<Document[]> => {
    return api.get('/documents');
  },

  delete: (documentId: string): Promise<void> => {
    return api.delete(`/documents/${documentId}`);
  },
};

export const chatAPI = {
  ask: async (question: string): Promise<AskResponse> => {
    const response = await api.post('/ask', { question });
    return response.data;
  },
};

export default api;