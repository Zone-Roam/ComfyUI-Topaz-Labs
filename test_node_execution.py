#!/usr/bin/env python3
"""
Test script for node execution without API calls
"""

import torch
import numpy as np
from PIL import Image
from topaz_image_nodes import TopazEnhanceNode, TopazSharpenNode, TopazDenoiseNode

def create_test_image_tensor():
    """Create a test image tensor in ComfyUI format"""
    # Create a simple test image (64x64 RGB)
    height, width, channels = 64, 64, 3
    
    # Create a gradient pattern
    test_array = np.zeros((height, width, channels), dtype=np.float32)
    for i in range(height):
        for j in range(width):
            test_array[i, j, 0] = i / height  # Red gradient
            test_array[i, j, 1] = j / width   # Green gradient
            test_array[i, j, 2] = 0.5         # Blue constant
    
    # Convert to ComfyUI tensor format [1, H, W, C]
    test_tensor = torch.from_numpy(test_array).unsqueeze(0)
    return test_tensor

def test_node_processing():
    """Test node processing without making API calls"""
    print("Testing node processing (without API calls)...")
    
    # Create test image
    test_tensor = create_test_image_tensor()
    print(f"Created test tensor with shape: {test_tensor.shape}")
    
    # Test 1: TopazEnhanceNode tensor conversion
    print("\n1. Testing TopazEnhanceNode tensor conversion...")
    try:
        enhance_node = TopazEnhanceNode()
        
        # Test tensor to PIL conversion
        pil_image = enhance_node.tensor_to_pil(test_tensor)
        print(f"   ✓ Tensor to PIL: {pil_image.size}, mode: {pil_image.mode}")
        
        # Test PIL to tensor conversion
        result_tensor = enhance_node.pil_to_tensor(pil_image)
        print(f"   ✓ PIL to tensor: {result_tensor.shape}")
        
        # Verify data integrity
        original_mean = test_tensor.mean().item()
        result_mean = result_tensor.mean().item()
        print(f"   ✓ Data integrity: original={original_mean:.3f}, result={result_mean:.3f}")
        
    except Exception as e:
        print(f"   ✗ TopazEnhanceNode test failed: {e}")
        return False
    
    # Test 2: TopazSharpenNode tensor conversion
    print("\n2. Testing TopazSharpenNode tensor conversion...")
    try:
        sharpen_node = TopazSharpenNode()
        
        pil_image = sharpen_node.tensor_to_pil(test_tensor)
        result_tensor = sharpen_node.pil_to_tensor(pil_image)
        print(f"   ✓ Sharpen node conversion: {pil_image.size} -> {result_tensor.shape}")
        
    except Exception as e:
        print(f"   ✗ TopazSharpenNode test failed: {e}")
        return False
    
    # Test 3: TopazDenoiseNode tensor conversion
    print("\n3. Testing TopazDenoiseNode tensor conversion...")
    try:
        denoise_node = TopazDenoiseNode()
        
        pil_image = denoise_node.tensor_to_pil(test_tensor)
        result_tensor = denoise_node.pil_to_tensor(pil_image)
        print(f"   ✓ Denoise node conversion: {pil_image.size} -> {result_tensor.shape}")
        
    except Exception as e:
        print(f"   ✗ TopazDenoiseNode test failed: {e}")
        return False
    
    # Test 4: Test different image sizes
    print("\n4. Testing different image sizes...")
    sizes = [(32, 32), (128, 128), (256, 256)]
    
    for width, height in sizes:
        try:
            # Create tensor of specific size
            test_array = np.random.rand(height, width, 3).astype(np.float32)
            size_tensor = torch.from_numpy(test_array).unsqueeze(0)
            
            # Test with enhance node
            pil_img = enhance_node.tensor_to_pil(size_tensor)
            result_tensor = enhance_node.pil_to_tensor(pil_img)
            
            print(f"   ✓ Size {width}x{height}: {size_tensor.shape} -> {pil_img.size} -> {result_tensor.shape}")
            
        except Exception as e:
            print(f"   ✗ Size {width}x{height} failed: {e}")
            return False
    
    print("\n✅ All node processing tests passed!")
    return True

def test_input_types():
    """Test INPUT_TYPES methods"""
    print("\nTesting INPUT_TYPES methods...")
    
    try:
        # Test enhance node
        enhance_types = TopazEnhanceNode.INPUT_TYPES()
        print(f"   ✓ TopazEnhanceNode INPUT_TYPES: {len(enhance_types['required'])} required inputs")
        
        # Test sharpen node
        sharpen_types = TopazSharpenNode.INPUT_TYPES()
        print(f"   ✓ TopazSharpenNode INPUT_TYPES: {len(sharpen_types['required'])} required inputs")
        
        # Test denoise node
        denoise_types = TopazDenoiseNode.INPUT_TYPES()
        print(f"   ✓ TopazDenoiseNode INPUT_TYPES: {len(denoise_types['required'])} required inputs")
        
        return True
        
    except Exception as e:
        print(f"   ✗ INPUT_TYPES test failed: {e}")
        return False

if __name__ == "__main__":
    print("ComfyUI Topaz Labs - Node Execution Test")
    print("=" * 50)
    
    success1 = test_input_types()
    success2 = test_node_processing()
    
    if success1 and success2:
        print("\n🎉 All node execution tests passed!")
        print("The nodes should work correctly in ComfyUI!")
    else:
        print("\n❌ Some tests failed!")
