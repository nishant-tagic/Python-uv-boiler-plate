from typing import Optional
from fastapi import UploadFile

from app.validators.file_validator import FileValidator
from app.handlers.processors.image_processor import ImageProcessor
from app.handlers.processors.pdf_processor import PDFProcessor
from app.handlers.processors.spreadsheet_processor import SpreadsheetProcessor
from app.config.FileConfig import FileConfig
from app.core.logging import get_logger  # ✅ import logger


class FileUploadHandler:
    def __init__(self):
        self.validator = FileValidator()
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        self.spreadsheet_processor = SpreadsheetProcessor()
        self.logger = get_logger(__name__)

    async def validate_and_process(
        self,
        file: UploadFile,
        allowed_types: Optional[set] = None,
        max_size: Optional[int] = None,
        process_file: bool = True,
    ) -> dict:
        self.logger.info("Validating file", filename=file.filename)

        self.validator.validate_extension(file.filename)
        safe_name = self.validator.sanitize_filename(file.filename)
        unique_name = self.validator.generate_unique_filename(file.filename)
        mime_type = await self.validator.validate_mime_type(file, allowed_types)
        size = await self.validator.validate_file_size(file, max_size)
        file_type = self.validator.get_file_type(mime_type)

        info = {
            "original_filename": file.filename,
            "safe_filename": safe_name,
            "unique_filename": unique_name,
            "mime_type": mime_type,
            "file_type": file_type.value
            if hasattr(file_type, "value")
            else str(file_type),
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 2),
        }

        self.logger.debug("File basic info collected", **info)

        if process_file:
            try:
                if file_type.value == "image":
                    w, h = await self.image_processor.validate_image(file)
                    info["dimensions"] = {"width": w, "height": h}
                    self.logger.info("Image validated", dimensions=info["dimensions"])
                elif file_type.value == "pdf":
                    pages = await self.pdf_processor.validate_pdf(file)
                    info["page_count"] = pages
                    self.logger.info("PDF validated", pages=pages)
                elif file_type.value in ["csv", "excel"]:
                    info["validated"] = True
                    self.logger.info("Spreadsheet validated", filename=file.filename)
            except Exception as e:
                self.logger.error(
                    "File processing failed",
                    filename=file.filename,
                    error=str(e),
                )
                raise

        return info

    async def save_temp_file(self, file: UploadFile, filename: str):
        file_path = FileConfig.TEMP_UPLOAD_DIR / filename
        content = await file.read()
        await file.seek(0)
        with open(file_path, "wb") as f:
            f.write(content)

        self.logger.info("File saved temporarily", file_path=str(file_path))
        return file_path

file_handler = FileUploadHandler()
