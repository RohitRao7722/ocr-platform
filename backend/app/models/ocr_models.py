from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


class Document(Base):
    """Document upload record"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)

    # OCR Results
    extracted_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    line_count = Column(Integer, nullable=True)
    ocr_lines = Column(JSON, nullable=True)  # Store bounding boxes and line details

    # Processing Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "extracted_text": self.extracted_text,
            "confidence": self.confidence,
            "line_count": self.line_count,
            "ocr_lines": self.ocr_lines,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
