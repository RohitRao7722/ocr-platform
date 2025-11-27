# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-27

### Added
- Initial release of OCR Platform
- Dual OCR engine support (PaddleOCR + Tesseract)
- Single document upload and processing
- Batch upload support (up to 10 files)
- ZIP archive processing (up to 20 files)
- Multi-format export (TXT, JSON, DOCX, PDF)
- Parallel PDF page processing
- Document history with filtering
- Confidence score analytics
- Real-time processing status
- Modern React UI with drag-and-drop
- RESTful API with FastAPI
- PostgreSQL database integration
- Redis caching and task queue
- Docker containerization
- Comprehensive API documentation
- Interactive Swagger UI

### Backend Features
- FastAPI REST API
- SQLAlchemy ORM with PostgreSQL
- Alembic database migrations
- Celery for background tasks
- PaddleOCR primary OCR engine
- Tesseract fallback OCR engine
- Automatic engine selection
- Bounding box detection
- Multi-language support

### Frontend Features
- React 18 with Vite
- Tailwind CSS styling
- react-dropzone for file upload
- Axios HTTP client
- Real-time result display
- Batch processing UI
- Document history table
- Export functionality
- Mobile-responsive design

### Documentation
- Comprehensive README
- API documentation
- Architecture guide
- Quick start guide
- Contributing guidelines
- MIT License

---

## [Unreleased]

### Planned Features
- User authentication (JWT)
- API rate limiting
- Webhook notifications
- Table extraction
- Handwritten text recognition
- Multi-language UI
- Mobile application
- Custom model training
- Advanced analytics dashboard
- Cloud storage integration (S3/MinIO)

---

## Version History

- **1.0.0** - Initial release with core OCR functionality
