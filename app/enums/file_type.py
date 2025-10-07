from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    # CSV = "csv"
    EXCEL = "excel"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"
