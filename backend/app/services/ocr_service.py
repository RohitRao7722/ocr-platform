from typing import Dict, List, Tuple, Optional
import cv2
import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
import logging
from multiprocessing import Pool, cpu_count
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OCRService:
    """Service for OCR text extraction using PaddleOCR and Tesseract with parallel processing"""

    def __init__(self):
        logger.info("🚀 Initializing OCR engines...")

        # Initialize PaddleOCR
        self.paddle_ocr = PaddleOCR(
            use_angle_cls=True,
            lang=settings.OCR_LANGUAGE,
            use_gpu=False,
            show_log=False
        )
        logger.info("✅ PaddleOCR engine initialized")

        # Configure Tesseract if enabled
        if settings.TESSERACT_ENABLED:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            logger.info(f"✅ Tesseract configured: {settings.TESSERACT_CMD}")
        else:
            logger.info("⚠️  Tesseract disabled in settings")

        # Get CPU count for parallel processing
        self.max_workers = max(1, cpu_count() - 1)  # Leave 1 core free
        logger.info(f"⚡ Parallel processing enabled: {self.max_workers} workers")

    def extract_text(self, file_path: str, engine: str = "auto") -> Dict:
        """
        Extract text from image or PDF using OCR

        Args:
            file_path: Path to the image or PDF file
            engine: OCR engine to use ("auto", "paddleocr", "tesseract")

        Returns:
            Dict containing extracted text, confidence, and coordinates
        """
        try:
            # Check if file is PDF
            if file_path.lower().endswith('.pdf'):
                logger.info(f"📄 Processing PDF: {os.path.basename(file_path)}")
                return self._extract_from_pdf_parallel(file_path, engine)
            else:
                logger.info(f"🖼️  Processing image: {os.path.basename(file_path)}")
                return self._extract_from_image_auto(file_path, engine)

        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {str(e)}")
            return {
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "engine_used": "none",
                "error": str(e)
            }

    def _process_single_page(self, args: Tuple) -> Dict:
        """
        Process a single PDF page (used for parallel processing)
        This is now a static method that creates its own OCR instance
        """
        image, page_num, temp_path, engine = args

        try:
            # Save page as temporary image
            temp_image_path = temp_path.replace('.pdf', f'_page{page_num}_temp.jpg')
            image.save(temp_image_path, 'JPEG')

            # Create OCR instance for this process
            from paddleocr import PaddleOCR
            paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                use_gpu=False,
                show_log=False
            )

            # Run OCR
            result = paddle_ocr.ocr(temp_image_path, cls=True)

            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            if not result or not result[0]:
                return {
                    "page_num": page_num,
                    "success": False,
                    "text": "",
                    "lines": [],
                    "confidence": 0.0,
                    "line_count": 0,
                    "engine_used": "none"
                }

            # Process results
            lines = []
            all_text = []
            total_confidence = 0.0

            for line in result[0]:
                box = line[0]
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]

                lines.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": [[float(x), float(y)] for x, y in box],
                    "page": page_num
                })

                all_text.append(text)
                total_confidence += confidence

            avg_confidence = total_confidence / len(lines) if lines else 0.0

            return {
                "page_num": page_num,
                "success": True,
                "text": "\n".join(all_text),
                "lines": lines,
                "confidence": float(avg_confidence),
                "line_count": len(lines),
                "engine_used": "paddleocr"
            }

        except Exception as e:
            logger.error(f"Error processing page {page_num}: {str(e)}")
            # Clean up temporary file on error
            temp_image_path = temp_path.replace('.pdf', f'_page{page_num}_temp.jpg')
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            return {
                "page_num": page_num,
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "line_count": 0,
                "engine_used": "none",
                "error": str(e)
            }

    def _extract_from_pdf_parallel(self, pdf_path: str, engine: str = "auto") -> Dict:
        """Extract text from all pages of PDF using parallel processing"""
        try:
            print(f"\n{'='*60}")
            print(f"📄 Processing PDF: {os.path.basename(pdf_path)}")
            print(f"{'='*60}")
            print("🔄 Converting PDF to images...")

            images = convert_from_path(pdf_path)

            if not images:
                print("❌ PDF conversion failed - no images generated")
                return {
                    "success": False,
                    "text": "",
                    "lines": [],
                    "confidence": 0.0,
                    "error": "Could not convert PDF to images"
                }

            print(f"✅ PDF converted successfully - {len(images)} pages found")
            worker_count = max(1, min(len(images), self.max_workers, 4))
            print(f"⚡ Processing pages in parallel with {worker_count} workers...")

            # Prepare arguments for parallel processing
            page_args = [
                (image, page_num, pdf_path, engine)
                for page_num, image in enumerate(images, start=1)
            ]

            # Process pages in parallel using Pool with spawn method
            from multiprocessing import get_context
            try:
                with get_context('spawn').Pool(processes=worker_count) as pool:
                    page_results = pool.map(_process_page_worker, page_args)
            except Exception as parallel_error:
                warning_msg = (
                    f"Parallel PDF processing failed ({parallel_error}). "
                    "Falling back to sequential execution."
                )
                print(f"⚠️  {warning_msg}")
                logger.warning(warning_msg)

                page_results = []
                for args in page_args:
                    page_results.append(_process_page_worker(args))

            # Sort results by page number
            page_results.sort(key=lambda x: x["page_num"])

            # Combine results
            all_pages_text = []
            all_pages_lines = []
            total_confidence = 0.0
            total_lines = 0
            engines_used = []

            for page_result in page_results:
                page_num = page_result["page_num"]

                if page_result["success"]:
                    lines_found = page_result["line_count"]
                    confidence = page_result["confidence"]
                    engine_used = page_result.get("engine_used", "unknown")
                    engines_used.append(f"Page {page_num}: {engine_used}")

                    print(f"   ✅ Page {page_num}: {lines_found} lines (confidence: {confidence:.1%}) - {engine_used}")

                    # Add page header
                    page_header = f"\n{'='*60}\nPAGE {page_num}\n{'='*60}\n"
                    all_pages_text.append(page_header + page_result["text"])

                    # Add lines
                    all_pages_lines.extend(page_result["lines"])

                    total_confidence += page_result["confidence"] * page_result["line_count"]
                    total_lines += page_result["line_count"]
                else:
                    print(f"   ⚠️  Page {page_num}: No text detected")

            # Calculate overall confidence
            avg_confidence = total_confidence / total_lines if total_lines > 0 else 0.0

            print(f"\n{'='*60}")
            print("✅ PDF Processing Complete!")
            print(f"   📊 Total Pages: {len(images)}")
            print(f"   📝 Total Lines: {total_lines}")
            print(f"   🎯 Overall Confidence: {avg_confidence:.1%}")
            print(f"   ⚡ Parallel Processing: {worker_count if page_results else 1} workers used")
            print(f"{'='*60}\n")

            logger.info(
                "PDF processing complete: %s pages, %s total lines, %.2f%% overall confidence",
                len(images),
                total_lines,
                avg_confidence * 100,
            )

            return {
                "success": True,
                "text": "\n".join(all_pages_text),
                "lines": all_pages_lines,
                "confidence": float(avg_confidence),
                "line_count": total_lines,
                "page_count": len(images),
                "engines_used": engines_used,
                "parallel_workers": worker_count if page_results else 1
            }

        except Exception as e:
            print(f"❌ PDF processing error: {str(e)}")
            logger.error(f"PDF processing error: {str(e)}")
            return {
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "error": f"PDF processing failed: {str(e)}"
            }

    def _extract_from_image_auto(self, image_path: str, engine: str = "auto") -> Dict:
        """Extract text with automatic fallback"""

        if engine == "tesseract":
            return self._extract_with_tesseract(image_path)

        if engine == "paddleocr":
            return self._extract_from_image(image_path)

        # Auto mode: try PaddleOCR first
        paddle_result = self._extract_from_image(image_path)

        # Check if PaddleOCR succeeded with good confidence
        if paddle_result["success"] and paddle_result["confidence"] >= settings.OCR_CONFIDENCE_THRESHOLD:
            paddle_result["engine_used"] = "paddleocr"
            return paddle_result

        # Fallback to Tesseract if enabled
        if settings.TESSERACT_ENABLED:
            tesseract_result = self._extract_with_tesseract(image_path)

            if tesseract_result["success"]:
                tesseract_result["engine_used"] = "tesseract (fallback)"
                return tesseract_result

        # Return PaddleOCR result even if low confidence
        paddle_result["engine_used"] = "paddleocr (no fallback)"
        return paddle_result

    def _extract_with_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract OCR"""
        try:
            img = Image.open(image_path)

            # Get detailed data with confidence
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            # Process results
            lines = []
            all_text = []
            total_confidence = 0.0
            valid_lines = 0

            for i, text in enumerate(data['text']):
                if text.strip():  # Only process non-empty text
                    conf = float(data['conf'][i])
                    if conf > 0:  # Valid confidence
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                        lines.append({
                            "text": text,
                            "confidence": conf / 100.0,  # Convert to 0-1 range
                            "bbox": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
                        })

                        all_text.append(text)
                        total_confidence += conf
                        valid_lines += 1

            avg_confidence = (total_confidence / valid_lines / 100.0) if valid_lines > 0 else 0.0

            return {
                "success": True,
                "text": " ".join(all_text),
                "lines": lines,
                "confidence": float(avg_confidence),
                "line_count": len(lines)
            }

        except Exception as e:
            logger.error(f"Tesseract error: {str(e)}")
            return {
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "error": str(e)
            }

    def _extract_from_image(self, image_path: str) -> Dict:
        """Extract text from image file using PaddleOCR"""
        try:
            # Run OCR
            result = self.paddle_ocr.ocr(image_path, cls=True)

            if not result or not result[0]:
                return {
                    "success": False,
                    "text": "",
                    "lines": [],
                    "confidence": 0.0,
                    "error": "No text detected"
                }

            # Process results
            lines = []
            all_text = []
            total_confidence = 0.0

            for line in result[0]:
                box = line[0]
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]

                lines.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": [[float(x), float(y)] for x, y in box]
                })

                all_text.append(text)
                total_confidence += confidence

            avg_confidence = total_confidence / len(lines) if lines else 0.0

            return {
                "success": True,
                "text": "\n".join(all_text),
                "lines": lines,
                "confidence": float(avg_confidence),
                "line_count": len(lines)
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "error": str(e)
            }


def _process_page_worker(args: Tuple) -> Dict:
    """Worker function for parallel page processing"""
    image, page_num, temp_path, engine = args

    try:
        temp_image_path = temp_path.replace('.pdf', f'_page{page_num}_temp.jpg')
        image.save(temp_image_path, 'JPEG')

        from paddleocr import PaddleOCR
        paddle_ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=False,
            show_log=False
        )

        result = paddle_ocr.ocr(temp_image_path, cls=True)

        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        if not result or not result[0]:
            return {
                "page_num": page_num,
                "success": False,
                "text": "",
                "lines": [],
                "confidence": 0.0,
                "line_count": 0,
                "engine_used": "none"
            }

        lines = []
        all_text = []
        total_confidence = 0.0

        for line in result[0]:
            box = line[0]
            text_info = line[1]
            text = text_info[0]
            confidence = text_info[1]

            lines.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": [[float(x), float(y)] for x, y in box],
                "page": page_num
            })

            all_text.append(text)
            total_confidence += confidence

        avg_confidence = total_confidence / len(lines) if lines else 0.0

        return {
            "page_num": page_num,
            "success": True,
            "text": "\n".join(all_text),
            "lines": lines,
            "confidence": float(avg_confidence),
            "line_count": len(lines),
            "engine_used": "paddleocr"
        }

    except Exception as e:
        temp_image_path = temp_path.replace('.pdf', f'_page{page_num}_temp.jpg')
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        return {
            "page_num": page_num,
            "success": False,
            "text": "",
            "lines": [],
            "confidence": 0.0,
            "line_count": 0,
            "engine_used": "none",
            "error": str(e)
        }


# Global OCR service instance
ocr_service = OCRService()
