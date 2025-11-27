from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict
import os
import tempfile
from datetime import datetime
from app.models.database import get_db
from app.models.ocr_models import Document
from app.services.export_service import export_service

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/document/{document_id}/txt")
async def export_document_txt(
    document_id: str,
    db: Session = Depends(get_db)
) -> FileResponse:
    """Export document OCR results as plain text file"""

    # Get document from database
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    try:
        # Create temporary file
        output_filename = f"{document.original_filename.rsplit('.', 1)[0]}_ocr.txt"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)

        # Export to TXT
        export_service.export_to_txt(document.to_dict(), output_path)

        return FileResponse(
            output_path,
            media_type="text/plain",
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/document/{document_id}/json")
async def export_document_json(
    document_id: str,
    db: Session = Depends(get_db)
) -> FileResponse:
    """Export document OCR results as JSON file with metadata"""

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(statuscode=404, detail="Document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    try:
        output_filename = f"{document.original_filename.rsplit('.', 1)[0]}_ocr.json"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)

        export_service.export_to_json(document.to_dict(), output_path)

        return FileResponse(
            output_path,
            media_type="application/json",
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/document/{document_id}/docx")
async def export_document_docx(
    document_id: str,
    db: Session = Depends(get_db)
) -> FileResponse:
    """Export document OCR results as Microsoft Word document"""

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    try:
        output_filename = f"{document.original_filename.rsplit('.', 1)[0]}_ocr.docx"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)

        export_service.export_to_docx(document.to_dict(), output_path)

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/document/{document_id}/pdf")
async def export_document_pdf(
    document_id: str,
    db: Session = Depends(get_db)
) -> FileResponse:
    """Export document OCR results as PDF document"""

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    try:
        output_filename = f"{document.original_filename.rsplit('.', 1)[0]}_ocr.pdf"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)

        export_service.export_to_pdf(document.to_dict(), output_path)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
