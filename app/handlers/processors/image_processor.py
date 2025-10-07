import io
from typing import Tuple
from PIL import Image
from fastapi import UploadFile, HTTPException, status


class ImageProcessor:
    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[int, int]:
        try:
            content = await file.read()
            await file.seek(0)
            img = Image.open(io.BytesIO(content))
            img.verify()
            img = Image.open(io.BytesIO(content))
            return img.size
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {str(e)}",
            )

    @staticmethod
    async def resize_image(
        file: UploadFile,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
    ) -> bytes:
        content = await file.read()
        await file.seek(0)
        img = Image.open(io.BytesIO(content))
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()
