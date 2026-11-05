# ComfyUI Topaz Labs Integration

> Built in mid-2025 for a batch image and video production pipeline, to call Topaz Labs' cloud API directly from ComfyUI. ComfyUI has since added official Topaz API nodes; this package remains a working, self-contained reference for sync/async jobs, uploads, polling and downloads. Extra guides are in `docs/`.

A comprehensive custom node package for ComfyUI that integrates Topaz Labs AI image and video enhancement APIs, providing professional-grade enhancement capabilities for both images and videos.

## Features

### Image Enhancement
- **Image Enhancement**: Upscale and enhance images using Topaz Labs' industry-leading AI models
- **Image Sharpening**: Remove blur and bring images into focus with various sharpening models
- **Image Denoising**: Remove sensor noise and grain from images
- **Multiple Models**: Support for various specialized models (Standard V2, Low Resolution V2, CGI, High Fidelity V2, Text Refine, etc.)
- **Async/Sync Processing**: Choose between asynchronous (recommended for large images) or synchronous processing
- **Face Enhancement**: Automatic face detection and enhancement with customizable creativity and strength
- **Flexible Output**: Support for JPEG, PNG, and TIFF output formats

### Video Enhancement
- **Video Upscaling**: Enhance video resolution while maintaining clarity and sharpness
- **Frame Interpolation**: Create smooth slow motion by generating new frames (up to 8x slowmo)
- **Video Denoising**: Remove noise and grain for cleaner video output
- **Video Restoration**: Restore old, damaged, or low-quality videos using advanced AI models
- **Framerate Conversion**: Convert between different framerates with intelligent interpolation
- **Multiple Video Models**: Support for specialized models (Proteus, Artemis, Apollo, Dione, etc.)
- **Professional Output**: Support for various codecs (H264, H265, ProRes) and containers (MP4, MOV, AVI)

## Installation

### Method 1: Manual Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Create a new directory for the Topaz Labs nodes:
   ```bash
   mkdir comfyui-topaz-labs
   cd comfyui-topaz-labs
   ```

3. Copy all the files from this package into the directory

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Git Clone (if available)

```bash
cd ComfyUI/custom_nodes/
git clone <repository-url> comfyui-topaz-labs
cd comfyui-topaz-labs
pip install -r requirements.txt
```

## Setup

1. **Get your Topaz Labs API Key**:
   - Visit [https://www.topazlabs.com/api](https://www.topazlabs.com/api)
   - Sign up for an account and obtain your API key
   - Keep your API key secure and never share it publicly

2. **Restart ComfyUI** after installation

## Usage

After installation and restart, you'll find six new nodes in the "Topaz Labs" category:

### Image Processing Nodes

#### 1. Topaz Labs Image Enhancer
- **Purpose**: General image enhancement and upscaling
- **Models**: Standard V2, Low Resolution V2, CGI, High Fidelity V2, Text Refine
- **Key Features**:
  - Automatic upscaling with customizable output dimensions
  - Face enhancement with creativity and strength controls
  - Model-specific parameters (sharpen, denoise, fix_compression)
  - Crop to fill or letterbox options

#### 2. Topaz Labs Image Sharpener
- **Purpose**: Remove blur and sharpen images
- **Models**: Standard, Strong, Lens Blur, Lens Blur V2, Motion Blur, Natural, Refocus
- **Key Features**:
  - Strength control for sharpening intensity
  - Minor denoise option for compatible models
  - Specialized models for different types of blur

#### 3. Topaz Labs Image Denoiser
- **Purpose**: Remove noise and grain from images
- **Models**: Normal, Strong, Extreme
- **Key Features**:
  - Strength control for noise reduction
  - Minor deblur to counteract softness
  - Original detail recovery option

### Video Processing Nodes

#### 4. Topaz Labs Video Enhancer
- **Purpose**: General video enhancement and upscaling
- **Models**: Proteus, Artemis, Nyx, Rhea, Gaia
- **Key Features**:
  - Video upscaling with resolution control
  - Denoising and sharpening for videos
  - Support for various output formats and codecs
  - Specialized models for different content types (CG, animation, etc.)

#### 5. Topaz Labs Video Interpolator
- **Purpose**: Frame interpolation for slow motion and framerate conversion
- **Models**: Apollo, Chronos
- **Key Features**:
  - Up to 8x slow motion capability
  - Intelligent frame generation
  - Framerate conversion (24fps to 60fps, etc.)
  - Duplicate frame detection and handling

#### 6. Topaz Labs Video Restorer
- **Purpose**: Restore old, damaged, or low-quality videos
- **Models**: Dione, Theia, Iris, Themis
- **Key Features**:
  - Specialized restoration for vintage content
  - DV footage enhancement
  - Face-specific restoration
  - Motion deblur capabilities
  - Grain preservation options

## Node Parameters

### Common Parameters
- **API Key**: Your Topaz Labs API key (required)
- **Output Format**: Choose between JPEG, PNG, or TIFF
- **Use Async**: Enable for better performance with large images (recommended)

### Enhancement Node Specific
- **Model**: Choose the appropriate AI model for your image type
- **Output Height/Width**: Set custom output dimensions (0 = auto-scale)
- **Face Enhancement**: Enable/disable automatic face enhancement
- **Face Enhancement Creativity**: Control creative liberties (0-1)
- **Face Enhancement Strength**: Control sharpness relative to background (0-1)
- **Crop to Fill**: Choose between cropping or letterboxing for aspect ratio changes

### Model-Specific Parameters
- **Sharpen**: Enhance image sharpness (0-1)
- **Denoise**: Reduce noise in the image (0-1)
- **Fix Compression**: Reduce compression artifacts (0-1)
- **Strength**: Control processing intensity (0.01-1)
- **Minor Denoise/Deblur**: Fine-tune secondary effects

## Tips and Best Practices

1. **API Key Security**: Store your API key securely and never commit it to version control
2. **Async Processing**: Use async mode for large images or batch processing
3. **Model Selection**: 
   - Use "Standard V2" for general-purpose enhancement
   - Use "Low Resolution V2" for web graphics and screenshots
   - Use "CGI" for computer-generated images
   - Use "High Fidelity V2" for professional photography
   - Use "Text Refine" for images with text and shapes
4. **Face Enhancement**: Start with low creativity values and adjust as needed
5. **Output Dimensions**: Leave at 0 for automatic scaling, or set specific values for exact sizing

## Troubleshooting

### Common Issues

1. **"API key is required" error**:
   - Ensure you've entered your valid Topaz Labs API key
   - Check that the API key doesn't have extra spaces

2. **"API request failed" error**:
   - Check your internet connection
   - Verify your API key is valid and has sufficient credits
   - Ensure the image format is supported (JPEG, PNG, TIFF)

3. **"Job timed out" error**:
   - Large images may take longer to process
   - Try using a smaller image or different model
   - Check Topaz Labs service status

4. **Node not appearing**:
   - Ensure all files are in the correct directory
   - Restart ComfyUI completely
   - Check the console for any import errors

### Getting Help

- Check the Topaz Labs API documentation: [https://developer.topazlabs.com/](https://developer.topazlabs.com/)
- Verify your API credits and usage at the Topaz Labs dashboard
- Ensure your API key has the necessary permissions

## API Credits and Pricing

This integration uses the Topaz Labs API, which requires credits for processing. Check the current pricing at [https://developer.topazlabs.com/whats-the-pricing](https://developer.topazlabs.com/whats-the-pricing).

## License

This custom node package is provided as-is. Please refer to Topaz Labs' terms of service for API usage guidelines.

## Contributing

Feel free to submit issues, feature requests, or improvements to this integration.
