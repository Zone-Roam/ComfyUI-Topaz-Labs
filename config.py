"""
Configuration file for Topaz Labs ComfyUI Integration
"""

import os

# API Configuration
TOPAZ_API_BASE_URL = "https://api.topazlabs.com/image/v1"
TOPAZ_VIDEO_API_BASE_URL = "https://api.topazlabs.com/video"

# Default timeout settings (in seconds)
DEFAULT_TIMEOUT = 300  # 5 minutes for API requests
DEFAULT_ASYNC_TIMEOUT = 600  # 10 minutes for async job completion

# Default polling interval for async jobs (in seconds)
ASYNC_POLL_INTERVAL = 5

# Maximum file size for uploads (in bytes)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB as per API documentation

# Supported image formats
SUPPORTED_INPUT_FORMATS = ['jpeg', 'jpg', 'png', 'tiff', 'tif']
SUPPORTED_OUTPUT_FORMATS = ['jpeg', 'jpg', 'png', 'tiff', 'tif']

# Model configurations
ENHANCE_MODELS = {
    "Standard V2": {
        "description": "General-purpose model balancing detail, sharpness, and noise reduction",
        "parameters": ["sharpen", "denoise", "fix_compression"]
    },
    "Low Resolution V2": {
        "description": "Enhances clarity and detail in low-resolution images",
        "parameters": ["sharpen", "denoise", "fix_compression"]
    },
    "CGI": {
        "description": "Optimized for CGI and digital illustrations",
        "parameters": ["sharpen", "denoise"]
    },
    "High Fidelity V2": {
        "description": "Ideal for high-quality images, preserving intricate details",
        "parameters": ["sharpen", "denoise", "fix_compression"]
    },
    "Text Refine": {
        "description": "Designed for images with text and shapes",
        "parameters": ["strength", "sharpen", "denoise", "fix_compression"]
    }
}

SHARPEN_MODELS = {
    "Standard": {
        "description": "All-purpose sharpening for slight lens and motion blur",
        "parameters": ["strength", "minor_denoise"]
    },
    "Strong": {
        "description": "For very blurry and out-of-focus images",
        "parameters": ["strength"]
    },
    "Lens Blur": {
        "description": "Ideal for images affected by lens focus issues",
        "parameters": ["strength", "minor_denoise"]
    },
    "Lens Blur V2": {
        "description": "Generation 2 lens blur correction with stronger results",
        "parameters": ["strength", "minor_denoise"]
    },
    "Motion Blur": {
        "description": "Optimized for movement-caused blur",
        "parameters": ["strength", "minor_denoise"]
    },
    "Natural": {
        "description": "Sharpen objects while keeping textures natural",
        "parameters": ["strength", "minor_denoise"]
    },
    "Refocus": {
        "description": "Emphasize details and bring out finer textures",
        "parameters": ["strength", "minor_denoise"]
    }
}

DENOISE_MODELS = {
    "Normal": {
        "description": "Remove low-medium noise from smartphones and cameras",
        "parameters": ["strength", "minor_deblur", "original_detail"]
    },
    "Strong": {
        "description": "Emphasize detail retention for medium-high noise images",
        "parameters": ["strength", "minor_deblur", "original_detail"]
    },
    "Extreme": {
        "description": "Prioritize noise removal over detail preservation",
        "parameters": ["strength", "minor_deblur", "original_detail"]
    }
}

# Environment variable names for API key
API_KEY_ENV_VARS = [
    'TOPAZ_API_KEY',
    'TOPAZ_LABS_API_KEY',
    'TOPAZLABS_API_KEY'
]

def get_api_key_from_env():
    """Try to get API key from environment variables"""
    for var_name in API_KEY_ENV_VARS:
        api_key = os.getenv(var_name)
        if api_key:
            return api_key
    return None

# Default parameter values
DEFAULT_ENHANCE_PARAMS = {
    "face_enhancement": True,
    "face_enhancement_creativity": 0.0,
    "face_enhancement_strength": 0.8,
    "crop_to_fill": False,
    "sharpen": 0.5,
    "denoise": 0.5,
    "fix_compression": 0.5,
    "output_format": "png"
}

DEFAULT_SHARPEN_PARAMS = {
    "strength": 0.5,
    "minor_denoise": 0.3,
    "output_format": "png"
}

DEFAULT_DENOISE_PARAMS = {
    "strength": 0.5,
    "minor_deblur": 0.3,
    "original_detail": 0.5,
    "output_format": "png"
}

# Video API Configuration
VIDEO_ENHANCEMENT_MODELS = {
    "prob-4": {
        "name": "Proteus General",
        "description": "Best for most videos - general upscaling and enhancement",
        "category": "enhancement",
        "type": "upscaling"
    },
    "ahq-12": {
        "name": "Artemis High Quality",
        "description": "Best for both denoise and sharpen - high quality",
        "category": "enhancement",
        "type": "denoise_sharpen"
    },
    "amq-13": {
        "name": "Artemis Medium Quality",
        "description": "Denoise and sharpen - medium quality",
        "category": "enhancement",
        "type": "denoise_sharpen"
    },
    "alq-13": {
        "name": "Artemis Low Quality",
        "description": "Denoise and sharpen - low quality",
        "category": "enhancement",
        "type": "denoise_sharpen"
    },
    "nyx-3": {
        "name": "Nyx General",
        "description": "Dedicated for denoise - general",
        "category": "enhancement",
        "type": "denoise"
    },
    "nxf-1": {
        "name": "Nyx Fast",
        "description": "Dedicated for denoise - fast",
        "category": "enhancement",
        "type": "denoise"
    },
    "rhea-1": {
        "name": "Rhea General",
        "description": "Advanced 4x upscaling",
        "category": "enhancement",
        "type": "upscaling"
    },
    "ghq-5": {
        "name": "Gaia High Quality",
        "description": "Best for GenAI/CG/Animation - high quality",
        "category": "enhancement",
        "type": "cg_animation"
    },
    "gcg-5": {
        "name": "Gaia Computer Generated",
        "description": "Best for computer generated content",
        "category": "enhancement",
        "type": "cg_animation"
    },
    "apo-8": {
        "name": "Apollo General",
        "description": "Best overall frame interpolation - up to 8x slowmo",
        "category": "interpolation",
        "type": "slowmo"
    },
    "apf-2": {
        "name": "Apollo Fast",
        "description": "Fast frame interpolation",
        "category": "interpolation",
        "type": "slowmo"
    },
    "chr-2": {
        "name": "Chronos General",
        "description": "General framerate conversions",
        "category": "interpolation",
        "type": "framerate"
    },
    "chf-3": {
        "name": "Chronos Fast",
        "description": "Fast framerate conversions",
        "category": "interpolation",
        "type": "framerate"
    }
}

# Advanced video models
ADVANCED_VIDEO_MODELS = {
    "ddv-3": {
        "name": "Dione DV Footage",
        "description": "Best for older DV footage",
        "category": "advanced",
        "type": "restoration"
    },
    "dtd-4": {
        "name": "Dione Robust",
        "description": "Robust enhancement for older content",
        "category": "advanced",
        "type": "restoration"
    },
    "dtds-2": {
        "name": "Dione Robust Dehalo",
        "description": "Robust enhancement with dehalo",
        "category": "advanced",
        "type": "restoration"
    },
    "dtv-4": {
        "name": "Dione TV",
        "description": "Best for TV content",
        "category": "advanced",
        "type": "restoration"
    },
    "dtvs-2": {
        "name": "Dione Halo",
        "description": "TV content with halo removal",
        "category": "advanced",
        "type": "restoration"
    },
    "thd-3": {
        "name": "Theia Detail",
        "description": "High fidelity and details",
        "category": "advanced",
        "type": "detail"
    },
    "thf-4": {
        "name": "Theia Fidelity",
        "description": "High fidelity enhancement",
        "category": "advanced",
        "type": "detail"
    },
    "iris-3": {
        "name": "Iris General",
        "description": "Specialized enhancement for faces",
        "category": "advanced",
        "type": "faces"
    },
    "thm-2": {
        "name": "Themis General",
        "description": "Motion deblur",
        "category": "advanced",
        "type": "deblur"
    }
}

# Video output settings
VIDEO_CONTAINERS = ["mp4", "mov", "avi"]
VIDEO_CODECS = ["H264", "H265", "ProRes"]
VIDEO_PROFILES = ["High", "Main", "Baseline"]  # High is required by Topaz API
AUDIO_CODECS = ["AAC", "MP3", "PCM"]
AUDIO_TRANSFER_OPTIONS = ["Copy", "Transcode"]
COMPRESSION_LEVELS = ["Low", "Medium", "High"]

# Default video parameters
DEFAULT_VIDEO_PARAMS = {
    "container": "mp4",
    "video_encoder": "H264",
    "video_profile": "Main",
    "audio_codec": "AAC",
    "audio_transfer": "Copy",
    "compression_level": "High"
}
