# System Architecture

## Overview

The OCR Platform follows a modern microservices architecture with separated frontend and backend, connected via RESTful APIs.

## Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        USER LAYER                             │
│   Browser (Chrome, Firefox, Safari, Edge)                     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS/HTTP
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   FRONTEND (React/Vite)                       │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  Components                                               │ │
│ │  - UploadZone  - ResultsDisplay  - DocumentHistory       │ │
│ │  - BatchUpload - ExportButtons   - Analytics             │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  State Management (React Hooks)                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  HTTP Client (Axios)                                     │ │
│ └──────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │ REST API (JSON)
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                       │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  Routers                                                  │ │
│ │  /api/ocr/*    /api/batch/*    /api/export/*            │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  Middleware                                               │ │
│ │  - CORS  - Authentication  - Error Handling  - Logging   │ │
│ └──────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌────────────────────┐          ┌────────────────────┐
│  SERVICE LAYER     │          │  BACKGROUND JOBS   │
│                    │          │                    │
│  OCR Service       │◄─────────┤  Celery Workers    │
│  - PaddleOCR       │          │  - Async OCR       │
│  - Tesseract       │          │  - Batch Process   │
│  - PDF Processing  │          │  - Cleanup Tasks   │
│                    │          │                    │
│  Export Service    │          └────────┬───────────┘
│  - TXT Generator   │                   │
│  - JSON Generator  │                   │ Redis Queue
│  - DOCX Generator  │                   │
│  - PDF Generator   │                   ▼
└────────┬───────────┘          ┌────────────────────┐
         │                      │    REDIS CACHE     │
         │                      │  - Task Queue      │
         │                      │  - Session Store   │
         │                      └────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│           DATA LAYER (PostgreSQL)          │
│ ┌────────────────────────────────────────┐ │
│ │  Tables                                 │ │
│ │  - documents (OCR results & metadata)   │ │
│ │  - alembic_version (migrations)         │ │
│ └────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────┐ │
│ │  Indexes                                │ │
│ │  - document_id, created_at, status      │ │
│ └────────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

## Request Flow

### Single Document Upload

```
1. User uploads file in React UI
   ↓
2. Frontend sends POST /api/ocr/extract with file
   ↓
3. FastAPI receives file, validates format/size
   ↓
4. Save file to disk (./uploads/)
   ↓
5. Create database record (status: "uploaded")
   ↓
6. OCR Service extracts text
   ├── Try PaddleOCR first
   └── Fallback to Tesseract if confidence < threshold
   ↓
7. Update database with results (status: "completed")
   ↓
8. Return JSON response to frontend
   ↓
9. Display results in UI
```

### Batch Upload

```
1. User uploads multiple files
   ↓
2. Frontend sends POST /api/batch/upload-multiple
   ↓
3. FastAPI iterates through files
   ↓
4. For each file:
   ├── Validate format
   ├── Save to disk
   ├── Process OCR
   └── Store results
   ↓
5. Return aggregated results
   {
     "successful": 8,
     "failed": 2,
     "results": [...]
   }
   ↓
6. Display batch results in UI
```

### PDF Processing (Parallel)

```
1. Receive PDF file
   ↓
2. Convert PDF to images (one per page)
   ↓
3. Create worker pool (CPU count - 1)
   ↓
4. Distribute pages across workers
   Worker 1: Page 1, 4, 7, ...
   Worker 2: Page 2, 5, 8, ...
   Worker 3: Page 3, 6, 9, ...
   ↓
5. Each worker runs PaddleOCR
   ↓
6. Aggregate results from all workers
   ↓
7. Return combined text with page markers
```

## Database Schema

### Documents Table

```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    original_filename VARCHAR NOT NULL,
    stored_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR NOT NULL,
    
    -- OCR Results
    extracted_text TEXT,
    confidence FLOAT,
    line_count INTEGER,
    ocr_lines JSONB,  -- Bounding boxes and coordinates
    
    -- Status
    status VARCHAR DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);
```

## Technology Decisions

### Why FastAPI?
- Modern async/await support
- Automatic API documentation
- Type validation with Pydantic
- High performance (comparable to NodeJS/Go)

### Why PaddleOCR + Tesseract?
- PaddleOCR: Superior accuracy for modern documents
- Tesseract: Reliable fallback, better for low-quality scans
- Dual-engine approach maximizes accuracy

### Why PostgreSQL?
- JSONB support for flexible OCR metadata
- Full-text search capabilities
- Proven reliability and performance
- Easy to scale

### Why Redis?
- Fast in-memory operations
- Perfect for task queues
- Session management
- Caching layer

### Why React?
- Component reusability
- Virtual DOM performance
- Large ecosystem
- Easy to maintain

## Scalability Considerations

### Horizontal Scaling
- Frontend: Deploy to CDN (Vercel/Netlify)
- Backend: Multiple API server instances behind load balancer
- Celery: Add more worker nodes
- Database: Read replicas for queries

### Vertical Scaling
- Increase CPU cores for parallel PDF processing
- Add RAM for larger file processing
- SSD storage for faster disk I/O

### Performance Optimizations
1. **Caching**: Redis cache for frequently accessed documents
2. **Lazy Loading**: Paginate document history
3. **Background Jobs**: Move heavy processing to Celery
4. **CDN**: Serve static assets from edge locations
5. **Database Indexing**: Optimize queries with proper indexes

## Security

### Current Implementation
- CORS configuration
- File type validation
- File size limits
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (React auto-escaping)

### Future Enhancements
- JWT authentication
- Rate limiting
- API key management
- File encryption at rest
- HTTPS enforcement

## Monitoring & Logging

### Logs
- Application logs: stdout/stderr
- Access logs: FastAPI middleware
- Error tracking: Structured JSON logs

### Metrics (Future)
- Request latency
- OCR processing time
- Error rates
- Queue depth
- Resource utilization

## Deployment Architecture

```
┌──────────────────────────────────────────┐
│  Vercel (Frontend)                        │
│  - Global CDN                             │
│  - Automatic HTTPS                        │
│  - Git-based deployments                  │
└────────────┬─────────────────────────────┘
             │ API Calls
             ▼
┌──────────────────────────────────────────┐
│  Render (Backend)                         │
│  ┌────────────────────────────────────┐  │
│  │  Docker Container                   │  │
│  │  - FastAPI                          │  │
│  │  - PaddleOCR                        │  │
│  │  - Tesseract                        │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Managed PostgreSQL                 │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Managed Redis                      │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## API Design Principles

1. **RESTful**: Standard HTTP methods (GET, POST, DELETE)
2. **Stateless**: Each request contains all necessary information
3. **JSON**: Consistent response format
4. **Error Handling**: Meaningful error messages with HTTP status codes
5. **Versioning**: API version in URL (/api/v1/...)
6. **Documentation**: Auto-generated OpenAPI/Swagger docs

## Future Architecture Enhancements

1. **Microservices**: Separate OCR service from API
2. **Message Queue**: RabbitMQ for more complex workflows
3. **Object Storage**: S3/MinIO for uploaded files
4. **Load Balancer**: Nginx/HAProxy for high availability
5. **Container Orchestration**: Kubernetes for production
6. **Monitoring**: Prometheus + Grafana
7. **APM**: Application Performance Monitoring (New Relic/DataDog)
