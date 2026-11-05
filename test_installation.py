#!/usr/bin/env python3
"""
Test script for ComfyUI Topaz Labs Integration
This script tests the installation and basic functionality without making API calls
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        # Test basic imports
        import torch
        print("✓ PyTorch imported successfully")

        import numpy as np
        print("✓ NumPy imported successfully")

        from PIL import Image
        print("✓ Pillow imported successfully")

        import requests
        print("✓ Requests imported successfully")

        # Add current directory to path for testing
        import sys
        from pathlib import Path
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        # Test our modules (import as standalone modules for testing)
        import config
        print("✓ Configuration imported successfully")

        import utils
        print("✓ Utility functions imported successfully")

        # For topaz_nodes, we need to temporarily modify imports
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        traceback.print_exc()
        return False

def test_node_classes():
    """Test that node classes can be instantiated"""
    print("\nTesting node classes...")

    try:
        # Test image nodes
        from topaz_image_nodes import TopazEnhanceNode, TopazSharpenNode, TopazDenoiseNode

        enhance_node = TopazEnhanceNode()
        print("✓ TopazEnhanceNode instantiated successfully")

        sharpen_node = TopazSharpenNode()
        print("✓ TopazSharpenNode instantiated successfully")

        denoise_node = TopazDenoiseNode()
        print("✓ TopazDenoiseNode instantiated successfully")

        # Test video nodes
        from topaz_video_nodes import TopazVideoEnhanceNode, TopazVideoInterpolateNode, TopazVideoRestoreNode

        video_enhance_node = TopazVideoEnhanceNode()
        print("✓ TopazVideoEnhanceNode instantiated successfully")

        video_interpolate_node = TopazVideoInterpolateNode()
        print("✓ TopazVideoInterpolateNode instantiated successfully")

        video_restore_node = TopazVideoRestoreNode()
        print("✓ TopazVideoRestoreNode instantiated successfully")

        # Test INPUT_TYPES method
        enhance_inputs = TopazEnhanceNode.INPUT_TYPES()
        assert 'required' in enhance_inputs
        assert 'optional' in enhance_inputs
        print("✓ Image INPUT_TYPES method works correctly")

        video_enhance_inputs = TopazVideoEnhanceNode.INPUT_TYPES()
        assert 'required' in video_enhance_inputs
        assert 'optional' in video_enhance_inputs
        print("✓ Video INPUT_TYPES method works correctly")

        return True

    except Exception as e:
        print(f"✗ Error testing node classes: {e}")
        traceback.print_exc()
        return False

def test_utility_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        import torch
        import numpy as np
        from PIL import Image
        from utils import tensor_to_pil, pil_to_tensor, validate_api_key, get_image_info
        
        # Create a test tensor (simulating ComfyUI image format)
        test_tensor = torch.rand(1, 64, 64, 3)  # Small test image
        
        # Test tensor to PIL conversion
        pil_image = tensor_to_pil(test_tensor)
        assert isinstance(pil_image, Image.Image)
        assert pil_image.size == (64, 64)
        print("✓ tensor_to_pil works correctly")
        
        # Test PIL to tensor conversion
        result_tensor = pil_to_tensor(pil_image)
        assert isinstance(result_tensor, torch.Tensor)
        assert result_tensor.shape == (1, 64, 64, 3)
        print("✓ pil_to_tensor works correctly")
        
        # Test image info
        info = get_image_info(pil_image)
        assert 'width' in info
        assert 'height' in info
        assert info['width'] == 64
        assert info['height'] == 64
        print("✓ get_image_info works correctly")
        
        # Test API key validation
        assert validate_api_key("valid_looking_api_key_12345") == True
        assert validate_api_key("") == False
        assert validate_api_key("key") == False
        print("✓ validate_api_key works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing utility functions: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration values"""
    print("\nTesting configuration...")
    
    try:
        from config import (
            TOPAZ_API_BASE_URL, TOPAZ_VIDEO_API_BASE_URL, ENHANCE_MODELS, SHARPEN_MODELS, DENOISE_MODELS,
            VIDEO_ENHANCEMENT_MODELS, ADVANCED_VIDEO_MODELS, DEFAULT_TIMEOUT, MAX_FILE_SIZE
        )

        # Test API URLs
        assert TOPAZ_API_BASE_URL.startswith("https://")
        print("✓ Image API base URL is valid")

        assert TOPAZ_VIDEO_API_BASE_URL.startswith("https://")
        print("✓ Video API base URL is valid")

        # Test image model configurations
        assert len(ENHANCE_MODELS) > 0
        assert "Standard V2" in ENHANCE_MODELS
        print("✓ Image enhance models configured correctly")

        assert len(SHARPEN_MODELS) > 0
        assert "Standard" in SHARPEN_MODELS
        print("✓ Sharpen models configured correctly")

        assert len(DENOISE_MODELS) > 0
        assert "Normal" in DENOISE_MODELS
        print("✓ Denoise models configured correctly")

        # Test video model configurations
        assert len(VIDEO_ENHANCEMENT_MODELS) > 0
        assert "prob-4" in VIDEO_ENHANCEMENT_MODELS
        print("✓ Video enhancement models configured correctly")

        assert len(ADVANCED_VIDEO_MODELS) > 0
        assert "dtd-4" in ADVANCED_VIDEO_MODELS
        print("✓ Advanced video models configured correctly")

        # Test numeric values
        assert DEFAULT_TIMEOUT > 0
        assert MAX_FILE_SIZE > 0
        print("✓ Timeout and file size limits configured correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing configuration: {e}")
        traceback.print_exc()
        return False

def test_comfyui_integration():
    """Test ComfyUI integration"""
    print("\nTesting ComfyUI integration...")

    try:
        # Test individual node mappings
        from topaz_image_nodes import NODE_CLASS_MAPPINGS as IMAGE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY_MAPPINGS
        from topaz_video_nodes import VIDEO_NODE_CLASS_MAPPINGS, VIDEO_NODE_DISPLAY_NAME_MAPPINGS

        # Combine mappings for testing
        NODE_CLASS_MAPPINGS = {**IMAGE_MAPPINGS, **VIDEO_NODE_CLASS_MAPPINGS}
        NODE_DISPLAY_NAME_MAPPINGS = {**IMAGE_DISPLAY_MAPPINGS, **VIDEO_NODE_DISPLAY_NAME_MAPPINGS}

        # Test node mappings
        assert len(NODE_CLASS_MAPPINGS) > 0
        assert len(NODE_DISPLAY_NAME_MAPPINGS) > 0
        print("✓ Combined node mappings are properly defined")

        # Test that all mapped nodes have display names
        for node_key in NODE_CLASS_MAPPINGS.keys():
            assert node_key in NODE_DISPLAY_NAME_MAPPINGS
        print("✓ All nodes have display names")

        # Test node categories
        for node_class in NODE_CLASS_MAPPINGS.values():
            if hasattr(node_class, 'CATEGORY'):
                assert "Topaz Labs" in node_class.CATEGORY
        print("✓ Node categories are correct")

        # Test that we have both image and video nodes
        node_names = list(NODE_CLASS_MAPPINGS.keys())
        has_image_nodes = any("Enhance" in name or "Sharpen" in name or "Denoise" in name for name in node_names)
        has_video_nodes = any("Video" in name for name in node_names)

        assert has_image_nodes, "Should have image processing nodes"
        assert has_video_nodes, "Should have video processing nodes"
        print("✓ Both image and video nodes are available")

        return True

    except Exception as e:
        print(f"✗ Error testing ComfyUI integration: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("ComfyUI Topaz Labs Integration - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_node_classes,
        test_utility_functions,
        test_configuration,
        test_comfyui_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed! Installation appears to be working correctly.")
        print("\nNext steps:")
        print("1. Restart ComfyUI")
        print("2. Get your Topaz Labs API key")
        print("3. Try the example workflow")
        return True
    else:
        print("✗ Some tests failed. Please check the installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
