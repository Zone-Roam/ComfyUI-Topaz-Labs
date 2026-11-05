#!/usr/bin/env python3
"""
Installation script for ComfyUI Topaz Labs Integration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_comfyui_path():
    """Try to find ComfyUI installation path"""
    possible_paths = [
        Path.cwd() / "ComfyUI",
        Path.home() / "ComfyUI", 
        Path("C:/ComfyUI") if os.name == 'nt' else Path("/opt/ComfyUI"),
        Path("./"),  # Current directory might be ComfyUI
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "main.py").exists():
            return path
    
    return None

def install_dependencies():
    """Install required Python packages"""
    requirements = [
        "requests>=2.25.0",
        "Pillow>=8.0.0", 
        "numpy>=1.19.0",
        "torch>=1.9.0"
    ]
    
    print("Installing dependencies...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✓ Installed {req}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {req}: {e}")
            return False
    
    return True

def copy_files(source_dir, target_dir):
    """Copy node files to ComfyUI custom_nodes directory"""
    files_to_copy = [
        "__init__.py",
        "topaz_nodes.py", 
        "utils.py",
        "config.py",
        "requirements.txt",
        "README.md"
    ]
    
    print(f"Copying files to {target_dir}...")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for filename in files_to_copy:
        source_file = source_dir / filename
        target_file = target_dir / filename
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"✓ Copied {filename}")
        else:
            print(f"✗ Source file not found: {filename}")
            return False
    
    return True

def main():
    print("ComfyUI Topaz Labs Integration - Installation Script")
    print("=" * 50)
    
    # Get current directory (where the script is located)
    current_dir = Path(__file__).parent.absolute()
    print(f"Source directory: {current_dir}")
    
    # Try to find ComfyUI installation
    comfyui_path = find_comfyui_path()
    
    if not comfyui_path:
        print("\n✗ Could not find ComfyUI installation.")
        print("Please ensure ComfyUI is installed and try one of these options:")
        print("1. Run this script from the ComfyUI directory")
        print("2. Set the COMFYUI_PATH environment variable")
        print("3. Manually copy files to ComfyUI/custom_nodes/comfyui-topaz-labs/")
        return False
    
    print(f"✓ Found ComfyUI at: {comfyui_path}")
    
    # Set target directory
    custom_nodes_dir = comfyui_path / "custom_nodes"
    target_dir = custom_nodes_dir / "comfyui-topaz-labs"
    
    print(f"Target directory: {target_dir}")
    
    # Check if already installed
    if target_dir.exists():
        response = input(f"\nDirectory {target_dir} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return False
        
        # Remove existing directory
        shutil.rmtree(target_dir)
        print("✓ Removed existing installation")
    
    # Copy files
    if not copy_files(current_dir, target_dir):
        print("\n✗ Failed to copy files")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Failed to install dependencies")
        return False
    
    print("\n" + "=" * 50)
    print("✓ Installation completed successfully!")
    print("\nNext steps:")
    print("1. Restart ComfyUI")
    print("2. Get your Topaz Labs API key from https://www.topazlabs.com/api")
    print("3. Look for 'Topaz Labs' nodes in the node menu")
    print("\nFor help and documentation, see the README.md file.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
