#!/usr/bin/env python3
"""
Test script for video nodes
"""

import torch
import numpy as np
from PIL import Image

def test_video_node_import():
    """Test importing video nodes"""
    print("Testing video node imports...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        print("✓ TopazVideoEnhanceNode imported successfully")
        
        # Test node instantiation
        node = TopazVideoEnhanceNode()
        print("✓ TopazVideoEnhanceNode instantiated successfully")
        
        # Test INPUT_TYPES
        input_types = TopazVideoEnhanceNode.INPUT_TYPES()
        print(f"✓ INPUT_TYPES: {len(input_types['required'])} required inputs")
        
        # Check if it expects IMAGE input
        if "images" in input_types["required"]:
            print("✓ Node accepts IMAGE input (compatible with Load Video)")
        else:
            print("✗ Node does not accept IMAGE input")
            return False
        
        # Check return types
        if hasattr(TopazVideoEnhanceNode, 'RETURN_TYPES'):
            return_types = TopazVideoEnhanceNode.RETURN_TYPES
            if "IMAGE" in return_types:
                print("✓ Node returns IMAGE output (compatible with Save Video)")
            else:
                print("✗ Node does not return IMAGE output")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def create_test_image_batch():
    """Create a test batch of images"""
    # Create 5 test frames (64x64 RGB)
    batch_size = 5
    height, width, channels = 64, 64, 3
    
    images = []
    for i in range(batch_size):
        # Create a simple gradient pattern that changes per frame
        test_array = np.zeros((height, width, channels), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                test_array[y, x, 0] = (y / height) * (i + 1) / batch_size  # Red varies by frame
                test_array[y, x, 1] = x / width  # Green gradient
                test_array[y, x, 2] = 0.5  # Blue constant
        
        # Convert to tensor and add to batch
        tensor = torch.from_numpy(test_array).unsqueeze(0)  # Add batch dim
        images.append(tensor)
    
    # Combine into batch tensor [batch_size, height, width, channels]
    batch_tensor = torch.cat(images, dim=0)
    print(f"Created test batch with shape: {batch_tensor.shape}")
    return batch_tensor

def test_tensor_conversion():
    """Test tensor conversion functions"""
    print("\nTesting tensor conversion functions...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        node = TopazVideoEnhanceNode()
        
        # Create test image
        test_array = np.random.rand(64, 64, 3).astype(np.float32)
        test_tensor = torch.from_numpy(test_array).unsqueeze(0)
        
        # Test tensor to PIL
        pil_image = node.tensor_to_pil(test_tensor)
        print(f"✓ Tensor to PIL: {test_tensor.shape} -> {pil_image.size}, mode: {pil_image.mode}")
        
        # Test PIL to tensor
        result_tensor = node.pil_to_tensor(pil_image)
        print(f"✓ PIL to tensor: {pil_image.size} -> {result_tensor.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Tensor conversion test failed: {e}")
        return False

if __name__ == "__main__":
    print("ComfyUI Topaz Video Nodes - Test")
    print("=" * 40)
    
    success1 = test_video_node_import()
    success2 = test_tensor_conversion()
    
    if success1 and success2:
        print("\n🎉 Basic video node tests passed!")
        print("\nNext steps:")
        print("1. Install opencv-python: pip install opencv-python")
        print("2. Test with actual video processing")
        print("3. Connect with Load Video and Save Video nodes in ComfyUI")
    else:
        print("\n❌ Some tests failed!")
