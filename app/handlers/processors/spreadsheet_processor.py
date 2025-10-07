import io
from typing import Optional
import pandas as pd
from fastapi import UploadFile, HTTPException, status


class SpreadsheetProcessor:
    @staticmethod
    async def read_csv(
        file: UploadFile, max_rows: Optional[int] = None
    ) -> pd.DataFrame:
        try:
            content = await file.read()
            await file.seek(0)
            return pd.read_csv(io.BytesIO(content), nrows=max_rows)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid CSV: {str(e)}"
            )

    @staticmethod
    async def read_excel(
        file: UploadFile,
        sheet_name: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> pd.DataFrame:
        try:
            content = await file.read()
            await file.seek(0)
            return pd.read_excel(
                io.BytesIO(content), sheet_name=sheet_name or 0, nrows=max_rows
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel: {str(e)}",
            )
