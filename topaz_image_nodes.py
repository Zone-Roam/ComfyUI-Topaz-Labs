"""
Topaz Labs ComfyUI Nodes - Clean Version (Sync Only)
"""

import io
import time
import requests
import torch
import numpy as np
from PIL import Image
from typing import Dict, Any, Tuple

# Try relative imports first, then absolute
try:
    from .utils import (
        get_api_key, validate_image_size, prepare_image_for_api,
        log_processing_info, calculate_output_dimensions
    )
    from .config import (
        TOPAZ_API_BASE_URL, DEFAULT_TIMEOUT
    )
except ImportError:
    # Fallback for direct execution
    from utils import (
        get_api_key, validate_image_size, prepare_image_for_api,
        log_processing_info, calculate_output_dimensions
    )
    from config import (
        TOPAZ_API_BASE_URL, DEFAULT_TIMEOUT
    )


class TopazEnhanceNode:
    """
    ComfyUI Node for Topaz Labs Enhance API (Sync Only)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (["Standard V2", "Low Resolution V2", "CGI", "High Fidelity V2", "Text Refine"], {
                    "default": "Standard V2"
                }),
                "output_format": (["jpeg", "png", "tiff"], {
                    "default": "png"
                }),
            },
            "optional": {
                "output_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "0 means auto-scale based on width or original ratio"
                }),
                "output_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "0 means auto-scale based on height or original ratio"
                }),
                "face_enhancement": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enhanced",
                    "label_off": "Standard"
                }),
                "face_enhancement_creativity": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "face_enhancement_strength": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "crop_to_fill": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Crop",
                    "label_off": "Fit"
                }),
                "sharpen": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "denoise": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "fix_compression": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("enhanced_image",)
    FUNCTION = "enhance_image"
    CATEGORY = "Topaz Labs"
    DESCRIPTION = "Enhance images using Topaz Labs AI models (Sync mode only)"

    def call_topaz_api(self, image_data: bytes, params: Dict[str, Any], api_key: str) -> bytes:
        """Call Topaz Labs API (Sync mode only)"""
        endpoint = "/enhance"

        headers = {
            "X-API-Key": api_key,
            "Accept": "*/*"
        }

        # Prepare form data
        files = {
            'image': ('image.png', image_data, 'image/png')
        }

        # Add parameters to form data
        data = {}
        for key, value in params.items():
            if value is not None and value != "":
                data[key] = str(value) if not isinstance(value, bool) else str(value).lower()

        print(f"Calling Topaz API: {TOPAZ_API_BASE_URL}{endpoint}")
        print(f"Parameters: {data}")

        try:
            response = requests.post(
                f"{TOPAZ_API_BASE_URL}{endpoint}",
                headers=headers,
                files=files,
                data=data,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()

            # Return image data directly
            return response.content

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def validate_api_key(self, api_key: str) -> str:
        """Validate and return API key"""
        if not api_key or api_key.strip() == "":
            raise Exception("API key is required. Please provide your Topaz Labs API key.")
        return api_key.strip()

    def enhance_image(self, image, api_key, model, output_format,
                     output_height=0, output_width=0, face_enhancement=True,
                     face_enhancement_creativity=0.0, face_enhancement_strength=0.8,
                     crop_to_fill=False, sharpen=0.5, denoise=0.5, fix_compression=0.5):

        # Validate and get API key
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise Exception(str(e))

        # Input image is already validated by ComfyUI

        # Convert ComfyUI tensor to PIL Image
        pil_image = self.tensor_to_pil(image)

        # Get image info for logging
        input_info = {
            'width': pil_image.width,
            'height': pil_image.height,
            'mode': pil_image.mode,
            'megapixels': (pil_image.width * pil_image.height) / 1_000_000
        }

        # Calculate output dimensions
        output_width, output_height = calculate_output_dimensions(
            pil_image.width, pil_image.height, output_width, output_height
        )

        # Prepare image data
        image_data = prepare_image_for_api(pil_image)

        # Prepare API parameters
        params = {
            'model': model,
            'output_format': output_format,
            'face_enhancement': str(face_enhancement).lower(),
            'face_enhancement_creativity': str(face_enhancement_creativity),
            'face_enhancement_strength': str(face_enhancement_strength),
            'crop_to_fill': str(crop_to_fill).lower(),
            'output_width': str(output_width),
            'output_height': str(output_height),
            'sharpen': str(sharpen),
            'denoise': str(denoise),
            'fix_compression': str(fix_compression)
        }

        # Log processing info
        log_processing_info("enhance", model, input_info, params)

        try:
            # Call API (sync mode only)
            result_data = self.call_topaz_api(image_data, params, validated_api_key)

            # Convert result back to PIL Image
            print(f"Attempting to open image from {len(result_data)} bytes of data")
            result_image = Image.open(io.BytesIO(result_data))

            # Log output info
            output_info = {
                'width': result_image.width,
                'height': result_image.height,
                'mode': result_image.mode,
                'megapixels': (result_image.width * result_image.height) / 1_000_000
            }
            log_processing_info("enhance", model, output_info, {"status": "completed"})

            # Convert to ComfyUI tensor
            result_tensor = self.pil_to_tensor(result_image)

            return (result_tensor,)

        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            raise e

    def tensor_to_pil(self, tensor):
        """Convert ComfyUI tensor to PIL Image"""
        # ComfyUI tensors are in format [batch, height, width, channels]
        array = tensor.squeeze(0).cpu().numpy()  # Remove batch dimension

        # Ensure we have the right number of dimensions
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)
        elif array.ndim == 3 and array.shape[0] in [1, 3, 4]:  # CHW format
            array = np.transpose(array, (1, 2, 0))  # Convert to HWC

        # Convert to uint8
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)

        # Handle different channel counts
        if array.shape[2] == 1:  # Grayscale
            array = array.squeeze(2)
            return Image.fromarray(array, mode='L')
        elif array.shape[2] == 3:  # RGB
            return Image.fromarray(array, mode='RGB')
        elif array.shape[2] == 4:  # RGBA
            return Image.fromarray(array, mode='RGBA')
        else:
            raise ValueError(f"Unsupported number of channels: {array.shape[2]}")

    def pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI tensor"""
        # Convert PIL to numpy array
        array = np.array(pil_image).astype(np.float32) / 255.0

        # Ensure we have 3 dimensions (HWC)
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)

        # Convert to tensor and add batch dimension: [1, H, W, C]
        tensor = torch.from_numpy(array).unsqueeze(0)
        return tensor


class TopazSharpenNode:
    """
    ComfyUI Node for Topaz Labs Sharpen API (Sync Only)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (["Standard", "Strong", "Lens Blur"], {
                    "default": "Standard"
                }),
                "output_format": (["jpeg", "png", "tiff"], {
                    "default": "png"
                }),
            },
            "optional": {
                "output_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number"
                }),
                "output_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number"
                }),
                "strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("sharpened_image",)
    FUNCTION = "sharpen_image"
    CATEGORY = "Topaz Labs"
    DESCRIPTION = "Sharpen images using Topaz Labs AI models (Sync mode only)"

    def call_topaz_api(self, image_data: bytes, params: Dict[str, Any], api_key: str) -> bytes:
        """Call Topaz Labs Sharpen API (Sync mode only)"""
        base_url = "https://api.topazlabs.com/image/v1"
        endpoint = "/sharpen"

        headers = {
            "X-API-Key": api_key,
            "Accept": "*/*"
        }

        files = {
            'image': ('image.png', image_data, 'image/png')
        }

        data = {}
        for key, value in params.items():
            if value is not None and value != "":
                data[key] = str(value) if not isinstance(value, bool) else str(value).lower()

        print(f"Calling Topaz Sharpen API: {base_url}{endpoint}")
        print(f"Parameters: {data}")

        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                headers=headers,
                files=files,
                data=data,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            return response.content

        except requests.exceptions.RequestException as e:
            raise Exception(f"Sharpen API request failed: {str(e)}")

    def sharpen_image(self, image, api_key, model, output_format,
                     output_height=0, output_width=0, strength=0.5):

        # Validate and get API key
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise Exception(str(e))

        # Input image is already validated by ComfyUI

        # Convert ComfyUI tensor to PIL Image
        pil_image = self.tensor_to_pil(image)

        # Get image info for logging
        input_info = {
            'width': pil_image.width,
            'height': pil_image.height,
            'mode': pil_image.mode,
            'megapixels': (pil_image.width * pil_image.height) / 1_000_000
        }

        # Calculate output dimensions
        output_width, output_height = calculate_output_dimensions(
            pil_image.width, pil_image.height, output_width, output_height
        )

        # Prepare image data
        image_data = prepare_image_for_api(pil_image)

        # Prepare API parameters
        params = {
            'model': model,
            'output_format': output_format,
            'output_width': str(output_width),
            'output_height': str(output_height),
            'strength': str(strength)
        }

        # Log processing info
        log_processing_info("sharpen", model, input_info, params)

        try:
            # Call API (sync mode only)
            result_data = self.call_topaz_api(image_data, params, validated_api_key)

            # Convert result back to PIL Image
            result_image = Image.open(io.BytesIO(result_data))

            # Log output info
            output_info = {
                'width': result_image.width,
                'height': result_image.height,
                'mode': result_image.mode,
                'megapixels': (result_image.width * result_image.height) / 1_000_000
            }
            log_processing_info("sharpen", model, output_info, {"status": "completed"})

            # Convert to ComfyUI tensor
            result_tensor = self.pil_to_tensor(result_image)

            return (result_tensor,)

        except Exception as e:
            print(f"Error sharpening image: {str(e)}")
            raise e

    def tensor_to_pil(self, tensor):
        """Convert ComfyUI tensor to PIL Image"""
        # ComfyUI tensors are in format [batch, height, width, channels]
        array = tensor.squeeze(0).cpu().numpy()  # Remove batch dimension

        # Ensure we have the right number of dimensions
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)
        elif array.ndim == 3 and array.shape[0] in [1, 3, 4]:  # CHW format
            array = np.transpose(array, (1, 2, 0))  # Convert to HWC

        # Convert to uint8
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)

        # Handle different channel counts
        if array.shape[2] == 1:  # Grayscale
            array = array.squeeze(2)
            return Image.fromarray(array, mode='L')
        elif array.shape[2] == 3:  # RGB
            return Image.fromarray(array, mode='RGB')
        elif array.shape[2] == 4:  # RGBA
            return Image.fromarray(array, mode='RGBA')
        else:
            raise ValueError(f"Unsupported number of channels: {array.shape[2]}")

    def pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI tensor"""
        # Convert PIL to numpy array
        array = np.array(pil_image).astype(np.float32) / 255.0

        # Ensure we have 3 dimensions (HWC)
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)

        # Convert to tensor and add batch dimension: [1, H, W, C]
        tensor = torch.from_numpy(array).unsqueeze(0)
        return tensor


class TopazDenoiseNode:
    """
    ComfyUI Node for Topaz Labs Denoise API (Sync Only)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (["Standard", "Strong", "RAW"], {
                    "default": "Standard"
                }),
                "output_format": (["jpeg", "png", "tiff"], {
                    "default": "png"
                }),
            },
            "optional": {
                "output_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number"
                }),
                "output_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32000,
                    "step": 1,
                    "display": "number"
                }),
                "strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("denoised_image",)
    FUNCTION = "denoise_image"
    CATEGORY = "Topaz Labs"
    DESCRIPTION = "Denoise images using Topaz Labs AI models (Sync mode only)"

    def call_topaz_api(self, image_data: bytes, params: Dict[str, Any], api_key: str) -> bytes:
        """Call Topaz Labs Denoise API (Sync mode only)"""
        base_url = "https://api.topazlabs.com/image/v1"
        endpoint = "/denoise"

        headers = {
            "X-API-Key": api_key,
            "Accept": "*/*"
        }

        files = {
            'image': ('image.png', image_data, 'image/png')
        }

        data = {}
        for key, value in params.items():
            if value is not None and value != "":
                data[key] = str(value) if not isinstance(value, bool) else str(value).lower()

        print(f"Calling Topaz Denoise API: {base_url}{endpoint}")
        print(f"Parameters: {data}")

        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                headers=headers,
                files=files,
                data=data,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            return response.content

        except requests.exceptions.RequestException as e:
            raise Exception(f"Denoise API request failed: {str(e)}")

    def denoise_image(self, image, api_key, model, output_format,
                     output_height=0, output_width=0, strength=0.5):

        # Validate and get API key
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise Exception(str(e))

        # Input image is already validated by ComfyUI

        # Convert ComfyUI tensor to PIL Image
        pil_image = self.tensor_to_pil(image)

        # Get image info for logging
        input_info = {
            'width': pil_image.width,
            'height': pil_image.height,
            'mode': pil_image.mode,
            'megapixels': (pil_image.width * pil_image.height) / 1_000_000
        }

        # Calculate output dimensions
        output_width, output_height = calculate_output_dimensions(
            pil_image.width, pil_image.height, output_width, output_height
        )

        # Prepare image data
        image_data = prepare_image_for_api(pil_image)

        # Prepare API parameters
        params = {
            'model': model,
            'output_format': output_format,
            'output_width': str(output_width),
            'output_height': str(output_height),
            'strength': str(strength)
        }

        # Log processing info
        log_processing_info("denoise", model, input_info, params)

        try:
            # Call API (sync mode only)
            result_data = self.call_topaz_api(image_data, params, validated_api_key)

            # Convert result back to PIL Image
            result_image = Image.open(io.BytesIO(result_data))

            # Log output info
            output_info = {
                'width': result_image.width,
                'height': result_image.height,
                'mode': result_image.mode,
                'megapixels': (result_image.width * result_image.height) / 1_000_000
            }
            log_processing_info("denoise", model, output_info, {"status": "completed"})

            # Convert to ComfyUI tensor
            result_tensor = self.pil_to_tensor(result_image)

            return (result_tensor,)

        except Exception as e:
            print(f"Error denoising image: {str(e)}")
            raise e

    def tensor_to_pil(self, tensor):
        """Convert ComfyUI tensor to PIL Image"""
        # ComfyUI tensors are in format [batch, height, width, channels]
        array = tensor.squeeze(0).cpu().numpy()  # Remove batch dimension

        # Ensure we have the right number of dimensions
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)
        elif array.ndim == 3 and array.shape[0] in [1, 3, 4]:  # CHW format
            array = np.transpose(array, (1, 2, 0))  # Convert to HWC

        # Convert to uint8
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)

        # Handle different channel counts
        if array.shape[2] == 1:  # Grayscale
            array = array.squeeze(2)
            return Image.fromarray(array, mode='L')
        elif array.shape[2] == 3:  # RGB
            return Image.fromarray(array, mode='RGB')
        elif array.shape[2] == 4:  # RGBA
            return Image.fromarray(array, mode='RGBA')
        else:
            raise ValueError(f"Unsupported number of channels: {array.shape[2]}")

    def pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI tensor"""
        # Convert PIL to numpy array
        array = np.array(pil_image).astype(np.float32) / 255.0

        # Ensure we have 3 dimensions (HWC)
        if array.ndim == 2:  # Grayscale
            array = np.expand_dims(array, axis=2)

        # Convert to tensor and add batch dimension: [1, H, W, C]
        tensor = torch.from_numpy(array).unsqueeze(0)
        return tensor


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "TopazEnhanceNode": TopazEnhanceNode,
    "TopazSharpenNode": TopazSharpenNode,
    "TopazDenoiseNode": TopazDenoiseNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TopazEnhanceNode": "Topaz Image Enhance",
    "TopazSharpenNode": "Topaz Image Sharpen",
    "TopazDenoiseNode": "Topaz Image Denoise",
}
