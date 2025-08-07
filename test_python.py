#!/usr/bin/env python3
"""
Simple Python test script
"""

import sys
import os

def main():
    print("🐍 Python Test Script")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    # Check if we can import required modules
    try:
        import requests
        print("✅ requests module available")
    except ImportError:
        print("❌ requests module not available")
        print("Install with: pip install requests")
    
    try:
        import json
        print("✅ json module available")
    except ImportError:
        print("❌ json module not available")
    
    print("\n✅ Python is working correctly!")

if __name__ == "__main__":
    main()
