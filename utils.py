import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename

def generate_unique_filename(filename):
    """Generate a unique filename to avoid conflicts"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_filename = str(uuid.uuid4())
    return f"{unique_filename}.{ext}" if ext else unique_filename

def resize_image(image_path, max_width=1200, max_height=800, quality=85):
    """Resize image while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions
            width, height = img.size
            if width > max_width or height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

def create_thumbnail(image_path, thumb_path, size=(300, 300)):
    """Create a thumbnail from an image"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumb_path, 'JPEG', quality=80, optimize=True)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_currency(amount):
    """Format currency for display"""
    if amount is None:
        return "Price on request"
    return f"${amount:,.2f}"

def truncate_text(text, length=150):
    """Truncate text to specified length"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'
