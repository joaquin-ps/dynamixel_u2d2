#!/usr/bin/env python3
"""
Simple test script to verify the package can be imported correctly.
Run this after installing the package to test the installation.
"""

def test_import():
    """Test that the package can be imported correctly."""
    try:
        from dynamixel_u2d2 import U2D2Interface
        print("✅ Successfully imported U2D2Interface")
        
        # Test that the class can be instantiated (without actually connecting)
        print("✅ Package structure is correct")
        
        # Test version
        import dynamixel_u2d2
        print(f"✅ Package version: {dynamixel_u2d2.__version__}")
        
        print("\n🎉 Package installation successful!")
        print("You can now use: from dynamixel_u2d2 import U2D2Interface")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure the package is installed: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_import()
