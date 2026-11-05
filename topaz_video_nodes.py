"""
Topaz Labs Video Processing Nodes for ComfyUI
Provides video enhancement, frame interpolation, and restoration capabilities
Compatible with ComfyUI's Load Video and Save Video workflow
"""

import os
import time
import requests
import json
import tempfile
import torch
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

try:
    from .utils import (
        get_api_key, get_video_info, validate_video_file,
        log_video_processing_info, format_duration, estimate_video_processing_time
    )
    from .config import (
        TOPAZ_VIDEO_API_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_ASYNC_TIMEOUT,
        VIDEO_ENHANCEMENT_MODELS, ADVANCED_VIDEO_MODELS, VIDEO_CONTAINERS,
        VIDEO_CODECS, VIDEO_PROFILES, AUDIO_CODECS, AUDIO_TRANSFER_OPTIONS,
        COMPRESSION_LEVELS, DEFAULT_VIDEO_PARAMS
    )
except ImportError:
    # Fallback for standalone testing
    from utils import (
        get_api_key, get_video_info, validate_video_file,
        log_video_processing_info, format_duration, estimate_video_processing_time
    )
    from config import (
        TOPAZ_VIDEO_API_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_ASYNC_TIMEOUT,
        VIDEO_ENHANCEMENT_MODELS, ADVANCED_VIDEO_MODELS, VIDEO_CONTAINERS,
        VIDEO_CODECS, VIDEO_PROFILES, AUDIO_CODECS, AUDIO_TRANSFER_OPTIONS,
        COMPRESSION_LEVELS, DEFAULT_VIDEO_PARAMS
    )

class TopazVideoEnhanceNode:
    """
    ComfyUI Node for Topaz Labs Video Enhancement API
    Supports video upscaling, denoising, and general enhancement
    Works with ComfyUI's Load Video -> Save Video workflow
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # Get enhancement models (non-interpolation)
        enhancement_models = [
            f"{key} - {value['name']}"
            for key, value in VIDEO_ENHANCEMENT_MODELS.items()
            if value['category'] == 'enhancement'
        ]

        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Input video frames from Load Video node"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (enhancement_models, {
                    "default": enhancement_models[0] if enhancement_models else "prob-4 - Proteus General"
                }),
                "frame_rate": ("FLOAT", {
                    "default": 30.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 0.1,
                    "display": "number",
                    "tooltip": "Frame rate for temporary video processing"
                }),
            },
            "optional": {
                "output_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 7680,
                    "step": 2,
                    "display": "number",
                    "tooltip": "0 means keep original width"
                }),
                "output_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4320,
                    "step": 2,
                    "display": "number",
                    "tooltip": "0 means keep original height"
                }),
                "output_framerate": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 120.0,
                    "step": 0.1,
                    "display": "number",
                    "tooltip": "0 means keep original framerate"
                }),
                "container": (VIDEO_CONTAINERS, {
                    "default": "mp4"
                }),
                "video_encoder": (VIDEO_CODECS, {
                    "default": "H264"
                }),
                "video_profile": (VIDEO_PROFILES, {
                    "default": "High"
                }),
                "audio_codec": (AUDIO_CODECS, {
                    "default": "AAC"
                }),
                "audio_transfer": (AUDIO_TRANSFER_OPTIONS, {
                    "default": "Copy"
                }),
                "compression_level": (COMPRESSION_LEVELS, {
                    "default": "High"
                }),
                "proxy_url": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "http://proxy.server.com:8080 (可选，留空表示直连)"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("enhanced_images",)
    FUNCTION = "enhance_video_frames"
    CATEGORY = "Topaz Labs/Video"
    DESCRIPTION = "Enhance video frames using Topaz Labs AI models"

    def extract_model_key(self, model_display: str) -> str:
        """Extract model key from display string"""
        return model_display.split(" - ")[0]

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

    def images_to_temp_video(self, images, frame_rate):
        """Convert ComfyUI image batch to temporary video file"""
        import cv2

        # Create temporary video file
        temp_dir = tempfile.gettempdir()
        temp_video_path = os.path.join(temp_dir, f"topaz_temp_input_{int(time.time())}.mp4")

        # Get first image to determine dimensions
        first_pil = self.tensor_to_pil(images[0])
        width, height = first_pil.size

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, frame_rate, (width, height))

        # Convert each image and write to video
        for i, img_tensor in enumerate(images):
            pil_img = self.tensor_to_pil(img_tensor)
            # Convert PIL to OpenCV format (BGR)
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            out.write(cv_img)

        out.release()
        return temp_video_path

    def temp_video_to_images(self, video_path):
        """Convert video file back to ComfyUI image batch"""
        import cv2

        cap = cv2.VideoCapture(video_path)
        images = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert OpenCV frame (BGR) to PIL (RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)

            # Convert to ComfyUI tensor
            tensor = self.pil_to_tensor(pil_img)
            images.append(tensor)

        cap.release()

        # Combine all tensors into a batch
        if images:
            batch_tensor = torch.cat(images, dim=0)
            return batch_tensor
        else:
            raise ValueError("No frames found in processed video")

    def cleanup_temp_files(self, file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                print(f"Warning: Could not clean up {file_path}: {e}")

    def get_video_metadata(self, video_path):
        """Get video metadata using OpenCV"""
        import cv2
        import os

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        # Get file info
        file_size = os.path.getsize(video_path)
        file_ext = os.path.splitext(video_path)[1].lower().lstrip('.')

        return {
            'width': width,
            'height': height,
            'framerate': fps,
            'frame_count': frame_count,
            'duration': duration,
            'size_bytes': file_size,
            'container': file_ext,
            'path': video_path
        }

    def process_video_with_topaz(self, video_path, api_key, model_key,
                                output_width, output_height, output_framerate,
                                container, video_encoder, video_profile,
                                audio_codec, audio_transfer, compression_level,
                                proxy_url=""):
        """Process video using Topaz API async workflow and return enhanced video path"""

        # Get video info using OpenCV
        video_info = self.get_video_metadata(video_path)

        # Prepare output parameters
        final_width = output_width if output_width > 0 else video_info['width']
        final_height = output_height if output_height > 0 else video_info['height']
        final_framerate = output_framerate if output_framerate > 0 else video_info['framerate']

        print(f"Input resolution: {video_info['width']}x{video_info['height']}")
        print(f"Output resolution: {final_width}x{final_height}")
        print(f"Input framerate: {video_info['framerate']}")
        print(f"Output framerate: {final_framerate}")

        output_params = {
            'width': final_width,
            'height': final_height,
            'framerate': final_framerate,
            'container': container,
            'video_encoder': video_encoder,
            'video_profile': video_profile,
            'audio_codec': audio_codec,
            'audio_transfer': audio_transfer,
            'compression_level': compression_level
        }

        # Use the proper async workflow
        return self.process_video_async_workflow(video_path, video_info, model_key, output_params, api_key, proxy_url)

    def process_video_async_workflow(self, video_path: str, video_info: dict, model_key: str, output_params: dict, api_key: str, proxy_url: str = "") -> str:
        """Process video using the correct Topaz API async workflow"""

        try:
            # Step 1: Create request
            print("Step 1: Creating video enhancement request...")
            request_result = self.create_video_request(video_info, model_key, output_params, api_key, proxy_url)
            request_id = request_result['requestId']

            # Step 2: Accept request
            print("Step 2: Accepting video request...")
            accept_result = self.accept_video_request(request_id, api_key, proxy_url)

            # Get upload URLs from API response (field name is 'urls' according to API docs)
            upload_urls = (accept_result.get('urls') or
                          accept_result.get('uploadUrls') or
                          accept_result.get('uploadUrl') or
                          accept_result.get('upload_urls') or
                          accept_result.get('upload_url') or [])

            # Handle single URL as string
            if isinstance(upload_urls, str):
                upload_urls = [upload_urls]

            if not upload_urls:
                raise Exception(f"No upload URLs received. Response keys: {list(accept_result.keys())}")

            # Step 3: Upload video
            print("Step 3: Uploading video...")
            etag = self.upload_video_file(video_path, upload_urls[0], proxy_url)

            # Step 4: Complete upload
            print("Step 4: Completing upload and starting processing...")
            self.complete_video_upload(request_id, etag, api_key, proxy_url)

            # Step 5: Monitor processing and download result
            print("Step 5: Monitoring processing status...")
            enhanced_video_path = self.monitor_and_download_video(request_id, api_key, proxy_url)

            return enhanced_video_path

        except Exception as e:
            raise Exception(f"Video processing failed: {str(e)}")

    def monitor_and_download_video(self, request_id, api_key, proxy_url=""):
        """Monitor processing status and download enhanced video"""

        max_wait_time = DEFAULT_ASYNC_TIMEOUT
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            # Check status
            status_result = self.check_video_status(request_id, api_key, proxy_url)
            status = status_result.get('status')

            print(f"Video processing status: {status}")

            if status in ['completed', 'complete']:  # API returns 'complete' not 'completed'
                # Debug: Print full status response to see available fields
                print(f"Complete status response: {json.dumps(status_result, indent=2)}")

                # Get download URL from the correct API response structure
                download_info = status_result.get('download', {})
                download_url = download_info.get('url')

                # Fallback to other possible field names
                if not download_url:
                    download_url = (status_result.get('downloadUrl') or
                                   status_result.get('download_url') or
                                   status_result.get('outputUrl') or
                                   status_result.get('output_url') or
                                   status_result.get('resultUrl') or
                                   status_result.get('result_url'))

                if download_url:
                    print(f"Found download URL: {download_url[:50]}...")
                    temp_dir = tempfile.gettempdir()
                    output_path = os.path.join(temp_dir, f"topaz_enhanced_{int(time.time())}.mp4")
                    return self.download_processed_video(download_url, output_path, proxy_url)
                else:
                    print(f"No download URL found. Available keys: {list(status_result.keys())}")
                    raise Exception("No download URL provided")

            elif status == 'failed':
                error_msg = status_result.get('error', 'Unknown error')
                raise Exception(f"Video processing failed: {error_msg}")

            elif status in ['queued', 'processing']:
                time.sleep(30)  # Wait 30 seconds before next check

            else:
                print(f"Unknown status: {status}, continuing to wait...")
                time.sleep(30)

        raise Exception("Video processing timed out")

    def create_video_request(self, video_info: dict, model_key: str, output_params: dict, api_key: str, proxy_url: str = "") -> dict:
        """Create video enhancement request"""
        
        # Prepare source information using actual video metadata
        source_info = {
            "container": video_info.get('container', 'mp4'),
            "size": video_info.get('size_bytes', 0),
            "duration": video_info.get('duration', 60),
            "frameRate": video_info.get('framerate', 30),
            "frameCount": video_info.get('frame_count', 1800),
            "resolution": {
                "width": video_info.get('width', 1920),
                "height": video_info.get('height', 1080)
            }
        }
        
        # Prepare filters
        filters = [{
            "model": model_key
        }]
        
        # Prepare output settings
        output_info = {
            "frameRate": output_params.get('framerate', source_info['frameRate']),
            "audioTransfer": output_params.get('audio_transfer', 'Copy'),
            "audioCodec": output_params.get('audio_codec', 'AAC'),
            "videoEncoder": output_params.get('video_encoder', 'H264'),
            "videoProfile": "High",  # API only supports High profile
            "dynamicCompressionLevel": output_params.get('compression_level', 'High'),
            "container": output_params.get('container', 'mp4'),
            "resolution": {
                "width": output_params.get('width', source_info['resolution']['width']),
                "height": output_params.get('height', source_info['resolution']['height'])
            }
        }
        
        # Prepare request payload
        request_data = {
            "source": source_info,
            "filters": filters,
            "output": output_info
        }
        
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"Creating video request with data: {json.dumps(request_data, indent=2)}")

        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }
            print(f"Using proxy: {proxy_url.strip()}")

        try:
            response = requests.post(
                f"{TOPAZ_VIDEO_API_BASE_URL}/",
                headers=headers,
                json=request_data,
                timeout=DEFAULT_TIMEOUT,
                proxies=proxies
            )

            # Print detailed error information
            print(f"API Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"API Response Text: {response.text}")

            response.raise_for_status()
            result = response.json()

            print(f"Video request created successfully:")
            print(f"Request ID: {result.get('requestId')}")
            print(f"Cost estimate: {result.get('estimates', {}).get('cost', 'Unknown')} credits")
            print(f"Time estimate: {result.get('estimates', {}).get('time', 'Unknown')} seconds")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create video request: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse status: {e.response.status_code}"
                error_msg += f"\nResponse text: {e.response.text}"
            raise Exception(error_msg)

    def accept_video_request(self, request_id: str, api_key: str, proxy_url: str = "") -> dict:
        """Accept video request and get upload URLs"""

        headers = {
            "X-API-Key": api_key,
            "Accept": "application/json"
        }

        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }

        try:
            response = requests.patch(
                f"{TOPAZ_VIDEO_API_BASE_URL}/{request_id}/accept",
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
                proxies=proxies
            )

            print(f"Accept request response status: {response.status_code}")
            print(f"Accept request response headers: {dict(response.headers)}")

            response.raise_for_status()
            result = response.json()

            print(f"Accept request response body: {json.dumps(result, indent=2)}")

            # Check if upload URLs are in the response (API uses 'urls' field)
            upload_urls = result.get('urls', [])
            if not upload_urls:
                print(f"Warning: No upload URLs found in response. Available keys: {list(result.keys())}")
            else:
                print(f"Found {len(upload_urls)} upload URLs")

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to accept video request: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse status: {e.response.status_code}"
                error_msg += f"\nResponse text: {e.response.text}"
            raise Exception(error_msg)

    def upload_video_file(self, video_path: str, upload_url: str, proxy_url: str = "") -> str:
        """Upload video file to provided URL with retry mechanism"""

        import os

        file_size = os.path.getsize(video_path)
        print(f"Uploading video file: {video_path} (Size: {file_size / 1024 / 1024:.1f} MB)")

        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }
            print(f"Using proxy for upload: {proxy_url.strip()}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(video_path, 'rb') as video_file:
                    headers = {
                        "Content-Type": "video/mp4"
                    }

                    print(f"Upload attempt {attempt + 1}/{max_retries}...")

                    # Use shorter timeout for better error handling
                    response = requests.put(
                        upload_url,
                        data=video_file,
                        headers=headers,
                        timeout=(10, 300),  # (connect_timeout, read_timeout) - shorter timeouts
                        stream=False,  # Don't use streaming for smaller files
                        proxies=proxies  # Use proxy if provided
                    )

                    response.raise_for_status()

                    # Extract eTag from response headers
                    etag = response.headers.get('ETag', '').strip('"')
                    print(f"Video uploaded successfully. ETag: {etag}")

                    return etag

            except requests.exceptions.Timeout as e:
                print(f"Upload attempt {attempt + 1} timed out: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Upload failed after {max_retries} attempts due to timeout")
                print(f"Retrying in 5 seconds...")
                time.sleep(5)

            except requests.exceptions.ConnectionError as e:
                print(f"Upload attempt {attempt + 1} connection error: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Upload failed after {max_retries} attempts due to connection error")
                print(f"Retrying in 5 seconds...")
                time.sleep(5)

            except Exception as e:
                print(f"Upload attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Upload failed after {max_retries} attempts: {str(e)}")
                print(f"Retrying in 5 seconds...")
                time.sleep(5)

        raise Exception("Upload failed: Maximum retries exceeded")

    def complete_video_upload(self, request_id: str, etag: str, api_key: str, proxy_url: str = "") -> dict:
        """Complete video upload and start processing"""
        
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        upload_results = [{
            "partNum": 1,
            "eTag": etag
        }]
        
        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }

        try:
            response = requests.patch(
                f"{TOPAZ_VIDEO_API_BASE_URL}/{request_id}/complete-upload",
                headers=headers,
                json={"uploadResults": upload_results},
                timeout=DEFAULT_TIMEOUT,
                proxies=proxies
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"Video upload completed. Processing started.")
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to complete video upload: {str(e)}")

    def check_video_status(self, request_id: str, api_key: str, proxy_url: str = "") -> dict:
        """Check video processing status"""
        
        headers = {
            "X-API-Key": api_key,
            "Accept": "application/json"
        }
        
        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }

        try:
            # Use a fresh connection for each status check to avoid connection issues
            response = requests.get(
                f"{TOPAZ_VIDEO_API_BASE_URL}/{request_id}/status",
                headers=headers,
                timeout=30,  # Shorter timeout for status checks
                proxies=proxies,
                stream=False  # Don't use streaming for status checks
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error during status check: {str(e)}")
            # Return a default status to continue waiting
            return {'status': 'processing'}
        except requests.exceptions.Timeout as e:
            print(f"Timeout during status check: {str(e)}")
            # Return a default status to continue waiting
            return {'status': 'processing'}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to check video status: {str(e)}")

    def download_processed_video(self, download_url: str, output_path: str, proxy_url: str = "") -> str:
        """Download processed video"""
        
        # Setup proxy if provided
        proxies = None
        if proxy_url and proxy_url.strip():
            proxies = {
                'http': proxy_url.strip(),
                'https': proxy_url.strip()
            }

        try:
            print(f"Downloading processed video to: {output_path}")
            response = requests.get(download_url, stream=True, timeout=600, proxies=proxies)
            response.raise_for_status()
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Video downloaded successfully: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")

    def enhance_video_frames(self, images, api_key, model, frame_rate=30.0,
                           output_width=0, output_height=0, output_framerate=0.0,
                           container="mp4", video_encoder="H264", video_profile="Main",
                           audio_codec="AAC", audio_transfer="Copy", compression_level="High",
                           proxy_url=""):

        # Validate inputs
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise ValueError(str(e))

        if images is None or len(images) == 0:
            raise ValueError("No input images provided")

        # Extract model key
        model_key = self.extract_model_key(model)

        print(f"Processing {len(images)} frames with Topaz {model}")

        try:
            # Step 1: Convert images to temporary video
            temp_video_path = self.images_to_temp_video(images, frame_rate)
            print(f"Created temporary video: {temp_video_path}")

            # Step 2: Process video with Topaz API
            enhanced_video_path = self.process_video_with_topaz(
                temp_video_path, validated_api_key, model_key,
                output_width, output_height, output_framerate,
                container, video_encoder, video_profile,
                audio_codec, audio_transfer, compression_level,
                proxy_url
            )
            print(f"Enhanced video created: {enhanced_video_path}")

            # Step 3: Convert enhanced video back to images
            enhanced_images = self.temp_video_to_images(enhanced_video_path)
            print(f"Converted back to {len(enhanced_images)} enhanced frames")

            # Step 4: Clean up temporary files
            self.cleanup_temp_files([temp_video_path, enhanced_video_path])

            return (enhanced_images,)

        except Exception as e:
            print(f"Error enhancing video frames: {str(e)}")
            # Return original images if processing fails
            return (images,)

class TopazVideoInterpolateNode:
    """
    ComfyUI Node for Topaz Labs Video Frame Interpolation API
    Supports frame interpolation for slow motion and framerate conversion
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # Get interpolation models
        interpolation_models = [
            f"{key} - {value['name']}"
            for key, value in VIDEO_ENHANCEMENT_MODELS.items()
            if value['category'] == 'interpolation'
        ]

        return {
            "required": {
                "video_path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Path to input video file"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (interpolation_models, {
                    "default": interpolation_models[0] if interpolation_models else "apo-8 - Apollo General"
                }),
                "output_path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Path for output video file (optional)"
                }),
                "target_fps": ("FLOAT", {
                    "default": 60.0,
                    "min": 24.0,
                    "max": 240.0,
                    "step": 0.1,
                    "display": "number"
                }),
            },
            "optional": {
                "slowmo_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 1.0,
                    "max": 8.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Slow motion factor (1.0 = normal speed)"
                }),
                "duplicate_frames": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enable",
                    "label_off": "Disable",
                    "tooltip": "Allow frame duplication for better results"
                }),
                "duplicate_threshold": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider",
                    "tooltip": "Threshold for frame duplication detection"
                }),
                "container": (VIDEO_CONTAINERS, {
                    "default": "mp4"
                }),
                "video_encoder": (VIDEO_CODECS, {
                    "default": "H264"
                }),
                "audio_transfer": (AUDIO_TRANSFER_OPTIONS, {
                    "default": "Copy"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_video_path", "request_id", "status_info")
    FUNCTION = "interpolate_video"
    CATEGORY = "Topaz Labs/Video"
    DESCRIPTION = "Interpolate video frames for slow motion and framerate conversion"

    def extract_model_key(self, model_display: str) -> str:
        """Extract model key from display string"""
        return model_display.split(" - ")[0]

    def create_interpolation_request(self, video_info: dict, model_key: str, interpolation_params: dict, api_key: str) -> dict:
        """Create video interpolation request"""

        # Prepare source information
        source_info = {
            "container": video_info.get('container', 'mp4'),
            "size": video_info.get('size_bytes', 0),
            "duration": video_info.get('duration', 60),
            "frameRate": video_info.get('framerate', 30),
            "frameCount": video_info.get('frame_count', 1800),
            "resolution": {
                "width": video_info.get('width', 1920),
                "height": video_info.get('height', 1080)
            }
        }

        # Prepare filters with interpolation parameters
        filters = [{
            "model": model_key,
            "slowmo": interpolation_params.get('slowmo_factor', 1.0),
            "fps": interpolation_params.get('target_fps', 60.0),
            "duplicate": interpolation_params.get('duplicate_frames', True),
            "duplicateThreshold": interpolation_params.get('duplicate_threshold', 0.1)
        }]

        # Prepare output settings
        output_info = {
            "frameRate": interpolation_params.get('target_fps', 60.0),
            "audioTransfer": interpolation_params.get('audio_transfer', 'Copy'),
            "audioCodec": "AAC",
            "videoEncoder": interpolation_params.get('video_encoder', 'H264'),
            "videoProfile": "Main",
            "dynamicCompressionLevel": "High",
            "container": interpolation_params.get('container', 'mp4'),
            "resolution": source_info['resolution']  # Keep original resolution
        }

        # Prepare request payload
        request_data = {
            "source": source_info,
            "filters": filters,
            "output": output_info
        }

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print(f"Creating video interpolation request with data: {json.dumps(request_data, indent=2)}")

        try:
            response = requests.post(
                f"{TOPAZ_VIDEO_API_BASE_URL}/",
                headers=headers,
                json=request_data,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()

            print(f"Video interpolation request created successfully:")
            print(f"Request ID: {result.get('requestId')}")
            print(f"Cost estimate: {result.get('estimates', {}).get('cost', 'Unknown')} credits")
            print(f"Time estimate: {result.get('estimates', {}).get('time', 'Unknown')} seconds")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create video interpolation request: {str(e)}")

    def interpolate_video(self, video_path, api_key, model, output_path="", target_fps=60.0,
                         slowmo_factor=1.0, duplicate_frames=True, duplicate_threshold=0.1,
                         container="mp4", video_encoder="H264", audio_transfer="Copy"):

        # Validate inputs
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise ValueError(str(e))

        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")

        if not validate_video_file(video_path):
            raise ValueError(f"Unsupported video format: {video_path}")

        # Extract model key
        model_key = self.extract_model_key(model)

        # Get video info
        video_info = get_video_info(video_path)

        # Prepare interpolation parameters
        interpolation_params = {
            'target_fps': target_fps,
            'slowmo_factor': slowmo_factor,
            'duplicate_frames': duplicate_frames,
            'duplicate_threshold': duplicate_threshold,
            'container': container,
            'video_encoder': video_encoder,
            'audio_transfer': audio_transfer
        }

        # Generate output path if not provided
        if not output_path:
            input_path = Path(video_path)
            output_path = str(input_path.parent / f"{input_path.stem}_interpolated{input_path.suffix}")

        # Log processing info
        log_video_processing_info('interpolate', model, video_info, interpolation_params)

        try:
            # Use the same workflow as enhancement node
            # Step 1: Create request
            print("Step 1: Creating video interpolation request...")
            request_result = self.create_interpolation_request(video_info, model_key, interpolation_params, validated_api_key)
            request_id = request_result['requestId']

            # Reuse methods from TopazVideoEnhanceNode for the rest of the workflow
            enhance_node = TopazVideoEnhanceNode()

            # Step 2: Accept request
            print("Step 2: Accepting video request...")
            accept_result = enhance_node.accept_video_request(request_id, validated_api_key)

            # Get upload URLs from API response (field name is 'urls' according to API docs)
            upload_urls = (accept_result.get('urls') or
                          accept_result.get('uploadUrls') or
                          accept_result.get('uploadUrl') or
                          accept_result.get('upload_urls') or
                          accept_result.get('upload_url') or [])

            # Handle single URL as string
            if isinstance(upload_urls, str):
                upload_urls = [upload_urls]

            if not upload_urls:
                raise Exception(f"No upload URLs received. Response keys: {list(accept_result.keys())}")

            # Step 3: Upload video
            print("Step 3: Uploading video...")
            etag = enhance_node.upload_video_file(video_path, upload_urls[0])

            # Step 4: Complete upload
            print("Step 4: Completing upload and starting processing...")
            enhance_node.complete_video_upload(request_id, etag, validated_api_key)

            # Step 5: Monitor processing
            print("Step 5: Monitoring processing status...")
            max_wait_time = DEFAULT_ASYNC_TIMEOUT * 2  # Interpolation takes longer
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                status_result = enhance_node.check_video_status(request_id, validated_api_key)
                status = status_result.get('status', 'unknown')

                print(f"Processing status: {status}")

                if status in ['completed', 'complete']:  # API returns 'complete' not 'completed'
                    # Get download URL from the correct API response structure
                    download_info = status_result.get('download', {})
                    download_url = download_info.get('url')

                    # Fallback to other possible field names
                    if not download_url:
                        download_url = status_result.get('downloadUrl')
                    if download_url:
                        # Step 6: Download result
                        print("Step 6: Downloading processed video...")
                        final_output_path = enhance_node.download_processed_video(download_url, output_path)

                        status_info = f"Video interpolation completed successfully. Processing time: {time.time() - start_time:.1f}s"
                        return (final_output_path, request_id, status_info)
                    else:
                        raise Exception("No download URL provided")

                elif status == 'failed':
                    error_msg = status_result.get('error', 'Unknown error')
                    raise Exception(f"Video processing failed: {error_msg}")

                elif status in ['queued', 'processing']:
                    time.sleep(30)  # Wait 30 seconds before next check

                else:
                    print(f"Unknown status: {status}, continuing to wait...")
                    time.sleep(30)

            raise Exception("Video processing timed out")

        except Exception as e:
            error_msg = f"Error interpolating video: {str(e)}"
            print(error_msg)
            return ("", request_id if 'request_id' in locals() else "", error_msg)


class TopazVideoRestoreNode:
    """
    ComfyUI Node for Topaz Labs Advanced Video Restoration
    Supports restoration of old, damaged, or low-quality videos
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # Get advanced restoration models
        restoration_models = [
            f"{key} - {value['name']}"
            for key, value in ADVANCED_VIDEO_MODELS.items()
        ]

        return {
            "required": {
                "video_path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Path to input video file"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter your Topaz Labs API key"
                }),
                "model": (restoration_models, {
                    "default": restoration_models[0] if restoration_models else "dtd-4 - Dione Robust"
                }),
                "output_path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Path for output video file (optional)"
                }),
            },
            "optional": {
                "upscale_factor": (["1x", "2x", "4x"], {
                    "default": "2x"
                }),
                "output_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 7680,
                    "step": 2,
                    "display": "number",
                    "tooltip": "0 means auto-calculate based on upscale factor"
                }),
                "output_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 4320,
                    "step": 2,
                    "display": "number",
                    "tooltip": "0 means auto-calculate based on upscale factor"
                }),
                "preserve_grain": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Preserve",
                    "label_off": "Remove",
                    "tooltip": "Preserve original film grain"
                }),
                "container": (VIDEO_CONTAINERS, {
                    "default": "mp4"
                }),
                "video_encoder": (VIDEO_CODECS, {
                    "default": "H265"
                }),
                "compression_level": (COMPRESSION_LEVELS, {
                    "default": "High"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_video_path", "request_id", "status_info")
    FUNCTION = "restore_video"
    CATEGORY = "Topaz Labs/Video"
    DESCRIPTION = "Restore old, damaged, or low-quality videos using advanced AI models"

    def extract_model_key(self, model_display: str) -> str:
        """Extract model key from display string"""
        return model_display.split(" - ")[0]

    def calculate_upscale_dimensions(self, original_width: int, original_height: int, upscale_factor: str) -> tuple:
        """Calculate upscaled dimensions"""
        factor = int(upscale_factor.replace('x', ''))
        return original_width * factor, original_height * factor

    def create_restoration_request(self, video_info: dict, model_key: str, restoration_params: dict, api_key: str) -> dict:
        """Create video restoration request"""

        # Prepare source information
        source_info = {
            "container": video_info.get('container', 'mp4'),
            "size": video_info.get('size_bytes', 0),
            "duration": video_info.get('duration', 60),
            "frameRate": video_info.get('framerate', 30),
            "frameCount": video_info.get('frame_count', 1800),
            "resolution": {
                "width": video_info.get('width', 720),  # Assume older content
                "height": video_info.get('height', 480)
            }
        }

        # Calculate output resolution
        if restoration_params.get('output_width') and restoration_params.get('output_height'):
            output_width = restoration_params['output_width']
            output_height = restoration_params['output_height']
        else:
            output_width, output_height = self.calculate_upscale_dimensions(
                source_info['resolution']['width'],
                source_info['resolution']['height'],
                restoration_params.get('upscale_factor', '2x')
            )

        # Prepare filters
        filters = [{
            "model": model_key
        }]

        # Add model-specific parameters if needed
        if restoration_params.get('preserve_grain'):
            filters[0]['preserveGrain'] = True

        # Prepare output settings
        output_info = {
            "frameRate": source_info['frameRate'],  # Keep original framerate
            "audioTransfer": "Copy",
            "audioCodec": "AAC",
            "videoEncoder": restoration_params.get('video_encoder', 'H265'),
            "videoProfile": "Main",
            "dynamicCompressionLevel": restoration_params.get('compression_level', 'High'),
            "container": restoration_params.get('container', 'mp4'),
            "resolution": {
                "width": output_width,
                "height": output_height
            }
        }

        # Prepare request payload
        request_data = {
            "source": source_info,
            "filters": filters,
            "output": output_info
        }

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print(f"Creating video restoration request with data: {json.dumps(request_data, indent=2)}")

        try:
            response = requests.post(
                f"{TOPAZ_VIDEO_API_BASE_URL}/",
                headers=headers,
                json=request_data,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()

            print(f"Video restoration request created successfully:")
            print(f"Request ID: {result.get('requestId')}")
            print(f"Cost estimate: {result.get('estimates', {}).get('cost', 'Unknown')} credits")
            print(f"Time estimate: {result.get('estimates', {}).get('time', 'Unknown')} seconds")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create video restoration request: {str(e)}")

    def restore_video(self, video_path, api_key, model, output_path="",
                     upscale_factor="2x", output_width=0, output_height=0,
                     preserve_grain=False, container="mp4", video_encoder="H265",
                     compression_level="High"):

        # Validate inputs
        try:
            validated_api_key = get_api_key(api_key)
        except ValueError as e:
            raise ValueError(str(e))

        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")

        if not validate_video_file(video_path):
            raise ValueError(f"Unsupported video format: {video_path}")

        # Extract model key
        model_key = self.extract_model_key(model)

        # Get video info
        video_info = get_video_info(video_path)

        # Prepare restoration parameters
        restoration_params = {
            'upscale_factor': upscale_factor,
            'output_width': output_width if output_width > 0 else None,
            'output_height': output_height if output_height > 0 else None,
            'preserve_grain': preserve_grain,
            'container': container,
            'video_encoder': video_encoder,
            'compression_level': compression_level
        }

        # Generate output path if not provided
        if not output_path:
            input_path = Path(video_path)
            output_path = str(input_path.parent / f"{input_path.stem}_restored{input_path.suffix}")

        # Log processing info
        log_video_processing_info('restore', model, video_info, restoration_params)

        try:
            # Use the same workflow as enhancement node
            # Step 1: Create request
            print("Step 1: Creating video restoration request...")
            request_result = self.create_restoration_request(video_info, model_key, restoration_params, validated_api_key)
            request_id = request_result['requestId']

            # Reuse methods from TopazVideoEnhanceNode for the rest of the workflow
            enhance_node = TopazVideoEnhanceNode()

            # Step 2: Accept request
            print("Step 2: Accepting video request...")
            accept_result = enhance_node.accept_video_request(request_id, validated_api_key)

            # Get upload URLs from API response (field name is 'urls' according to API docs)
            upload_urls = (accept_result.get('urls') or
                          accept_result.get('uploadUrls') or
                          accept_result.get('uploadUrl') or
                          accept_result.get('upload_urls') or
                          accept_result.get('upload_url') or [])

            # Handle single URL as string
            if isinstance(upload_urls, str):
                upload_urls = [upload_urls]

            if not upload_urls:
                raise Exception(f"No upload URLs received. Response keys: {list(accept_result.keys())}")

            # Step 3: Upload video
            print("Step 3: Uploading video...")
            etag = enhance_node.upload_video_file(video_path, upload_urls[0])

            # Step 4: Complete upload
            print("Step 4: Completing upload and starting processing...")
            enhance_node.complete_video_upload(request_id, etag, validated_api_key)

            # Step 5: Monitor processing
            print("Step 5: Monitoring processing status...")
            max_wait_time = DEFAULT_ASYNC_TIMEOUT * 3  # Restoration takes even longer
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                status_result = enhance_node.check_video_status(request_id, validated_api_key)
                status = status_result.get('status', 'unknown')

                print(f"Processing status: {status}")

                if status in ['completed', 'complete']:  # API returns 'complete' not 'completed'
                    # Get download URL from the correct API response structure
                    download_info = status_result.get('download', {})
                    download_url = download_info.get('url')

                    # Fallback to other possible field names
                    if not download_url:
                        download_url = status_result.get('downloadUrl')
                    if download_url:
                        # Step 6: Download result
                        print("Step 6: Downloading processed video...")
                        final_output_path = enhance_node.download_processed_video(download_url, output_path)

                        status_info = f"Video restoration completed successfully. Processing time: {time.time() - start_time:.1f}s"
                        return (final_output_path, request_id, status_info)
                    else:
                        raise Exception("No download URL provided")

                elif status == 'failed':
                    error_msg = status_result.get('error', 'Unknown error')
                    raise Exception(f"Video processing failed: {error_msg}")

                elif status in ['queued', 'processing']:
                    time.sleep(60)  # Wait 1 minute before next check for restoration

                else:
                    print(f"Unknown status: {status}, continuing to wait...")
                    time.sleep(60)

            raise Exception("Video processing timed out")

        except Exception as e:
            error_msg = f"Error restoring video: {str(e)}"
            print(error_msg)
            return ("", request_id if 'request_id' in locals() else "", error_msg)


# Node mappings for ComfyUI
VIDEO_NODE_CLASS_MAPPINGS = {
    "TopazVideoEnhanceNode": TopazVideoEnhanceNode,
    "TopazVideoInterpolateNode": TopazVideoInterpolateNode,
    "TopazVideoRestoreNode": TopazVideoRestoreNode,
}

VIDEO_NODE_DISPLAY_NAME_MAPPINGS = {
    "TopazVideoEnhanceNode": "Topaz Video Enhance",
    "TopazVideoInterpolateNode": "Topaz Video Interpolate",
    "TopazVideoRestoreNode": "Topaz Video Restore",
}

