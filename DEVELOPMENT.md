# Development Configuration

## Environment Setup

### Required Environment Variables
```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Configuration  
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/knowledge_db

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Development Commands

#### Backend
```bash
# Start backend with auto-reload
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest backend/tests/

# Format code
black backend/
```

#### Frontend
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Format code
npm run format
```

## Project Standards

### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use Prettier for formatting, strict TypeScript config
- **Imports**: Absolute imports, organized by external/internal

### Commit Messages
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
- Keep messages concise and descriptive

### File Organization
- **Backend**: Separate models, services, and API routes
- **Frontend**: Component-based architecture with TypeScript
- **Tests**: Mirror the source code structure

### Documentation
- Update README for major changes
- Document API endpoints
- Add inline comments for complex logic