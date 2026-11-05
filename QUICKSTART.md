# Quick Start Guide - ComfyUI Topaz Labs Integration

## 🚀 Quick Installation

### Option 1: Automatic Installation
```bash
# Navigate to your ComfyUI directory
cd ComfyUI/custom_nodes/

# Create the directory and copy files
mkdir comfyui-topaz-labs
cd comfyui-topaz-labs

# Copy all files from this package to the directory
# Then run:
python install.py
```

### Option 2: Manual Installation
```bash
# Navigate to ComfyUI custom nodes directory
cd ComfyUI/custom_nodes/

# Create directory
mkdir comfyui-topaz-labs

# Copy these files to the directory:
# - __init__.py
# - topaz_nodes.py
# - utils.py
# - config.py
# - requirements.txt

# Install dependencies
pip install -r requirements.txt
```

## 🔑 Get Your API Key

1. Visit [https://www.topazlabs.com/api](https://www.topazlabs.com/api)
2. Sign up for an account
3. Get your API key
4. Keep it secure!

## 🎯 First Use

1. **Restart ComfyUI** after installation
2. Look for **"Topaz Labs"** category in the node menu
3. Add a **"Topaz Labs Image Enhancer"** node
4. Connect an image input
5. Enter your API key
6. Choose a model (start with "Standard V2")
7. Run the workflow!

## 📋 Available Nodes

### Image Processing Nodes

#### 🔧 Topaz Labs Image Enhancer
- **Purpose**: General upscaling and enhancement
- **Best for**: Most images, general improvement
- **Models**: Standard V2, Low Resolution V2, CGI, High Fidelity V2, Text Refine

#### ✨ Topaz Labs Image Sharpener
- **Purpose**: Remove blur and sharpen
- **Best for**: Blurry or out-of-focus images
- **Models**: Standard, Strong, Lens Blur, Motion Blur, Natural, Refocus

#### 🧹 Topaz Labs Image Denoiser
- **Purpose**: Remove noise and grain
- **Best for**: Low-light or noisy images
- **Models**: Normal, Strong, Extreme

### Video Processing Nodes

#### 🎬 Topaz Labs Video Enhancer
- **Purpose**: Video upscaling and enhancement
- **Best for**: General video improvement, upscaling
- **Models**: Proteus, Artemis, Nyx, Rhea, Gaia

#### 🎞️ Topaz Labs Video Interpolator
- **Purpose**: Frame interpolation and slow motion
- **Best for**: Creating smooth slow motion, framerate conversion
- **Models**: Apollo, Chronos

#### 🎭 Topaz Labs Video Restorer
- **Purpose**: Restore old or damaged videos
- **Best for**: Vintage footage, damaged videos, archival restoration
- **Models**: Dione, Theia, Iris, Themis

## ⚡ Quick Tips

- **Use Async mode** for better performance (default: ON)
- **Start with Standard V2** for general enhancement
- **Leave dimensions at 0** for automatic scaling
- **Enable face enhancement** for photos with people
- **Use PNG output** for best quality

## 🔧 Troubleshooting

### Node not appearing?
- Restart ComfyUI completely
- Check console for errors
- Run `python test_installation.py` to verify

### API errors?
- Check your API key is correct
- Verify you have API credits
- Check internet connection

### "Import error"?
- Install dependencies: `pip install -r requirements.txt`
- Check Python version compatibility

## 💡 Example Workflows

### Image Enhancement
```
Load Image → Topaz Image Enhancer → Save Image
     ↓
   (Your image gets enhanced with AI!)
```

### Video Enhancement
```
Video File Path → Topaz Video Enhancer → Enhanced Video File
     ↓
   (Your video gets upscaled and enhanced!)
```

### Slow Motion Creation
```
Video File Path → Topaz Video Interpolator → Slow Motion Video
     ↓
   (Creates smooth slow motion from normal speed video!)
```

### Video Restoration
```
Old Video Path → Topaz Video Restorer → Restored Video
     ↓
   (Restores and enhances vintage or damaged footage!)
```

## 📞 Need Help?

1. Check the full README.md for detailed documentation
2. Run the test script: `python test_installation.py`
3. Verify your API key at Topaz Labs dashboard
4. Check ComfyUI console for error messages

## 💰 Pricing

This integration uses Topaz Labs API which requires credits. Check current pricing at [https://developer.topazlabs.com/whats-the-pricing](https://developer.topazlabs.com/whats-the-pricing).

---

**Ready to enhance your images with professional AI? Let's go! 🚀**
