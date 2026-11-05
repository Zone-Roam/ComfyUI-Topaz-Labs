# Complete Installation and Usage Guide

## 📦 What You're Installing

This package provides **6 powerful nodes** for ComfyUI that integrate with Topaz Labs' professional AI enhancement services:

### Image Processing (3 nodes)
- **Topaz Labs Image Enhancer** - General upscaling and enhancement
- **Topaz Labs Image Sharpener** - Remove blur and sharpen images  
- **Topaz Labs Image Denoiser** - Remove noise and grain

### Video Processing (3 nodes)
- **Topaz Labs Video Enhancer** - Video upscaling and enhancement
- **Topaz Labs Video Interpolator** - Frame interpolation and slow motion
- **Topaz Labs Video Restorer** - Restore old or damaged videos

## 🔧 Installation Steps

### Step 1: Prepare Your Environment

1. **Ensure ComfyUI is installed** and working
2. **Get your Topaz Labs API key**:
   - Visit [https://www.topazlabs.com/api](https://www.topazlabs.com/api)
   - Sign up and obtain your API key
   - You'll get 100 free credits to start

### Step 2: Install the Package

#### Option A: Automatic Installation (Recommended)
```bash
# Navigate to ComfyUI custom nodes directory
cd ComfyUI/custom_nodes/

# Create directory and copy files
mkdir comfyui-topaz-labs
cd comfyui-topaz-labs

# Copy all files from this package, then run:
python install.py
```

#### Option B: Manual Installation
```bash
# Navigate to ComfyUI custom nodes directory
cd ComfyUI/custom_nodes/

# Create directory
mkdir comfyui-topaz-labs
cd comfyui-topaz-labs

# Copy these files:
# - __init__.py
# - topaz_nodes.py
# - topaz_video_nodes.py
# - utils.py
# - config.py
# - requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
# Run the test script
python test_installation.py
```

You should see:
```
✓ All tests passed! Installation appears to be working correctly.
```

### Step 4: Restart ComfyUI
**Important**: Restart ComfyUI completely for the nodes to appear.

## 🎯 First Usage

### For Images
1. Add **"Topaz Labs Image Enhancer"** node
2. Connect an image input (Load Image node)
3. Enter your API key
4. Choose model (start with "Standard V2")
5. Run the workflow!

### For Videos
1. Add **"Topaz Labs Video Enhancer"** node
2. Enter the path to your video file
3. Enter your API key
4. Choose model (start with "prob-4 - Proteus General")
5. Set output path (optional)
6. Run the workflow!

## 📋 Node Reference

### Image Nodes

#### Topaz Labs Image Enhancer
- **Input**: IMAGE tensor from ComfyUI
- **Output**: Enhanced IMAGE tensor
- **Best for**: General image improvement
- **Processing**: Sync or Async

#### Topaz Labs Image Sharpener
- **Input**: IMAGE tensor from ComfyUI
- **Output**: Sharpened IMAGE tensor
- **Best for**: Blurry or out-of-focus images
- **Processing**: Sync or Async

#### Topaz Labs Image Denoiser
- **Input**: IMAGE tensor from ComfyUI
- **Output**: Denoised IMAGE tensor
- **Best for**: Noisy or grainy images
- **Processing**: Sync or Async

### Video Nodes

#### Topaz Labs Video Enhancer
- **Input**: Video file path (STRING)
- **Output**: Enhanced video file path (STRING)
- **Best for**: General video improvement and upscaling
- **Processing**: Async only (videos take time!)

#### Topaz Labs Video Interpolator
- **Input**: Video file path (STRING)
- **Output**: Interpolated video file path (STRING)
- **Best for**: Creating slow motion, framerate conversion
- **Processing**: Async only

#### Topaz Labs Video Restorer
- **Input**: Video file path (STRING)
- **Output**: Restored video file path (STRING)
- **Best for**: Old, damaged, or low-quality videos
- **Processing**: Async only

## ⚙️ Configuration Tips

### API Key Management
- **Option 1**: Enter directly in each node
- **Option 2**: Set environment variable `TOPAZ_API_KEY`
- **Security**: Never commit API keys to version control

### Performance Optimization
- **Use Async mode** for large images and all videos
- **Monitor API credits** at Topaz Labs dashboard
- **Choose appropriate models** for your content type

### Model Selection Guide

#### Image Models
- **Standard V2**: Best for most photos
- **Low Resolution V2**: Web graphics, screenshots
- **CGI**: Computer-generated images
- **High Fidelity V2**: Professional photography
- **Text Refine**: Images with text

#### Video Enhancement Models
- **Proteus (prob-4)**: Best for most videos
- **Artemis (ahq-12)**: High-quality denoise + sharpen
- **Nyx (nyx-3)**: Dedicated denoising
- **Rhea (rhea-1)**: Advanced 4x upscaling
- **Gaia (ghq-5)**: AI/CG/Animation content

#### Video Interpolation Models
- **Apollo (apo-8)**: Best overall, up to 8x slowmo
- **Chronos (chr-2)**: General framerate conversion

#### Video Restoration Models
- **Dione (dtd-4)**: Robust restoration for old content
- **Theia (thd-3)**: High fidelity and detail
- **Iris (iris-3)**: Face-specific enhancement
- **Themis (thm-2)**: Motion deblur

## 🚨 Troubleshooting

### Common Issues

#### "Node not appearing"
- Restart ComfyUI completely
- Check console for import errors
- Run `python test_installation.py`

#### "API key is required"
- Verify your API key is correct
- Check for extra spaces
- Try setting environment variable

#### "Video file not found"
- Use absolute file paths
- Check file permissions
- Ensure supported format (MP4, MOV, AVI)

#### "Processing failed"
- Check API credits remaining
- Verify internet connection
- Check Topaz Labs service status

#### "Import errors"
- Install dependencies: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify all files are copied correctly

### Getting Help

1. **Check the logs**: ComfyUI console shows detailed error messages
2. **Test installation**: Run `python test_installation.py`
3. **Verify API key**: Test at Topaz Labs dashboard
4. **Check file formats**: Ensure supported image/video formats

## 💰 Cost Management

### Understanding Credits
- **Image processing**: 1-10 credits per image (varies by size/model)
- **Video processing**: 10-100+ credits per minute (varies by model/resolution)
- **Free tier**: 100 credits to start
- **Monitoring**: Check usage at Topaz Labs dashboard

### Cost Optimization
- **Start small**: Test with short videos or small images
- **Choose efficient models**: Some models use fewer credits
- **Monitor usage**: Keep track of credit consumption
- **Plan ahead**: Purchase credits in advance for large projects

## 🎬 Example Workflows

### Basic Image Enhancement
```
Load Image → Topaz Image Enhancer → Save Image
```

### Video Upscaling
```
Video Path → Topaz Video Enhancer → Enhanced Video
```

### Slow Motion Creation
```
Video Path → Topaz Video Interpolator → Slow Motion Video
```

### Vintage Video Restoration
```
Old Video Path → Topaz Video Restorer → Restored Video
```

## 🔄 Updates and Maintenance

### Keeping Updated
- Check for new models in Topaz Labs documentation
- Update the package when new features are released
- Monitor ComfyUI compatibility

### Backup and Recovery
- **Backup your workflows** before major updates
- **Keep API key secure** and backed up
- **Document your settings** for reproducibility

---

**You're now ready to enhance images and videos with professional AI! 🚀**

For detailed documentation, see README.md
For quick start, see QUICKSTART.md
