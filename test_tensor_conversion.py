#!/usr/bin/env python3
"""
Test script for tensor conversion functions
"""

import torch
import numpy as np
from PIL import Image
from topaz_image_nodes import TopazEnhanceNode

def test_tensor_conversion():
    """Test tensor to PIL and PIL to tensor conversion"""
    print("Testing tensor conversion functions...")
    
    # Create a test node
    node = TopazEnhanceNode()
    
    # Test 1: Create a simple RGB image tensor (ComfyUI format: [1, H, W, C])
    print("\n1. Testing RGB image conversion...")
    height, width, channels = 64, 64, 3
    test_array = np.random.rand(height, width, channels).astype(np.float32)
    test_tensor = torch.from_numpy(test_array).unsqueeze(0)  # Add batch dimension
    
    print(f"   Original tensor shape: {test_tensor.shape}")
    print(f"   Original tensor dtype: {test_tensor.dtype}")
    print(f"   Original tensor range: [{test_tensor.min():.3f}, {test_tensor.max():.3f}]")
    
    # Convert to PIL
    try:
        pil_image = node.tensor_to_pil(test_tensor)
        print(f"   PIL image size: {pil_image.size}")
        print(f"   PIL image mode: {pil_image.mode}")
        
        # Convert back to tensor
        result_tensor = node.pil_to_tensor(pil_image)
        print(f"   Result tensor shape: {result_tensor.shape}")
        print(f"   Result tensor dtype: {result_tensor.dtype}")
        print(f"   Result tensor range: [{result_tensor.min():.3f}, {result_tensor.max():.3f}]")
        
        print("   ✓ RGB conversion successful!")
        
    except Exception as e:
        print(f"   ✗ RGB conversion failed: {e}")
        return False
    
    # Test 2: Test grayscale image
    print("\n2. Testing grayscale image conversion...")
    gray_array = np.random.rand(height, width, 1).astype(np.float32)
    gray_tensor = torch.from_numpy(gray_array).unsqueeze(0)
    
    try:
        pil_gray = node.tensor_to_pil(gray_tensor)
        print(f"   PIL grayscale size: {pil_gray.size}")
        print(f"   PIL grayscale mode: {pil_gray.mode}")
        
        result_gray = node.pil_to_tensor(pil_gray)
        print(f"   Result grayscale shape: {result_gray.shape}")
        print("   ✓ Grayscale conversion successful!")
        
    except Exception as e:
        print(f"   ✗ Grayscale conversion failed: {e}")
        return False
    
    # Test 3: Test with actual ComfyUI-like tensor (edge case)
    print("\n3. Testing edge case tensor shapes...")
    
    # Test very small tensor
    tiny_array = np.random.rand(1, 1, 3).astype(np.float32)
    tiny_tensor = torch.from_numpy(tiny_array).unsqueeze(0)
    
    try:
        pil_tiny = node.tensor_to_pil(tiny_tensor)
        print(f"   Tiny PIL size: {pil_tiny.size}")
        print("   ✓ Tiny tensor conversion successful!")
        
    except Exception as e:
        print(f"   ✗ Tiny tensor conversion failed: {e}")
        return False
    
    print("\n✅ All tensor conversion tests passed!")
    return True

if __name__ == "__main__":
    success = test_tensor_conversion()
    if success:
        print("\n🎉 Tensor conversion is working correctly!")
    else:
        print("\n❌ Tensor conversion has issues!")
