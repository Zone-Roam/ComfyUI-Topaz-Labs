#!/usr/bin/env python3
"""
Test script for Topaz Labs Video API
Tests the corrected API endpoints and workflow
"""

import os
import requests
import json
from config import TOPAZ_VIDEO_API_BASE_URL

def test_create_request(api_key):
    """Test creating a video request"""

    # Test video metadata (small sample)
    test_video_info = {
        "container": "mp4",
        "size": 1000000,  # 1MB
        "duration": 5.0,
        "frameRate": 24.0,
        "frameCount": 120,
        "resolution": {
            "width": 640,
            "height": 480
        }
    }

    # Test request payload
    request_data = {
        "source": test_video_info,
        "filters": [{
            "model": "prob-4"
        }],
        "output": {
            "frameRate": 24.0,
            "audioTransfer": "Copy",
            "audioCodec": "AAC",
            "videoEncoder": "H264",
            "videoProfile": "High",  # Fixed: Use High instead of Main
            "dynamicCompressionLevel": "High",
            "container": "mp4",
            "resolution": {
                "width": 640,
                "height": 480
            }
        }
    }

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"🧪 Testing Step 1: Create Request")
    print(f"Endpoint: {TOPAZ_VIDEO_API_BASE_URL}/")

    try:
        response = requests.post(
            f"{TOPAZ_VIDEO_API_BASE_URL}/",
            headers=headers,
            json=request_data,
            timeout=30
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Step 1 successful!")
            print(f"Request ID: {result.get('requestId')}")
            print(f"Cost estimate: {result.get('estimates', {}).get('cost', 'Unknown')} credits")
            print(f"Time estimate: {result.get('estimates', {}).get('time', 'Unknown')} seconds")
            return result.get('requestId')
        else:
            print(f"❌ Step 1 failed!")
            print(f"Response text: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Step 1 request failed: {str(e)}")
        return None

def test_accept_request(api_key, request_id):
    """Test accepting a video request"""

    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json"
    }

    print(f"\n🧪 Testing Step 2: Accept Request")
    print(f"Endpoint: {TOPAZ_VIDEO_API_BASE_URL}/{request_id}/accept")

    try:
        response = requests.patch(
            f"{TOPAZ_VIDEO_API_BASE_URL}/{request_id}/accept",
            headers=headers,
            timeout=30
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Step 2 successful!")
            print(f"Response keys: {list(result.keys())}")
            print(f"Full response: {json.dumps(result, indent=2)}")

            # Check for upload URLs (API docs show field name is 'urls')
            upload_urls = (result.get('urls') or
                          result.get('uploadUrls') or
                          result.get('uploadUrl') or
                          result.get('upload_urls') or
                          result.get('upload_url'))

            if upload_urls:
                if isinstance(upload_urls, str):
                    upload_urls = [upload_urls]
                print(f"Found {len(upload_urls)} upload URL(s)")
                return upload_urls
            else:
                print("⚠️ No upload URLs found in response")
                return None
        else:
            print(f"❌ Step 2 failed!")
            print(f"Response text: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Step 2 request failed: {str(e)}")
        return None

def main():
    """Main test function"""

    # Get API key from environment or user input
    api_key = os.getenv('TOPAZ_API_KEY')
    if not api_key:
        api_key = input("Enter your Topaz Labs API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return

    print("🧪 Testing Topaz Labs Video API Workflow...")
    print(f"API Base URL: {TOPAZ_VIDEO_API_BASE_URL}")
    print("=" * 60)

    # Test Step 1: Create Request
    request_id = test_create_request(api_key)

    if not request_id:
        print("\n❌ Step 1 failed. Cannot proceed with further tests.")
        return

    # Test Step 2: Accept Request
    upload_urls = test_accept_request(api_key, request_id)

    if upload_urls:
        print(f"\n✅ API workflow test successful!")
        print(f"✅ Step 1: Request created successfully")
        print(f"✅ Step 2: Request accepted, got {len(upload_urls)} upload URL(s)")
        print(f"\n📝 Next steps would be:")
        print(f"   3. Upload video file to: {upload_urls[0][:50]}...")
        print(f"   4. Complete upload with ETag")
        print(f"   5. Monitor processing status")
        print(f"   6. Download result")
    else:
        print(f"\n⚠️ Partial success:")
        print(f"✅ Step 1: Request created successfully")
        print(f"❌ Step 2: No upload URLs received")
        print(f"\n🔍 This suggests the API response format may be different than expected.")
        print(f"   Check the response format in the logs above.")

if __name__ == "__main__":
    main()
