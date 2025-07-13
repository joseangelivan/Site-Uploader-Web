import os

STATIC_BASE = os.path.join(os.getcwd(), 'static')

class Config:
    UPLOAD_FOLDER = STATIC_BASE
    TOKEN = "cm6f0vxyt004cpl0175mingss"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 500  # 500 MB máximo
    DEFAULT_HASH_ALGORITHM = "sha256"
    ALLOWED_HASH_ALGORITHMS = ["sha256", "sha1", "md5"]
