import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from PIL import Image
import re

# Configuration
UPLOAD_DIR = "uploads/blog_images"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
IMAGE_QUALITY = 85  # For compression
MAX_WIDTH = 1920
MAX_HEIGHT = 1080


def ensure_upload_dir():
    """Create upload directory if it doesn't exist"""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def validate_image_file(filename: str, content: bytes) -> tuple[bool, str]:
    """Validate image file type and size"""
    
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Try to open as image
    try:
        from io import BytesIO
        img = Image.open(BytesIO(content))
        img.verify()  # Verify it's a valid image
        return True, "Valid image"
    except Exception:
        return False, "Invalid image file"


def sanitize_filename(filename: str, blog_id: int) -> str:
    """Generate safe filename with timestamp and blog ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(filename)[1].lower()
    
    # Create safe name
    safe_name = f"blog_{blog_id}_{timestamp}{ext}"
    return safe_name


def process_and_save_image(content: bytes, filename: str, blog_id: int) -> Optional[str]:
    """Process, compress, and save image"""
    try:
        from io import BytesIO
        
        # Ensure upload directory exists
        ensure_upload_dir()
        
        # Open image
        img = Image.open(BytesIO(content))
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Resize if too large
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        
        # Generate safe filename
        safe_filename = sanitize_filename(filename, blog_id)
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save with compression
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            img.save(file_path, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
        elif filename.lower().endswith('.png'):
            img.save(file_path, 'PNG', optimize=True)
        elif filename.lower().endswith('.webp'):
            img.save(file_path, 'WEBP', quality=IMAGE_QUALITY)
        else:
            img.save(file_path)
        
        return file_path
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def delete_image(image_path: Optional[str]):
    """Delete image file from filesystem"""
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
            print(f"Deleted image: {image_path}")
        except Exception as e:
            print(f"Error deleting image: {e}")


def get_image_url(image_path: Optional[str]) -> Optional[str]:
    """Convert file path to URL"""
    if image_path:
        # Convert to URL format
        return f"/{image_path.replace(os.sep, '/')}"
    return None