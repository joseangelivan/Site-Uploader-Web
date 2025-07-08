import os

# Define la carpeta base STATIC (dentro del proyecto)
STATIC_BASE = os.path.join(os.getcwd(), 'static')

class Config:
    UPLOAD_FOLDER = STATIC_BASE
    TOKEN = "cm6f0vxyt004cpl0175mingss"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 500  # 500 MB máximo