from pathlib import Path


class FileConfig:
    """File upload configuration"""

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_DOCUMENT_SIZE = 25 * 1024 * 1024  # 25MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB

    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/bmp",
    }

    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    ALLOWED_SPREADSHEET_TYPES = {
        # "text/excel",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel.sheet.macroEnabled.12",
    }

    ALLOWED_VIDEO_TYPES = {
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
    }

    ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"}

    ALLOWED_ARCHIVE_TYPES = {
        "application/zip",
        "application/x-zip-compressed",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
    }

    BLOCKED_EXTENSIONS = {
        ".exe",
        ".bat",
        ".cmd",
        ".sh",
        ".ps1",
        ".msi",
        ".dll",
        ".scr",
        ".vbs",
        ".js",
        ".jar",
        ".app",
        ".deb",
        ".rpm",
    }

    TEMP_UPLOAD_DIR = Path("./temp_uploads")
    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_all_allowed_types(cls) -> set:
        return (
            cls.ALLOWED_IMAGE_TYPES
            | cls.ALLOWED_DOCUMENT_TYPES
            | cls.ALLOWED_SPREADSHEET_TYPES
            | cls.ALLOWED_VIDEO_TYPES
            | cls.ALLOWED_AUDIO_TYPES
            | cls.ALLOWED_ARCHIVE_TYPES
        )
