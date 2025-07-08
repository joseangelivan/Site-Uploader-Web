import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static')
    TOKEN = "cm6f0vxyt004cpl0175mingss"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 500  # 500 MB máximo
