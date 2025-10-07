from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.FileConfig import FileConfig
from app.handlers.file_upload_handler import FileUploadHandler
from app.handlers.processors.spreadsheet_processor import SpreadsheetProcessor

import numpy as np

router = APIRouter()
file_handler = FileUploadHandler()

@router.post("/excel/upload")
async def upload_excel(file: UploadFile = File(...), sheet_name: str = None, preview_rows: int = 5):
    try:
        file_info = await file_handler.validate_and_process(
            file, allowed_types=FileConfig.ALLOWED_SPREADSHEET_TYPES
        )

        df = await SpreadsheetProcessor.read_excel(file, sheet_name=sheet_name, max_rows=preview_rows)

        # ✅ Replace NaN and infinite values before returning
        df = df.replace([np.inf, -np.inf], np.nan).fillna("")

        file_info["preview"] = {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "data": df.to_dict(orient="records")
        }

        return {"success": True, "message": "Excel file uploaded", "file_info": file_info}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
