#!/usr/bin/env python3
# Test script to verify Python imports

import sys

def test_import(module_name):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {module_name}: Import successful")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}: Unexpected error - {e}")
        return False

def main():
    print("Testing Python Imports")
    print("====================")
    
    modules = [
        'yaml',
        'markdown',
        'frontmatter',
        'edge_tts',
        'moviepy.editor',
        'PIL',
        'imageio_ffmpeg',
        'googleapiclient',
        'flask',
        'pytest'
    ]
    
    results = [test_import(m) for m in modules]
    success = all(results)
    
    print("\nTest Result:", "✅ All imports successful" if success else "❌ Some imports failed")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
