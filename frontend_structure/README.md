# 🎨 Frontend Structure for Knowledge Assistant

This directory contains the recommended structure and components for building the Knowledge Assistant frontend.

## 📁 Recommended Project Structure

```
frontend/
├── 📦 package.json                 # Dependencies and scripts
├── 🔧 next.config.js               # Next.js configuration
├── 🎨 tailwind.config.js           # Tailwind CSS configuration
├── 📄 tsconfig.json               # TypeScript configuration
├── 
├── 📁 public/                     # Static assets
│   ├── 🖼️ favicon.ico
│   ├── 📱 manifest.json
│   └── 🖼️ icons/
├── 
├── 📁 src/                        # Source code
│   ├── 📁 app/                    # App Router (Next.js 13+)
│   │   ├── 🏠 page.tsx            # Home page
│   │   ├── 🎨 layout.tsx          # Root layout
│   │   ├── 🌐 globals.css         # Global styles
│   │   ├── 
│   │   ├── 📁 upload/             # File upload page
│   │   │   └── 📄 page.tsx
│   │   ├── 
│   │   ├── 📁 chat/               # Chat interface
│   │   │   └── 📄 page.tsx
│   │   ├── 
│   │   ├── 📁 documents/          # Document management
│   │   │   ├── 📄 page.tsx
│   │   │   └── 📁 [id]/
│   │   │       └── 📄 page.tsx
│   │   ├── 
│   │   └── 📁 public/             # Public document viewer
│   │       └── 📁 [token]/
│   │           └── 📄 page.tsx
│   ├── 
│   ├── 📁 components/             # Reusable components
│   │   ├── 🧩 ui/                 # Basic UI components
│   │   │   ├── 🔘 Button.tsx
│   │   │   ├── 📝 Input.tsx
│   │   │   ├── 📋 Card.tsx
│   │   │   ├── 🔄 Loading.tsx
│   │   │   └── 🚨 Alert.tsx
│   │   ├── 
│   │   ├── 📤 FileUpload.tsx      # File upload component
│   │   ├── 💬 ChatInterface.tsx   # Chat UI component
│   │   ├── 📄 DocumentViewer.tsx  # Document display component
│   │   ├── 🔍 SearchResults.tsx   # Search results display
│   │   ├── 🔗 PublicShare.tsx     # Public sharing component
│   │   └── 📊 SourceAttribution.tsx # Source citation display
│   ├── 
│   ├── 📁 lib/                    # Utilities and API
│   │   ├── 🌐 api.ts              # API client functions
│   │   ├── 🔧 utils.ts            # Utility functions
│   │   ├── 🎯 types.ts            # TypeScript type definitions
│   │   └── 🗂️ constants.ts        # App constants
│   ├── 
│   ├── 📁 hooks/                  # Custom React hooks
│   │   ├── 📤 useFileUpload.ts
│   │   ├── 💬 useChat.ts
│   │   ├── 🔍 useDocumentSearch.ts
│   │   └── 🔗 usePublicShare.ts
│   ├── 
│   └── 📁 store/                  # State management
│       ├── 🗄️ index.ts            # Store configuration
│       ├── 📄 documentSlice.ts    # Document state
│       ├── 💬 chatSlice.ts        # Chat state
│       └── 👤 userSlice.ts        # User state
└── 
└── 📁 docs/                      # Documentation
    ├── 📖 SETUP.md               # Setup instructions
    ├── 🎨 DESIGN.md              # Design system
    └── 🧩 COMPONENTS.md          # Component documentation
```

## 🚀 Quick Start

### 1. Initialize Next.js Project
```bash
npx create-next-app@latest knowledge-assistant-frontend --typescript --tailwind --app
cd knowledge-assistant-frontend
```

### 2. Install Additional Dependencies
```bash
npm install @reduxjs/toolkit react-redux axios react-dropzone react-markdown
npm install lucide-react @headlessui/react @heroicons/react
npm install react-hook-form @hookform/resolvers zod
npm install react-hot-toast framer-motion
```

### 3. Development Dependencies
```bash
npm install -D @types/node eslint prettier eslint-config-prettier
```

## 🧩 Key Components

### FileUpload Component
Handles file uploads with drag-and-drop, progress tracking, and validation.

### ChatInterface Component
Provides chat UI with message history, typing indicators, and source attribution.

### DocumentViewer Component
Displays documents with syntax highlighting, PDF viewing, and image display.

### SourceAttribution Component
Shows source citations with confidence scores and links to original documents.

### SearchResults Component
Displays search results with relevance scores and document previews.

## 🎨 Design System

### Colors
- Primary: Blue (#3B82F6)
- Secondary: Green (#10B981)
- Accent: Purple (#8B5CF6)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Gray scales for text and backgrounds

### Typography
- Headings: Inter font family
- Body: System font stack
- Code: JetBrains Mono

### Spacing
- Base unit: 4px
- Scale: 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64

## 📱 Responsive Design

### Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### Layout Strategy
- Mobile-first approach
- Progressive enhancement
- Touch-friendly interfaces

## 🔌 API Integration

### Base API Configuration
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Example API Hooks
```typescript
// useFileUpload.ts
export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  
  const uploadFile = async (file: File, isPublic: boolean) => {
    setUploading(true);
    // Upload logic
  };
  
  return { uploadFile, uploading };
};

// useChat.ts
export const useChat = (sessionId: string) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (message: string, mode: string) => {
    // Chat logic
  };
  
  return { messages, sendMessage, loading };
};
```

## 🎭 Example Pages

### Upload Page Features
- Drag and drop file upload
- File type validation
- Upload progress tracking
- Public/private toggle
- Batch upload support

### Chat Page Features
- Message history
- Multiple chat modes
- Source attribution display
- Confidence indicators
- Export conversations

### Document Management Features
- Document list with search
- File type filtering
- Public share management
- Document preview
- Batch operations

### Public Document Viewer Features
- Secure token-based access
- Document preview
- Download functionality
- Mobile-optimized viewing
- Social sharing

## 🧪 Testing Strategy

### Unit Tests
- Component testing with Jest and React Testing Library
- Hook testing
- Utility function testing

### Integration Tests
- API integration testing
- User flow testing
- Cross-browser testing

### E2E Tests
- Complete user workflows
- File upload and processing
- Chat functionality
- Public sharing

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run start
```

### Environment Variables
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Knowledge Assistant
NEXT_PUBLIC_MAX_FILE_SIZE=10485760
```

## 📊 Performance Considerations

### Optimization Strategies
- Code splitting with dynamic imports
- Image optimization with Next.js Image component
- API response caching
- Virtual scrolling for large lists
- Lazy loading of components

### Bundle Analysis
```bash
npm install -D @next/bundle-analyzer
npm run analyze
```

## 🔒 Security

### Client-Side Security
- Input validation and sanitization
- XSS prevention
- CSRF protection
- Secure token handling

### File Upload Security
- File type validation
- Size limits
- Content scanning
- Secure file storage

## 📈 Analytics and Monitoring

### User Analytics
- File upload tracking
- Chat interaction metrics
- Document view analytics
- Error tracking

### Performance Monitoring
- Core Web Vitals
- API response times
- Bundle size monitoring
- User experience metrics

---

This structure provides a solid foundation for building a modern, responsive frontend for the Knowledge Assistant system. Each component can be implemented progressively, starting with basic functionality and adding advanced features over time.