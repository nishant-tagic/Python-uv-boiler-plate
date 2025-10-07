from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.handlers.file_upload_handler import FileUploadHandler
from app.schemas.file_schemas import FileUploadResponse
from app.core.logging import get_logger
from datetime import datetime, timezone

router = APIRouter()
file_handler = FileUploadHandler()
logger = get_logger(__name__)

def get_file_handler() -> FileUploadHandler:
    return file_handler


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    handler: FileUploadHandler = Depends(get_file_handler),
):

    try:
        logger.info("File upload started")

        file_info = await handler.validate_and_process(file)
        file_path = await handler.save_temp_file(file, file_info["unique_filename"])
        file_info["temp_path"] = str(file_path)
        file_info["upload_timestamp"] = datetime.now(timezone.utc).isoformat()

        logger.info("File upload completed")

        return FileUploadResponse(
            success=True,
            message="File uploaded",
            file_info=file_info,
        )

    except HTTPException as e:
        logger.warning(
            "File upload failed",
            error=str(e.detail),
        )
        raise

    except Exception as e:
        logger.error(
            "Unexpected error in file upload",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")