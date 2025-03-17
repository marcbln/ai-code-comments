#!/usr/bin/env python3
"""
Test script for profile functionality.
This script demonstrates how to use the profile loader and CLI options.
"""

import sys
from pathlib import Path
from aicoder.profiles import profile_loader
from aicoder.config import Config

def main():
    print("Testing Profile Functionality")
    print("-" * 50)
    
    # List available profiles
    print("Available profiles:")
    for profile_name in profile_loader.get_available_profiles():
        profile = profile_loader.get_profile(profile_name)
        print(f"  - {profile_name}: model={profile['model']}, strategy={profile['strategy']}")
    
    print("\nDefault profile:", Config.DEFAULT_PROFILE)
    
    # Test profile loading
    default_profile = profile_loader.get_profile(Config.DEFAULT_PROFILE)
    if default_profile:
        print(f"Default profile settings: {default_profile}")
    else:
        print("Default profile not found!")
    
    print("\nTest complete. Run the CLI with --help to see profile options:")
    print("  python -m aicoder.cli.main --help")
    print("  python -m aicoder.cli.main list-profiles")

if __name__ == "__main__":
    main()