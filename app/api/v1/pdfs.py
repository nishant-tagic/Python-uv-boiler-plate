from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.handlers.file_upload_handler import FileUploadHandler
from app.handlers.processors.pdf_processor import PDFProcessor

router = APIRouter()
file_handler = FileUploadHandler()

@router.post("/uploadpdf")
async def upload_pdf(file: UploadFile = File(...), extract_text: bool = False, handler: FileUploadHandler = Depends(lambda: file_handler)):
    try:
        file_info = await handler.validate_and_process(file, allowed_types={"application/pdf"})
        metadata = await PDFProcessor.get_metadata(file)
        file_info["metadata"] = metadata
        if extract_text:
            text = await PDFProcessor.extract_text(file)
            file_info["text_preview"] = text[:500]
            file_info["total_text_length"] = len(text)
        return {"success": True, "message": "PDF uploaded successfully", "file_info": file_info}
    except HTTPException:
        raise
