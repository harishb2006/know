// src/types/index.ts
export interface User {
  id: string;
  username: string;
  email: string;
}

export interface Document {
  id: string;
  filename: string;
  type: 'document' | 'chat';
  upload_date: string;
  file_size: number;
  content_preview?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UploadResponse {
  message: string;
}

export interface AskResponse {
  answer: string;
}