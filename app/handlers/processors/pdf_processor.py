import io
from fastapi import UploadFile, HTTPException, status
from pypdf import PdfReader


class PDFProcessor:
    @staticmethod
    async def validate_pdf(file: UploadFile) -> int:
        try:
            content = await file.read()
            await file.seek(0)
            pdf = PdfReader(io.BytesIO(content))
            return len(pdf.pages)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid PDF: {str(e)}"
            )

    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        content = await file.read()
        await file.seek(0)
        pdf = PdfReader(io.BytesIO(content))
        return "".join(page.extract_text() or "" for page in pdf.pages)

    @staticmethod
    async def get_metadata(file: UploadFile) -> dict:
        content = await file.read()
        await file.seek(0)
        pdf = PdfReader(io.BytesIO(content))
        md = pdf.metadata
        return {
            "title": md.get("/Title", ""),
            "author": md.get("/Author", ""),
            "subject": md.get("/Subject", ""),
            "creator": md.get("/Creator", ""),
            "producer": md.get("/Producer", ""),
            "creation_date": md.get("/CreationDate", ""),
            "pages": len(pdf.pages),
        }
