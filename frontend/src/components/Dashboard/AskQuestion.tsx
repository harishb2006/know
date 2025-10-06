// src/components/Dashboard/AskQuestion.tsx
import React, { useState } from 'react';
import { Send, Brain, Loader, Copy, Check } from 'lucide-react';
import { chatAPI } from '../../services/api';

interface ChatMessage {
  id: string;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
}

const AskQuestion: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    const questionMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'question',
      content: question.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, questionMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await chatAPI.ask(questionMessage.content);
      
      const answerMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'answer',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, answerMessage]);
    } catch (error) {
      console.error('Error asking question:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'answer',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const clearChat = () => {
    setMessages([]);
  };

  const suggestedQuestions = [
    "What are the main topics in my documents?",
    "Summarize the key points from my uploaded files",
    "What questions can I ask based on my knowledge base?",
    "Find information about specific topics in my documents",
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border">
        {/* Header */}
        <div className="border-b p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="h-6 w-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Ask Questions</h2>
            </div>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Clear Chat
              </button>
            )}
          </div>
          <p className="text-gray-600 mt-2">
            Ask questions about your uploaded documents and chat files. I'll search through your knowledge base to provide answers.
          </p>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto max-h-96 p-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to help!
              </h3>
              <p className="text-gray-500 mb-6">
                Ask me anything about your uploaded documents and chat files.
              </p>
              
              {/* Suggested Questions */}
              <div className="max-w-lg mx-auto">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Try asking:</h4>
                <div className="grid gap-2">
                  {suggestedQuestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setQuestion(suggestion)}
                      className="text-left px-4 py-2 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'question' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg px-4 py-3 ${
                      message.type === 'question'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        <p
                          className={`text-xs mt-2 ${
                            message.type === 'question' ? 'text-blue-100' : 'text-gray-500'
                          }`}
                        >
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                      {message.type === 'answer' && (
                        <button
                          onClick={() => copyToClipboard(message.content, message.id)}
                          className="ml-3 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                          title="Copy to clipboard"
                        >
                          {copiedId === message.id ? (
                            <Check className="h-4 w-4 text-green-500" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <Loader className="h-4 w-4 text-gray-500 animate-spin" />
                      <span className="text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Form */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AskQuestion;