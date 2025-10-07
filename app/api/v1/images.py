from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from app.config.FileConfig import FileConfig
from app.handlers.file_upload_handler import FileUploadHandler
from app.handlers.processors.image_processor import ImageProcessor
from app.core.logging import get_logger

router = APIRouter()
file_handler = FileUploadHandler()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    resize: bool = False,
    max_width: int = 1920,
    max_height: int = 1080,
    handler: FileUploadHandler = Depends(lambda: file_handler),
):
    request_id = getattr(request.state, "request_id", None)

    try:
        # Log file upload start
        logger.info(
            "Image upload started",
            extra={
                "request_id": request_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "resize": resize,
            },
        )

        # Validate & process
        file_info = await handler.validate_and_process(
            file, allowed_types=FileConfig.ALLOWED_IMAGE_TYPES
        )

        processed_files = {}

        # Optional: Resize
        if resize:
            resized_data = await ImageProcessor.resize_image(
                file, max_width, max_height
            )
            processed_files["resized"] = len(resized_data)
            logger.info(
                "Image resized",
                extra={
                    "request_id": request_id,
                    "filename": file.filename,
                    "width": max_width,
                    "height": max_height,
                },
            )

        file_info["processed_files"] = processed_files

        # Log success
        logger.info(
            "Image upload and processing complete",
            extra={
                "request_id": request_id,
                "filename": file.filename,
                "processed_files": list(processed_files.keys()),
            },
        )

        return {
            "success": True,
            "message": "Image uploaded and processed successfully",
            "file_info": file_info,
        }

    except HTTPException as e:
        logger.error(
            "HTTPException during image upload",
            extra={
                "request_id": request_id,
                "filename": file.filename,
                "detail": str(e.detail),
                "status_code": e.status_code,
            },
        )
        raise
    except Exception as e:
        logger.exception(
            "Unexpected error during image upload",
            extra={
                "request_id": request_id,
                "filename": getattr(file, "filename", None),
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail="Internal server error")
