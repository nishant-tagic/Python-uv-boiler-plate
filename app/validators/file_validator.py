import os
import uuid
from datetime import datetime
from typing import Optional
import magic
from fastapi import UploadFile, HTTPException, status

from app.config.FileConfig import FileConfig
from app.enums.file_type import FileType


class FileValidator:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        filename = os.path.basename(filename)
        filename = filename.replace(" ", "_")
        safe_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        )
        return "".join(c for c in filename if c in safe_chars)

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        sanitized = FileValidator.sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}_{unique_id}{ext}"

    @staticmethod
    def validate_extension(filename: str) -> None:
        ext = os.path.splitext(filename)[1].lower()
        if ext in FileConfig.BLOCKED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not allowed",
            )

    @staticmethod
    async def detect_mime_type(file: UploadFile) -> str:
        content = await file.read(2048)
        await file.seek(0)
        return magic.from_buffer(content, mime=True)

    @staticmethod
    async def validate_mime_type(
        file: UploadFile, allowed_types: Optional[set] = None
    ) -> str:
        actual_mime = await FileValidator.detect_mime_type(file)
        if allowed_types is None:
            allowed_types = FileConfig.get_all_allowed_types()
        if actual_mime not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{actual_mime}' is not allowed",
            )
        return actual_mime

    @staticmethod
    async def validate_file_size(
        file: UploadFile, max_size: Optional[int] = None
    ) -> int:
        if max_size is None:
            max_size = FileConfig.MAX_FILE_SIZE

        # Read the entire file to get its size
        # UploadFile.seek() doesn't support whence parameter
        content = await file.read()
        size = len(content)
        await file.seek(0)  # Reset to beginning

        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File size exceeds {max_size / (1024 * 1024):.2f}MB",
            )
        return size

    @staticmethod
    def get_file_type(mime_type: str) -> FileType:
        if mime_type in FileConfig.ALLOWED_IMAGE_TYPES:
            return FileType.IMAGE
        elif mime_type in FileConfig.ALLOWED_DOCUMENT_TYPES:
            return FileType.PDF if mime_type == "application/pdf" else FileType.DOCUMENT
        elif mime_type in FileConfig.ALLOWED_SPREADSHEET_TYPES:
            return FileType.CSV if mime_type == "text/excel" else FileType.EXCEL
        elif mime_type in FileConfig.ALLOWED_VIDEO_TYPES:
            return FileType.VIDEO
        elif mime_type in FileConfig.ALLOWED_AUDIO_TYPES:
            return FileType.AUDIO
        elif mime_type in FileConfig.ALLOWED_ARCHIVE_TYPES:
            return FileType.ARCHIVE
        return FileType.OTHER
