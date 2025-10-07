from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class FileTypeEnum(str, Enum):
    """File type categories"""
    IMAGE = "image"
    PDF = "pdf"
    # CSV = "csv"
    EXCEL = "excel"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


class ImageDimensions(BaseModel):
    """Image dimensions"""
    width: int = Field(..., gt=0, description="Image width in pixels")
    height: int = Field(..., gt=0, description="Image height in pixels")


class PDFMetadata(BaseModel):
    """PDF file metadata"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    pages: int = Field(..., ge=1)


class FileInfoSchema(BaseModel):
    """Base file information schema"""
    original_filename: str = Field(..., description="Original uploaded filename")
    safe_filename: str = Field(..., description="Sanitized filename")
    unique_filename: str = Field(..., description="Unique filename with timestamp")
    mime_type: str = Field(..., description="Detected MIME type")
    file_type: FileTypeEnum = Field(..., description="File category")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    size_mb: float = Field(..., ge=0, description="File size in megabytes")
    upload_timestamp: str = Field(..., description="ISO format timestamp")
    
    # Optional fields based on file type
    dimensions: Optional[ImageDimensions] = None
    page_count: Optional[int] = Field(None, ge=1)
    metadata: Optional[PDFMetadata] = None
    temp_path: Optional[str] = None
    thumbnail_created: Optional[bool] = None
    thumbnail_size: Optional[int] = None
    extracted_text: Optional[str] = None
    total_text_length: Optional[int] = None
    validated: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_filename": "document.pdf",
                "safe_filename": "document.pdf",
                "unique_filename": "document_20241005_143022_a1b2c3d4.pdf",
                "mime_type": "application/pdf",
                "file_type": "pdf",
                "size_bytes": 1048576,
                "size_mb": 1.0,
                "upload_timestamp": "2024-10-05T14:30:22.123456",
                "page_count": 10
            }
        }


class FileUploadResponse(BaseModel):
    """Response for single file upload"""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Status message")
    file_info: Optional[FileInfoSchema] = Field(None, description="File information")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "File uploaded successfully",
                "file_info": {
                    "original_filename": "image.jpg",
                    "unique_filename": "image_20241005_143022_a1b2c3d4.jpg",
                    "mime_type": "image/jpeg",
                    "file_type": "image",
                    "size_mb": 2.5
                }
            }
        }


class ExcelPreviewResponse(BaseModel):
    """Excel file preview response"""
    sheet_name: Optional[str] = None
    columns: List[str]
    row_count: int = Field(..., ge=0)
    data: List[Dict[str, Any]]


class ImageProcessingRequest(BaseModel):
    """Request for image processing operations"""
    max_width: int = Field(1920, ge=100, le=4096, description="Maximum width")
    max_height: int = Field(1080, ge=100, le=4096, description="Maximum height")
    quality: int = Field(85, ge=1, le=100, description="JPEG quality (1-100)")
    create_thumbnail: bool = Field(False, description="Also create thumbnail")


class ThumbnailRequest(BaseModel):
    """Request for thumbnail creation"""
    width: int = Field(200, ge=50, le=500, description="Thumbnail width")
    height: int = Field(200, ge=50, le=500, description="Thumbnail height")


class FileValidationRequest(BaseModel):
    """Request to validate file without saving"""
    validate_only: bool = Field(True, description="Only validate, don't save")
    check_content: bool = Field(True, description="Validate file content")


class BulkFileUploadRequest(BaseModel):
    """Request for bulk file upload"""
    max_files: int = Field(10, ge=1, le=50, description="Maximum files to accept")
    allowed_types: Optional[List[str]] = Field(None, description="Allowed MIME types")
    fail_on_error: bool = Field(False, description="Fail entire batch if one fails")


class FileProcessingStatus(str, Enum):
    """File processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileProcessingJob(BaseModel):
    """File processing job status"""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str
    status: FileProcessingStatus
    progress: int = Field(0, ge=0, le=100, description="Processing progress percentage")
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
    result: Optional[FileInfoSchema] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "File too large",
                "detail": "File size (15.2MB) exceeds maximum allowed size (10.0MB)",
                "code": "FILE_TOO_LARGE"
            }
        }


# Health check schemas
class FileServiceHealth(BaseModel):
    """File service health status"""
    service: str = "file-upload"
    status: str = Field(..., description="Service status: healthy, degraded, unhealthy")
    temp_directory_writable: bool
    temp_directory_space_mb: Optional[float] = None
    active_uploads: int = Field(0, ge=0)
    timestamp: datetime


# Statistics schemas
class FileUploadStats(BaseModel):
    """File upload statistics"""
    total_uploads: int = Field(0, ge=0)
    successful_uploads: int = Field(0, ge=0)
    failed_uploads: int = Field(0, ge=0)
    total_size_mb: float = Field(0, ge=0)
    average_size_mb: float = Field(0, ge=0)
    file_types: Dict[str, int] = Field(default_factory=dict)
    period_start: datetime
    period_end: datetime