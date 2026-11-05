# Topaz Labs Video Nodes for ComfyUI

## 🎬 Updated Video Workflow Integration

The Topaz Labs video nodes have been **completely redesigned** to work seamlessly with ComfyUI's standard video workflow using **Load Video** and **Save Video** nodes.

## ✨ Key Features

### 🔄 ComfyUI Native Workflow
- **Input**: Accepts `IMAGE` batches from ComfyUI's Load Video nodes
- **Output**: Returns `IMAGE` batches compatible with Save Video nodes
- **No file paths**: Works entirely through node connections

### 🎯 Available Video Nodes

1. **Topaz Video Enhance** - General video enhancement and upscaling
2. **Topaz Video Interpolate** - Frame interpolation for smooth slow motion
3. **Topaz Video Restore** - Restoration of old or damaged videos

## 🚀 How It Works

### Traditional Workflow (OLD)
```
Video File Path → Topaz Node → Output Video Path
```

### New ComfyUI Workflow (NEW)
```
Load Video → IMAGE Batch → Topaz Video Node → Enhanced IMAGE Batch → Save Video
```

## 📋 Requirements

### Dependencies
```bash
pip install opencv-python
```

### ComfyUI Extensions
- **ComfyUI-VideoHelperSuite** (for Load Video and Save Video nodes)

## 🎯 Example Workflow

### Basic Video Enhancement
1. **Load Video** (VHS_LoadVideo)
   - Load your input video file
   - Outputs IMAGE batch of video frames

2. **Topaz Video Enhance**
   - Input: IMAGE batch from Load Video
   - Configure: API key, model, frame rate
   - Output: Enhanced IMAGE batch

3. **Save Video** (VHS_VideoCombine)
   - Input: Enhanced IMAGE batch
   - Output: Final enhanced video file

### Workflow JSON
See `../example_video_workflow.json` for a complete workflow example.

## ⚙️ Technical Details

### Internal Processing
1. **Frame Conversion**: ComfyUI IMAGE batch → Temporary video file
2. **API Processing**: Temporary video → Topaz Labs API → Enhanced video
3. **Frame Recovery**: Enhanced video → ComfyUI IMAGE batch
4. **Cleanup**: Automatic removal of temporary files

### Data Flow
```
ComfyUI Images → OpenCV Video → Topaz API → Enhanced Video → ComfyUI Images
```

## 🎛️ Node Parameters

### Topaz Video Enhance
- **images**: IMAGE batch input (from Load Video)
- **api_key**: Your Topaz Labs API key
- **model**: Enhancement model selection
- **frame_rate**: Frame rate for temporary video processing
- **output_width/height**: Optional resolution override
- **video_encoder**: H264, H265, etc.
- **compression_level**: Quality settings

## 🔧 Configuration

### API Key Setup
1. Get your API key from [Topaz Labs](https://www.topazlabs.com/)
2. Enter it in the `api_key` field of any Topaz node
3. The key will be validated before processing

### Model Selection
- **Proteus General**: Best for general enhancement
- **Artemis General**: Optimized for specific content types
- **Apollo General**: For frame interpolation
- **Chronos General**: For restoration tasks

## 🎨 Advantages of New Design

### ✅ Benefits
- **Native ComfyUI Integration**: Works with standard video nodes
- **Visual Workflow**: See the entire process in the node graph
- **Flexible Connections**: Easy to add pre/post-processing
- **Batch Processing**: Handles any number of frames
- **Memory Efficient**: Streams frames through temporary files

### 🔄 Compatibility
- **Load Video Sources**: Any ComfyUI video loader
- **Save Video Formats**: Any ComfyUI video saver
- **Frame Processing**: Works with other image processing nodes
- **Workflow Sharing**: Easy to share and modify workflows

## 🚨 Important Notes

### Temporary Files
- Video nodes create temporary video files for API processing
- Files are automatically cleaned up after processing
- Ensure sufficient disk space for temporary video files

### Processing Time
- Video processing can take significant time depending on:
  - Video length and resolution
  - Selected model complexity
  - Topaz Labs API queue status

### Error Handling
- If API processing fails, original frames are returned
- Temporary files are cleaned up even on errors
- Detailed error messages in ComfyUI console

## 🎯 Migration from Old Nodes

### Old Workflow
```json
{
  "video_path": "/path/to/input.mp4",
  "output_path": "/path/to/output.mp4"
}
```

### New Workflow
```json
{
  "images": "Connected from Load Video",
  "enhanced_images": "Connected to Save Video"
}
```

## 🎉 Ready to Use!

The updated video nodes are now fully compatible with ComfyUI's video workflow. Simply:

1. Install dependencies: `pip install opencv-python`
2. Install ComfyUI-VideoHelperSuite
3. Restart ComfyUI
4. Use the example workflow as a starting point

**Happy video enhancing!** 🎬✨
