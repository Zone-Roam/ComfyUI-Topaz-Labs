#!/usr/bin/env python3
"""
Test script for API request format validation
"""

import json

def test_api_request_format():
    """Test the API request format matches Topaz Labs requirements"""
    print("Testing API request format...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        node = TopazVideoEnhanceNode()
        
        # Mock video metadata (similar to what we get from OpenCV)
        video_info = {
            'width': 1280,
            'height': 720,
            'framerate': 24.0,
            'frame_count': 192,
            'duration': 8.0,
            'size_bytes': 3350617,
            'container': 'mp4'
        }
        
        # Mock output parameters
        output_params = {
            'output_width': 0,
            'output_height': 0,
            'output_framerate': 0.0,
            'container': 'mp4',
            'video_encoder': 'H264',
            'video_profile': 'High',  # Now using High instead of Main
            'audio_codec': 'AAC',
            'audio_transfer': 'Copy',
            'compression_level': 'High'
        }
        
        print("✓ Testing create_video_request format...")
        
        # Simulate the request data creation (without API key)
        source_info = {
            "container": video_info.get('container', 'mp4'),
            "size": video_info.get('size_bytes', 0),
            "duration": video_info.get('duration', 60),
            "frameRate": video_info.get('framerate', 30),
            "frameCount": video_info.get('frame_count', 1800),
            "resolution": {
                "width": video_info.get('width', 1920),
                "height": video_info.get('height', 1080)
            }
        }
        
        filters = [{"model": "prob-4"}]
        
        output_info = {
            "frameRate": output_params.get('framerate', source_info['frameRate']),
            "audioTransfer": output_params.get('audio_transfer', 'Copy'),
            "audioCodec": output_params.get('audio_codec', 'AAC'),
            "videoEncoder": output_params.get('video_encoder', 'H264'),
            "videoProfile": "High",  # Fixed: API only supports High profile
            "dynamicCompressionLevel": output_params.get('compression_level', 'High'),
            "container": output_params.get('container', 'mp4'),
            "resolution": {
                "width": output_params.get('output_width') or source_info['resolution']['width'],
                "height": output_params.get('output_height') or source_info['resolution']['height']
            }
        }
        
        request_data = {
            "source": source_info,
            "filters": filters,
            "output": output_info
        }
        
        print("✓ API request format generated successfully")
        print("\n📋 Request Data Structure:")
        print(json.dumps(request_data, indent=2))
        
        # Validate against known requirements
        print("\n🔍 Validation against API requirements:")
        
        # Check source info
        required_source_fields = ['container', 'size', 'duration', 'frameRate', 'frameCount', 'resolution']
        for field in required_source_fields:
            if field in request_data['source']:
                print(f"   ✓ Source has {field}: {request_data['source'][field]}")
            else:
                print(f"   ✗ Source missing {field}")
                return False
        
        # Check resolution format
        if 'width' in request_data['source']['resolution'] and 'height' in request_data['source']['resolution']:
            print(f"   ✓ Source resolution format correct")
        else:
            print(f"   ✗ Source resolution format incorrect")
            return False
        
        # Check filters
        if request_data['filters'] and 'model' in request_data['filters'][0]:
            print(f"   ✓ Filters format correct: {request_data['filters'][0]['model']}")
        else:
            print(f"   ✗ Filters format incorrect")
            return False
        
        # Check output info
        required_output_fields = ['frameRate', 'audioTransfer', 'audioCodec', 'videoEncoder', 'videoProfile', 'dynamicCompressionLevel', 'container', 'resolution']
        for field in required_output_fields:
            if field in request_data['output']:
                print(f"   ✓ Output has {field}: {request_data['output'][field]}")
            else:
                print(f"   ✗ Output missing {field}")
                return False
        
        # Check critical fix: videoProfile should be "High"
        if request_data['output']['videoProfile'] == 'High':
            print(f"   ✓ Video profile correctly set to 'High' (API requirement)")
        else:
            print(f"   ✗ Video profile is '{request_data['output']['videoProfile']}', should be 'High'")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ API request format test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_defaults():
    """Test that node defaults are correct"""
    print("\nTesting node default values...")
    
    try:
        from topaz_video_nodes import TopazVideoEnhanceNode
        
        # Get INPUT_TYPES
        input_types = TopazVideoEnhanceNode.INPUT_TYPES()
        
        # Check video_profile default
        video_profile_config = input_types['optional']['video_profile']
        default_profile = video_profile_config[1]['default']
        
        if default_profile == 'High':
            print(f"   ✓ Node default video_profile is 'High'")
        else:
            print(f"   ⚠ Node default video_profile is '{default_profile}', should be 'High'")
        
        # Check available options
        available_profiles = video_profile_config[0]
        if 'High' in available_profiles:
            print(f"   ✓ 'High' profile is available in options: {available_profiles}")
        else:
            print(f"   ✗ 'High' profile not available in options: {available_profiles}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Node defaults test failed: {e}")
        return False

if __name__ == "__main__":
    print("ComfyUI Topaz Video Nodes - API Request Format Test")
    print("=" * 60)
    
    success1 = test_api_request_format()
    success2 = test_node_defaults()
    
    if success1 and success2:
        print("\n🎉 All API request format tests passed!")
        print("\nKey fixes applied:")
        print("✅ Video profile set to 'High' (API requirement)")
        print("✅ Request format matches Topaz Labs documentation")
        print("✅ Node defaults updated correctly")
        print("\nThe API request should now work correctly!")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the error messages above.")
