from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import os
import uuid
import zipfile
import io
from datetime import datetime
from app.models.database import get_db
from app.models.ocr_models import Document
from app.services.ocr_service import ocr_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/batch", tags=["Batch Operations"])


@router.post("/upload-multiple")
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and process multiple files at once
    
    Args:
        files: List of files to upload
        
    Returns:
        Summary of batch upload with individual file results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 10 files allowed per batch upload"
        )
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Validate file type
            file_extension = os.path.splitext(file.filename)[1].lower()
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
            
            if file_extension not in allowed_extensions:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Unsupported file type: {file_extension}"
                })
                failed += 1
                continue
            
            # Save uploaded file
            file_id = str(uuid.uuid4())
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_extension}")
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Get file size
            file_size = len(content)
            
            # Process OCR
            logger.info(f"Processing batch file: {file.filename}")
            ocr_result = ocr_service.extract_text(file_path)
            
            if ocr_result["success"]:
                # Save to database
                document = Document(
                    id=file_id,
                    original_filename=file.filename,
                    stored_filename=f"{file_id}{file_extension}",
                    file_path=file_path,
                    file_type=file_extension[1:],
                    file_size=file_size,
                    extracted_text=ocr_result["text"],
                    confidence=ocr_result["confidence"],
                    line_count=ocr_result["line_count"],
                    status="completed"
                )
                db.add(document)
                db.commit()
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "file_id": file_id,
                    "confidence": ocr_result["confidence"],
                    "line_count": ocr_result["line_count"],
                    "extracted_text_preview": ocr_result["text"][:200]
                })
                successful += 1
            else:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": ocr_result.get("error", "OCR processing failed")
                })
                failed += 1
                
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
            failed += 1
    
    return {
        "success": True,
        "message": f"Batch upload complete: {successful} successful, {failed} failed",
        "total_files": len(files),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@router.post("/upload-zip")
async def batch_upload_zip(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload a ZIP file and process all supported files inside
    
    Args:
        file: ZIP file containing documents
        
    Returns:
        Summary of extracted and processed files
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    
    try:
        # Read ZIP file
        content = await file.read()
        zip_buffer = io.BytesIO(content)
        
        results = []
        successful = 0
        failed = 0
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            
            if len(file_list) > 20:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP contains more than 20 files. Maximum allowed is 20."
                )
            
            for filename in file_list:
                # Skip directories and hidden files
                if filename.endswith('/') or filename.startswith('.') or filename.startswith('__MACOSX'):
                    continue
                
                file_extension = os.path.splitext(filename)[1].lower()
                allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
                
                if file_extension not in allowed_extensions:
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": f"Unsupported file type: {file_extension}"
                    })
                    failed += 1
                    continue
                
                try:
                    # Extract file
                    file_data = zip_ref.read(filename)
                    
                    # Save to disk
                    file_id = str(uuid.uuid4())
                    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_extension}")
                    
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                    
                    # Process OCR
                    logger.info(f"Processing ZIP file: {filename}")
                    ocr_result = ocr_service.extract_text(file_path)
                    
                    if ocr_result["success"]:
                        # Save to database
                        document = Document(
                            id=file_id,
                            original_filename=filename,
                            stored_filename=f"{file_id}{file_extension}",
                            file_path=file_path,
                            file_type=file_extension[1:],
                            file_size=len(file_data),
                            extracted_text=ocr_result["text"],
                            confidence=ocr_result["confidence"],
                            line_count=ocr_result["line_count"],
                            status="completed"
                        )
                        db.add(document)
                        db.commit()
                        
                        results.append({
                            "filename": filename,
                            "success": True,
                            "file_id": file_id,
                            "confidence": ocr_result["confidence"],
                            "line_count": ocr_result["line_count"]
                        })
                        successful += 1
                    else:
                        results.append({
                            "filename": filename,
                            "success": False,
                            "error": ocr_result.get("error", "OCR processing failed")
                        })
                        failed += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": str(e)
                    })
                    failed += 1
        
        return {
            "success": True,
            "message": f"ZIP processing complete: {successful} successful, {failed} failed",
            "total_files": len(file_list),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        logger.error(f"ZIP processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ZIP processing failed: {str(e)}")


@router.delete("/documents/bulk")
async def bulk_delete_documents(
    document_ids: List[str],
    db: Session = Depends(get_db)
) -> Dict:
    """
    Delete multiple documents at once
    
    Args:
        document_ids: List of document IDs to delete
        
    Returns:
        Summary of deletion operation
    """
    if len(document_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 documents can be deleted at once")
    
    deleted = 0
    failed = 0
    
    for doc_id in document_ids:
        try:
            document = db.query(Document).filter(Document.id == doc_id).first()
            
            if document:
                # Delete file from disk
                if os.path.exists(document.file_path):
                    os.remove(document.file_path)
                
                # Delete from database
                db.delete(document)
                db.commit()
                deleted += 1
            else:
                failed += 1
                
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            failed += 1
    
    return {
        "success": True,
        "message": f"Bulk delete complete: {deleted} deleted, {failed} failed",
        "deleted": deleted,
        "failed": failed
    }
