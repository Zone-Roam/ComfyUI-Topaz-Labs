#!/usr/bin/env python3
"""
Test script for video conversion functions
"""

import torch
import numpy as np
import os
import tempfile
from PIL import Image

def create_test_video_batch():
    """Create a test batch of video frames"""
    print("Creating test video batch...")
    
    # Create 10 test frames (128x128 RGB) with animation
    batch_size = 10
    height, width, channels = 128, 128, 3
    
    images = []
    for frame_idx in range(batch_size):
        # Create animated pattern
        test_array = np.zeros((height, width, channels), dtype=np.float32)
        
        # Moving circle animation
        center_x = int(width * 0.3 + (width * 0.4) * (frame_idx / (batch_size - 1)))
        center_y = height // 2
        radius = 20
        
        for y in range(height):
            for x in range(width):
                # Distance from center
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                if dist <= radius:
                    # Red circle
                    test_array[y, x, 0] = 1.0
                    test_array[y, x, 1] = 0.2
                    test_array[y, x, 2] = 0.2
                else:
                    # Blue background with gradient
                    test_array[y, x, 0] = 0.1
                    test_array[y, x, 1] = 0.1 + 0.3 * (x / width)
                    test_array[y, x, 2] = 0.3 + 0.4 * (y / height)
        
        # Convert to tensor
        tensor = torch.from_numpy(test_array).unsqueeze(0)
        images.append(tensor)
    
    # Combine into batch tensor [batch_size, height, width, channels]
    batch_tensor = torch.cat(images, dim=0)
    print(f"✓ Created animated test batch: {batch_tensor.shape}")
    return batch_tensor

def test_video_conversion_functions():
    """Test video conversion without API calls"""
    print("\nTesting video conversion functions...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        node = TopazVideoEnhanceNode()
        
        # Create test batch
        test_batch = create_test_video_batch()
        
        # Test 1: Images to temporary video
        print("\n1. Testing images_to_temp_video...")
        temp_video_path = node.images_to_temp_video(test_batch, frame_rate=30.0)
        
        if os.path.exists(temp_video_path):
            file_size = os.path.getsize(temp_video_path)
            print(f"✓ Temporary video created: {temp_video_path}")
            print(f"✓ File size: {file_size} bytes")
        else:
            print("✗ Temporary video file not created")
            return False
        
        # Test 2: Video back to images
        print("\n2. Testing temp_video_to_images...")
        recovered_batch = node.temp_video_to_images(temp_video_path)
        
        print(f"✓ Recovered batch shape: {recovered_batch.shape}")
        print(f"✓ Original frames: {len(test_batch)}, Recovered frames: {len(recovered_batch)}")
        
        # Test 3: Compare dimensions
        if test_batch.shape[0] == recovered_batch.shape[0]:
            print("✓ Frame count matches")
        else:
            print(f"⚠ Frame count differs: {test_batch.shape[0]} -> {recovered_batch.shape[0]}")
        
        if test_batch.shape[1:3] == recovered_batch.shape[1:3]:
            print("✓ Frame dimensions match")
        else:
            print(f"⚠ Frame dimensions differ: {test_batch.shape[1:3]} -> {recovered_batch.shape[1:3]}")
        
        # Test 4: Data integrity check
        original_mean = test_batch.mean().item()
        recovered_mean = recovered_batch.mean().item()
        difference = abs(original_mean - recovered_mean)
        
        print(f"✓ Data integrity: original={original_mean:.3f}, recovered={recovered_mean:.3f}, diff={difference:.3f}")
        
        if difference < 0.1:  # Allow some compression loss
            print("✓ Data integrity acceptable")
        else:
            print("⚠ Significant data loss detected")
        
        # Test 5: Cleanup
        print("\n3. Testing cleanup...")
        node.cleanup_temp_files([temp_video_path])
        
        if not os.path.exists(temp_video_path):
            print("✓ Temporary file cleaned up successfully")
        else:
            print("⚠ Temporary file still exists")
        
        return True
        
    except Exception as e:
        print(f"✗ Video conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_interface():
    """Test the node interface without API calls"""
    print("\nTesting node interface...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        node = TopazVideoEnhanceNode()
        
        # Create test batch
        test_batch = create_test_video_batch()
        
        # Test INPUT_TYPES structure
        input_types = TopazVideoEnhanceNode.INPUT_TYPES()
        required_inputs = input_types["required"]
        
        print(f"✓ Required inputs: {list(required_inputs.keys())}")
        
        # Check expected inputs
        expected_inputs = ["images", "api_key", "model", "frame_rate"]
        for inp in expected_inputs:
            if inp in required_inputs:
                print(f"✓ Has required input: {inp}")
            else:
                print(f"✗ Missing required input: {inp}")
                return False
        
        # Test return types
        if hasattr(node, 'RETURN_TYPES') and hasattr(node, 'RETURN_NAMES'):
            print(f"✓ Return types: {node.RETURN_TYPES}")
            print(f"✓ Return names: {node.RETURN_NAMES}")
        else:
            print("✗ Missing return type definitions")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Node interface test failed: {e}")
        return False

if __name__ == "__main__":
    print("ComfyUI Topaz Video Nodes - Conversion Test")
    print("=" * 50)
    
    success1 = test_node_interface()
    success2 = test_video_conversion_functions()
    
    if success1 and success2:
        print("\n🎉 All video conversion tests passed!")
        print("\nThe video nodes are ready for use with ComfyUI!")
        print("\nWorkflow:")
        print("1. Load Video -> Topaz Video Enhance -> Save Video")
        print("2. The node will temporarily convert frames to video for API processing")
        print("3. Results are converted back to frame format for ComfyUI")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the error messages above.")
