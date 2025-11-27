# Quick Start Guide

Get the OCR Platform running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- (Optional) Node.js 18+ for local frontend development

---

## 🚀 Option 1: Docker (Recommended)

Perfect for quickly testing the full application.

### Steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ocr-platform.git
   cd ocr-platform
   ```

2. **Configure environment (optional)**
   ```bash
   # Backend environment is already configured for Docker
   # If you need custom settings:
   cp backend/.env.example backend/.env
   # Edit backend/.env as needed
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```
   
   This will start:
   - ✅ PostgreSQL database
   - ✅ Redis cache
   - ✅ FastAPI backend
   - ✅ Celery workers

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 💻 Option 2: Local Development

For active development work on the codebase.

### Backend Setup:

1. **Navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Activate on Windows
   .venv\Scripts\activate
   
   # Activate on macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env - change database/redis URLs to localhost
   ```

5. **Start PostgreSQL and Redis**
   ```bash
   # Option A: Use Docker for just the databases
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=ocr_password -e POSTGRES_USER=ocr_user -e POSTGRES_DB=ocr_db postgres:15-alpine
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Option B: Install locally
   # Install PostgreSQL and Redis on your system
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup:

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access frontend**
   - http://localhost:5173

---

## ✅ Verify Installation

1. **Check backend health**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "environment": "development"
   }
   ```

2. **Check API documentation**
   - Open http://localhost:8000/docs
   - You should see the Swagger UI

3. **Test file upload**
   - Open http://localhost:5173
   - Drag and drop an image or PDF
   - Click "Run Extraction"
   - View the extracted text

---

## 🧪 Test with Sample Files

Create a test image with text:

```bash
# On macOS/Linux
echo "Hello World" | convert label:@- test.png

# On Windows
# Use any image with text or download a sample invoice PDF
```

Upload via UI or API:

```bash
curl -X POST http://localhost:8000/api/ocr/extract \
  -F "file=@test.png"
```

---

## 🛑 Stopping Services

### Docker:
```bash
docker-compose down
```

### Local Development:
```bash
# Stop backend: Ctrl+C in the terminal running uvicorn
# Stop frontend: Ctrl+C in the terminal running npm
# Stop databases: docker stop <container_id>
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Problem**: `Error: Port 8000 is already in use`

**Solution**:
```bash
# Find and kill the process using the port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
1. Ensure PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```
2. Check DATABASE_URL in `.env`
3. Verify database credentials

### Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'paddleocr'`

**Solution**:
```bash
# Ensure you're in the virtual environment
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Build Errors

**Problem**: `npm ERR! code ELIFECYCLE`

**Solution**:
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Next Steps

- Read the [Architecture Documentation](docs/ARCHITECTURE.md)
- Explore the [API Documentation](docs/API.md)
- Check the [Contributing Guidelines](CONTRIBUTING.md)
- Try the batch upload feature
- Export results in different formats

---

## 🆘 Need Help?

- Check [README.md](README.md) for detailed information
- Review [API Documentation](docs/API.md)
- Open an issue on GitHub
- Check existing issues for solutions

---

**Happy Coding! 🚀**
