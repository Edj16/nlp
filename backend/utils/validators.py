from pathlib import Path
from config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS

def validate_file_upload(file) -> tuple[bool, str]:
    if not file:
        return False, "No file provided"
    if file.filename == '':
        return False, "No file selected"
    
    ext = Path(file.filename).suffix[1:].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return False, f"File too large. Max: {MAX_FILE_SIZE / 1024 / 1024}MB"
    
    return True, "Valid"
