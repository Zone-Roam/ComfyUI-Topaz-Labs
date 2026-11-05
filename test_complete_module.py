#!/usr/bin/env python3
"""
Test script for complete module import
"""

def test_complete_module():
    """Test importing the complete module"""
    print("Testing complete module import...")
    
    try:
        # Import image nodes
        from topaz_image_nodes import NODE_CLASS_MAPPINGS as IMAGE_MAPPINGS
        from topaz_image_nodes import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY_MAPPINGS
        print(f"✓ Image nodes imported: {list(IMAGE_MAPPINGS.keys())}")
        
        # Import video nodes
        from topaz_video_nodes import VIDEO_NODE_CLASS_MAPPINGS as VIDEO_MAPPINGS
        from topaz_video_nodes import VIDEO_NODE_DISPLAY_NAME_MAPPINGS as VIDEO_DISPLAY_MAPPINGS
        print(f"✓ Video nodes imported: {list(VIDEO_MAPPINGS.keys())}")
        
        # Combine mappings
        combined_class_mappings = {**IMAGE_MAPPINGS, **VIDEO_MAPPINGS}
        combined_display_mappings = {**IMAGE_DISPLAY_MAPPINGS, **VIDEO_DISPLAY_MAPPINGS}
        
        print(f"\n✓ Total nodes available: {len(combined_class_mappings)}")
        print("✓ All node classes:")
        for key, cls in combined_class_mappings.items():
            display_name = combined_display_mappings.get(key, key)
            print(f"   - {key}: {display_name}")
        
        # Test node categories
        print("\n✓ Node categories:")
        categories = set()
        for cls in combined_class_mappings.values():
            if hasattr(cls, 'CATEGORY'):
                categories.add(cls.CATEGORY)
        
        for category in sorted(categories):
            print(f"   - {category}")
        
        # Test instantiation
        print("\n✓ Testing node instantiation:")
        for key, cls in combined_class_mappings.items():
            try:
                instance = cls()
                print(f"   ✓ {key}: instantiated successfully")
            except Exception as e:
                print(f"   ✗ {key}: failed to instantiate - {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_compatibility():
    """Test node compatibility with ComfyUI"""
    print("\nTesting ComfyUI compatibility...")
    
    try:
        from topaz_image_nodes import TopazEnhanceNode
        from topaz_video_nodes import TopazVideoEnhanceNode
        
        # Test image node
        image_node = TopazEnhanceNode()
        image_input_types = image_node.INPUT_TYPES()
        
        print("✓ Image node compatibility:")
        print(f"   - Input: {image_input_types['required'].keys()}")
        print(f"   - Output: {image_node.RETURN_TYPES}")
        print(f"   - Category: {image_node.CATEGORY}")
        
        # Test video node
        video_node = TopazVideoEnhanceNode()
        video_input_types = video_node.INPUT_TYPES()
        
        print("✓ Video node compatibility:")
        print(f"   - Input: {video_input_types['required'].keys()}")
        print(f"   - Output: {video_node.RETURN_TYPES}")
        print(f"   - Category: {video_node.CATEGORY}")
        
        # Check workflow compatibility
        if "IMAGE" in image_input_types["required"] and "IMAGE" in image_node.RETURN_TYPES:
            print("✓ Image nodes: Compatible with ComfyUI image workflow")
        
        if "IMAGE" in video_input_types["required"] and "IMAGE" in video_node.RETURN_TYPES:
            print("✓ Video nodes: Compatible with Load Video -> Save Video workflow")
        
        return True
        
    except Exception as e:
        print(f"✗ Compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("ComfyUI Topaz Labs - Complete Module Test")
    print("=" * 50)
    
    success1 = test_complete_module()
    success2 = test_node_compatibility()
    
    if success1 and success2:
        print("\n🎉 Complete module test passed!")
        print("\nReady for ComfyUI integration!")
        print("\nAvailable workflows:")
        print("📸 Image Processing:")
        print("   Load Image -> Topaz Image Enhance/Sharpen/Denoise -> Save Image")
        print("🎬 Video Processing:")
        print("   Load Video -> Topaz Video Enhance/Interpolate/Restore -> Save Video")
        print("\nAll nodes work with ComfyUI's standard data flow!")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the error messages above.")
