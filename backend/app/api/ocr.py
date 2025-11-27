from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.ocr_service import ocr_service
from app.models.database import get_db
from app.models.ocr_models import Document


router = APIRouter(prefix="/api/ocr", tags=["OCR"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload a document for OCR processing

    Args:
        file: Document file (image or PDF)
        db: Database session

    Returns:
        Dict with upload status and file info
    """
    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{unique_id}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file
    try:
        contents = await file.read()

        # Check file size
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1048576}MB"
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        # Save to database
        document = Document(
            id=unique_id,
            original_filename=file.filename,
            stored_filename=safe_filename,
            file_path=file_path,
            file_size=len(contents),
            file_type=file_ext,
            status="uploaded"
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": unique_id,
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": len(contents)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/extract")
async def extract_text_from_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and immediately extract text from document

    Args:
        file: Document file (image or PDF)
        db: Database session

    Returns:
        Dict with extracted text and metadata
    """
    # First upload the file
    upload_result = await upload_document(file, db)

    if not upload_result["success"]:
        raise HTTPException(status_code=500, detail="File upload failed")

    # Get the document from database
    document_id = upload_result["file_id"]
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Extract text using OCR
    file_path = document.file_path

    try:
        # Update status to processing
        document.status = "processing"
        db.commit()

        ocr_result = ocr_service.extract_text(file_path)

        # Update document with OCR results
        document.extracted_text = ocr_result.get("text", "")
        document.confidence = ocr_result.get("confidence", 0.0)
        document.line_count = ocr_result.get("line_count", 0)
        document.ocr_lines = ocr_result.get("lines", [])
        document.status = "completed" if ocr_result["success"] else "failed"
        document.error_message = ocr_result.get("error")
        document.processed_at = datetime.now()

        db.commit()
        db.refresh(document)

        return {
            "success": ocr_result["success"],
            "file_id": document.id,
            "original_filename": document.original_filename,
            "extracted_text": document.extracted_text,
            "confidence": document.confidence,
            "line_count": document.line_count,
            "lines": document.ocr_lines,
            "status": document.status,
            "error": document.error_message,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        }

    except Exception as e:
        document.status = "failed"
        document.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict:
    """
    List all processed documents

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of documents with pagination
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    total = db.query(Document).count()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "documents": [doc.to_dict() for doc in documents]
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get a specific document by ID

    Args:
        document_id: Document UUID
        db: Database session

    Returns:
        Document details with OCR results
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document.to_dict()
