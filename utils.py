"""
Utility functions for Topaz Labs ComfyUI Integration
"""

import torch
import numpy as np
from PIL import Image
import io
import os
from typing import Optional, Tuple, Union
try:
    from .config import get_api_key_from_env, MAX_FILE_SIZE
except ImportError:
    # Fallback for standalone testing
    from config import get_api_key_from_env, MAX_FILE_SIZE

def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    Convert ComfyUI tensor to PIL Image
    
    Args:
        tensor: ComfyUI image tensor in format [batch, height, width, channels] with values 0-1
        
    Returns:
        PIL Image object
    """
    # Remove batch dimension if present
    if len(tensor.shape) == 4:
        tensor = tensor.squeeze(0)
    
    # Ensure we have 3 channels (RGB)
    if tensor.shape[-1] == 1:
        # Grayscale to RGB
        tensor = tensor.repeat(1, 1, 3)
    elif tensor.shape[-1] == 4:
        # RGBA to RGB (remove alpha channel)
        tensor = tensor[:, :, :3]
    
    # Convert from 0-1 to 0-255 and to uint8
    array = (tensor.cpu().numpy() * 255).astype(np.uint8)
    
    return Image.fromarray(array)

def pil_to_tensor(pil_image: Image.Image) -> torch.Tensor:
    """
    Convert PIL Image to ComfyUI tensor
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        ComfyUI tensor in format [1, height, width, channels] with values 0-1
    """
    # Ensure RGB mode
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to numpy array and normalize to 0-1
    array = np.array(pil_image).astype(np.float32) / 255.0
    
    # Add batch dimension: [1, height, width, channels]
    tensor = torch.from_numpy(array).unsqueeze(0)
    
    return tensor

def validate_image_size(image_data: bytes) -> bool:
    """
    Validate that image data is within size limits
    
    Args:
        image_data: Raw image data in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return len(image_data) <= MAX_FILE_SIZE

def get_image_info(pil_image: Image.Image) -> dict:
    """
    Get information about a PIL image
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        Dictionary with image information
    """
    return {
        'width': pil_image.width,
        'height': pil_image.height,
        'mode': pil_image.mode,
        'format': pil_image.format,
        'size_bytes': len(pil_image.tobytes()) if hasattr(pil_image, 'tobytes') else 0,
        'megapixels': (pil_image.width * pil_image.height) / 1_000_000
    }

def calculate_output_dimensions(
    input_width: int, 
    input_height: int, 
    output_width: Optional[int] = None, 
    output_height: Optional[int] = None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Calculate output dimensions maintaining aspect ratio
    
    Args:
        input_width: Original image width
        input_height: Original image height
        output_width: Desired output width (None for auto)
        output_height: Desired output height (None for auto)
        
    Returns:
        Tuple of (calculated_width, calculated_height)
    """
    if output_width and output_height:
        # Both dimensions specified
        return output_width, output_height
    elif output_width and not output_height:
        # Only width specified, calculate height
        aspect_ratio = input_height / input_width
        calculated_height = int(output_width * aspect_ratio)
        return output_width, calculated_height
    elif output_height and not output_width:
        # Only height specified, calculate width
        aspect_ratio = input_width / input_height
        calculated_width = int(output_height * aspect_ratio)
        return calculated_width, output_height
    else:
        # Neither specified, return None for both (API will auto-scale)
        return None, None

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def validate_api_key(api_key: str) -> bool:
    """
    Basic validation of API key format
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if format appears valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Remove whitespace
    api_key = api_key.strip()
    
    # Basic length check (Topaz API keys are typically longer)
    if len(api_key) < 10:
        return False
    
    # Check for obvious placeholder text
    placeholder_texts = [
        'your_api_key',
        'api_key_here',
        'enter_key',
        'topaz_key',
        'key',
        'xxx'
    ]
    
    if api_key.lower() in placeholder_texts:
        return False
    
    return True

def get_api_key(provided_key: str) -> str:
    """
    Get API key from provided value or environment variables
    
    Args:
        provided_key: API key provided by user
        
    Returns:
        Valid API key
        
    Raises:
        ValueError: If no valid API key is found
    """
    # First try the provided key
    if provided_key and validate_api_key(provided_key):
        return provided_key.strip()
    
    # Try environment variables
    env_key = get_api_key_from_env()
    if env_key and validate_api_key(env_key):
        return env_key.strip()
    
    raise ValueError(
        "No valid API key found. Please provide your Topaz Labs API key "
        "either in the node parameter or set it as an environment variable "
        "(TOPAZ_API_KEY, TOPAZ_LABS_API_KEY, or TOPAZLABS_API_KEY)."
    )

def prepare_image_for_api(pil_image: Image.Image, format: str = 'PNG') -> bytes:
    """
    Prepare PIL image for API upload
    
    Args:
        pil_image: PIL Image object
        format: Output format ('PNG', 'JPEG', etc.)
        
    Returns:
        Image data as bytes
    """
    # Ensure RGB mode for JPEG, keep as-is for PNG
    if format.upper() == 'JPEG' and pil_image.mode in ('RGBA', 'LA', 'P'):
        # Convert to RGB for JPEG (no transparency support)
        pil_image = pil_image.convert('RGB')
    elif format.upper() == 'PNG' and pil_image.mode not in ('RGB', 'RGBA', 'L', 'LA'):
        # Convert to RGB for PNG if needed
        pil_image = pil_image.convert('RGB')
    
    # Save to bytes buffer
    img_buffer = io.BytesIO()
    save_kwargs = {}
    
    if format.upper() == 'JPEG':
        save_kwargs['quality'] = 95
        save_kwargs['optimize'] = True
    
    pil_image.save(img_buffer, format=format.upper(), **save_kwargs)
    return img_buffer.getvalue()

def log_processing_info(operation: str, model: str, input_info: dict, params: dict):
    """
    Log processing information for debugging

    Args:
        operation: Type of operation (enhance, sharpen, denoise)
        model: Model being used
        input_info: Input image information
        params: Processing parameters
    """
    print(f"\n=== Topaz Labs {operation.title()} ===")
    print(f"Model: {model}")
    print(f"Input: {input_info['width']}x{input_info['height']} ({input_info['megapixels']:.1f}MP)")
    print(f"Format: {input_info['mode']}")
    print(f"Parameters: {params}")
    print("=" * 40)

def get_video_info(video_path: str) -> dict:
    """
    Get information about a video file using basic file operations

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with video information
    """
    import os

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size = os.path.getsize(video_path)
    file_ext = os.path.splitext(video_path)[1].lower().lstrip('.')

    # Basic info that can be determined without video libraries
    info = {
        'path': video_path,
        'size_bytes': file_size,
        'size_mb': file_size / (1024 * 1024),
        'container': file_ext,
        'filename': os.path.basename(video_path)
    }

    return info

def validate_video_file(video_path: str) -> bool:
    """
    Validate that video file exists and has supported format

    Args:
        video_path: Path to video file

    Returns:
        True if valid, False otherwise
    """
    try:
        from .config import VIDEO_CONTAINERS
    except ImportError:
        from config import VIDEO_CONTAINERS

    import os

    if not os.path.exists(video_path):
        return False

    file_ext = os.path.splitext(video_path)[1].lower().lstrip('.')
    return file_ext in [c.lower() for c in VIDEO_CONTAINERS]

def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m 45s")
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs}s"

def estimate_video_processing_time(duration_seconds: int, model_type: str) -> tuple:
    """
    Estimate video processing time based on duration and model

    Args:
        duration_seconds: Video duration in seconds
        model_type: Type of model being used

    Returns:
        Tuple of (min_time, max_time) in seconds
    """
    # Base processing ratios (processing_time / video_duration)
    base_ratios = {
        'upscaling': (2, 4),      # 2x-4x video duration
        'denoise': (1, 2),        # 1x-2x video duration
        'interpolation': (3, 6),  # 3x-6x video duration (more complex)
        'restoration': (2, 5),    # 2x-5x video duration
        'detail': (1.5, 3),       # 1.5x-3x video duration
        'faces': (2, 4),          # 2x-4x video duration
        'deblur': (2, 3),         # 2x-3x video duration
        'default': (1, 3)         # Default range
    }

    ratio_min, ratio_max = base_ratios.get(model_type, base_ratios['default'])

    min_time = int(duration_seconds * ratio_min)
    max_time = int(duration_seconds * ratio_max)

    return (min_time, max_time)

def log_video_processing_info(operation: str, model: str, video_info: dict, params: dict):
    """
    Log video processing information for debugging

    Args:
        operation: Type of operation (enhance, interpolate, etc.)
        model: Model being used
        video_info: Video file information
        params: Processing parameters
    """
    print(f"\n=== Topaz Labs Video {operation.title()} ===")
    print(f"Model: {model}")
    print(f"File: {video_info.get('filename', 'Unknown')}")
    print(f"Size: {video_info.get('size_mb', 0):.1f} MB")
    print(f"Container: {video_info.get('container', 'Unknown')}")
    if 'duration' in video_info:
        print(f"Duration: {format_duration(video_info['duration'])}")
    if 'resolution' in video_info:
        res = video_info['resolution']
        print(f"Resolution: {res.get('width', '?')}x{res.get('height', '?')}")
    print(f"Parameters: {params}")
    print("=" * 50)
