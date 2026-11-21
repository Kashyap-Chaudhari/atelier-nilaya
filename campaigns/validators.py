import os
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_video_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp4', '.webm', '.mov']
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported video format. Allowed formats: {", ".join(valid_extensions)}')
    
    max_size = getattr(settings, 'MAX_VIDEO_UPLOAD_SIZE', 35 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(f'Video file size exceeds limit of {max_size / (1024 * 1024):.0f}MB.')

def validate_image_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported image format. Allowed formats: {", ".join(valid_extensions)}')
    
    max_size = getattr(settings, 'MAX_IMAGE_UPLOAD_SIZE', 10 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(f'Image file size exceeds limit of {max_size / (1024 * 1024):.0f}MB.')
