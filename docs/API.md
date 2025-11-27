# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-api-domain.com`

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

---

## Endpoints

### Health Check

#### GET `/`
Root endpoint returning API status.

**Response:**
```json
{
  "message": "Welcome to OCR Platform",
  "version": "1.0.0",
  "status": "running"
}
```

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

## OCR Operations

### Single Document Upload & Extract

#### POST `/api/ocr/extract`

Upload a document and immediately extract text.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (required): Document file (PDF, PNG, JPG, JPEG, TIFF, BMP)

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/ocr/extract \
  -F "file=@document.pdf"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/ocr/extract', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

**Response (200 OK):**
```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "invoice.pdf",
  "extracted_text": "Invoice\nDate: 2024-01-15\nTotal: $1,234.56\n...",
  "confidence": 0.967,
  "line_count": 42,
  "lines": [
    {
      "text": "Invoice",
      "confidence": 0.99,
      "bbox": [[10, 20], [100, 20], [100, 40], [10, 40]]
    },
    ...
  ],
  "status": "completed",
  "error": null,
  "processed_at": "2024-01-15T10:30:45.123Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "File type not allowed. Supported: pdf, png, jpg, jpeg, tiff, bmp"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "OCR processing failed: [error details]"
}
```

---

### List All Documents

#### GET `/api/ocr/documents`

Retrieve a list of all processed documents.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Example:**
```bash
GET /api/ocr/documents?skip=0&limit=20
```

**Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "original_filename": "invoice.pdf",
      "stored_filename": "20240115_103045_uuid.pdf",
      "file_type": "pdf",
      "file_size": 245760,
      "confidence": 0.967,
      "line_count": 42,
      "status": "completed",
      "created_at": "2024-01-15T10:30:45.123Z",
      "processed_at": "2024-01-15T10:30:47.456Z"
    },
    ...
  ],
  "total": 156,
  "skip": 0,
  "limit": 20
}
```

---

### Get Single Document

#### GET `/api/ocr/documents/{document_id}`

Retrieve details of a specific document.

**Path Parameters:**
- `document_id` (required): UUID of the document

**Example:**
```bash
GET /api/ocr/documents/550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "invoice.pdf",
  "stored_filename": "20240115_103045_uuid.pdf",
  "file_path": "/app/uploads/20240115_103045_uuid.pdf",
  "file_type": "pdf",
  "file_size": 245760,
  "extracted_text": "Full extracted text...",
  "confidence": 0.967,
  "line_count": 42,
  "ocr_lines": [...],
  "status": "completed",
  "error_message": null,
  "created_at": "2024-01-15T10:30:45.123Z",
  "processed_at": "2024-01-15T10:30:47.456Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Document not found"
}
```

---

## Batch Operations

### Batch Upload Multiple Files

#### POST `/api/batch/upload-multiple`

Upload and process multiple files simultaneously (max 10 files).

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `files` (required): Array of document files

**Example (JavaScript):**
```javascript
const formData = new FormData();
files.forEach(file => {
  formData.append('files', file);
});

const response = await fetch('http://localhost:8000/api/batch/upload-multiple', {
  method: 'POST',
  body: formData
});
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Batch upload complete: 8 successful, 2 failed",
  "total_files": 10,
  "successful": 8,
  "failed": 2,
  "results": [
    {
      "filename": "invoice1.pdf",
      "success": true,
      "file_id": "550e8400-e29b-41d4-a716-446655440001",
      "confidence": 0.967,
      "line_count": 42,
      "extracted_text_preview": "Invoice\nDate: 2024-01-15..."
    },
    {
      "filename": "corrupted.pdf",
      "success": false,
      "error": "Failed to read PDF file"
    },
    ...
  ]
}
```

---

### Upload ZIP Archive

#### POST `/api/batch/upload-zip`

Upload a ZIP file containing multiple documents (max 20 files).

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (required): ZIP archive file

**Response (200 OK):**
```json
{
  "success": true,
  "message": "ZIP processing complete: 18 successful, 2 failed",
  "total_files": 20,
  "successful": 18,
  "failed": 2,
  "results": [...]
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "ZIP contains more than 20 files. Maximum allowed is 20."
}
```

---

### Bulk Delete Documents

#### DELETE `/api/batch/documents/bulk`

Delete multiple documents at once (max 50 documents).

**Request:**
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "document_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Bulk delete complete: 2 deleted, 0 failed",
  "deleted": 2,
  "failed": 0
}
```

---

## Export Operations

### Export Document

#### GET `/api/export/document/{document_id}/{format}`

Export a processed document in the specified format.

**Path Parameters:**
- `document_id` (required): UUID of the document
- `format` (required): Export format (`txt`, `json`, `docx`, `pdf`)

**Examples:**
```bash
# Export as plain text
GET /api/export/document/550e8400-e29b-41d4-a716-446655440000/txt

# Export as JSON
GET /api/export/document/550e8400-e29b-41d4-a716-446655440000/json

# Export as Word document
GET /api/export/document/550e8400-e29b-41d4-a716-446655440000/docx

# Export as PDF
GET /api/export/document/550e8400-e29b-41d4-a716-446655440000/pdf
```

**Response:**
- **Content-Type**: Varies based on format
  - `txt`: `text/plain`
  - `json`: `application/json`
  - `docx`: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `pdf`: `application/pdf`
- **Body**: File content

**Error Response (404 Not Found):**
```json
{
  "detail": "Document not found"
}
```

---

## Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| **200** | Success | Request processed successfully |
| **400** | Bad Request | Invalid file type, file too large |
| **404** | Not Found | Document not found |
| **500** | Internal Server Error | OCR processing failed, database error |

---

## Rate Limiting

Currently, there are no rate limits. Future versions will implement:
- 100 requests per minute for single uploads
- 10 requests per minute for batch operations

---

## CORS Policy

The API allows requests from all origins in development. In production, configure `CORS_ORIGINS` in environment variables.

---

## Interactive API Documentation

Once the backend is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all available endpoints
- See request/response schemas
- Try API calls directly from the browser
- Download OpenAPI specification

---

## Code Examples

### Python

```python
import requests

# Single upload
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/ocr/extract', files=files)
    result = response.json()
    print(f"Extracted text: {result['extracted_text']}")

# Batch upload
files = [
    ('files', open('doc1.pdf', 'rb')),
    ('files', open('doc2.pdf', 'rb')),
]
response = requests.post('http://localhost:8000/api/batch/upload-multiple', files=files)
result = response.json()
print(f"Successful: {result['successful']}, Failed: {result['failed']}")
```

### JavaScript/Fetch

```javascript
// Single upload
async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/ocr/extract', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Get documents
async function getDocuments() {
  const response = await fetch('http://localhost:8000/api/ocr/documents?limit=20');
  return await response.json();
}
```

### cURL

```bash
# Upload document
curl -X POST http://localhost:8000/api/ocr/extract \
  -F "file=@document.pdf"

# Get documents
curl http://localhost:8000/api/ocr/documents

# Export as JSON
curl http://localhost:8000/api/export/document/{doc_id}/json \
  -o output.json

# Delete documents
curl -X DELETE http://localhost:8000/api/batch/documents/bulk \
  -H "Content-Type: application/json" \
  -d '{"document_ids": ["uuid1", "uuid2"]}'
```

---

## Webhooks (Future Feature)

Future versions will support webhooks to notify your application when OCR processing is complete:

```json
POST https://your-webhook-url.com/ocr-complete
{
  "event": "ocr.completed",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "confidence": 0.967,
  "timestamp": "2024-01-15T10:30:47.456Z"
}
```
