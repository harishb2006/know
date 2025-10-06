// src/components/Dashboard/Dashboard.tsx
import React, { useState } from 'react';
import { Upload, MessageSquare, FileText, LogOut, Brain } from 'lucide-react';
import DocumentUpload from './DocumentUpload';
import ChatUpload from './ChatUpload';
import AskQuestion from './AskQuestion';
import DocumentList from './DocumentList';

interface DashboardProps {
  onLogout: () => void;
}

type TabType = 'upload' | 'chat-upload' | 'ask' | 'documents';

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState<TabType>('upload');

  const tabs = [
    { id: 'upload' as TabType, label: 'Upload Documents', icon: Upload },
    { id: 'chat-upload' as TabType, label: 'Upload Chats', icon: MessageSquare },
    { id: 'ask' as TabType, label: 'Ask Questions', icon: Brain },
    { id: 'documents' as TabType, label: 'My Documents', icon: FileText },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'upload':
        return <DocumentUpload />;
      case 'chat-upload':
        return <ChatUpload />;
      case 'ask':
        return <AskQuestion />;
      case 'documents':
        return <DocumentList />;
      default:
        return <DocumentUpload />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🧠 Knowledge Assistant</h1>
              <span className="ml-3 text-sm text-gray-500">Personal AI Knowledge Management</span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderTabContent()}
      </main>
    </div>
  );
};

export default Dashboard;