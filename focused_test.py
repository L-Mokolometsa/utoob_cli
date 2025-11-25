#!/usr/bin/env python3
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock
import io

# Add the project directory to Python path
sys.path.insert(0, '/home/letlhogonolo-mokolometsa/rootfolder/private_folder--admin_only/repos/utoob_cli/utoob')

def test_youtube_validation_issue():
    """Test the specific YouTube validation issue"""
    print("Testing YouTube validation issue...")
    
    from utoob import validate_youtube_url
    
    # Test cases that should be valid YouTube URLs
    valid_youtube_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Standard YouTube URL"),
        ("http://youtube.com/watch?v=dQw4w9WgXcQ", "Non-www YouTube URL"),
        ("https://youtu.be/dQw4w9WgXcQ", "Shortened YouTube URL"),
        ("https://www.youtu.be/dQw4w9WgXcQ", "Shortened with www"),
        ("https://music.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube Music URL"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "Embedded YouTube URL"),
        ("https://www.youtube.com/v/dQw4w9WgXcQ", "YouTube video URL"),
        ("https://www.youtube.com/attribution_link?a=xyz", "Attribution link")
    ]
    
    print("Testing YouTube URL validation:")
    for url, description in valid_youtube_cases:
        result = validate_youtube_url(url)
        print(f"  {description}: {url}")
        print(f"    Valid: {result}")
        if not result:
            print(f"    ❌ FAILED - This should be valid!")
        else:
            print(f"    ✅ PASSED")
        print()

def test_security_checks():
    """Test security validation specifically"""
    print("Testing security validation...")
    
    from utoob import validate_url, validate_youtube_url, sanitize_filename
    
    # Security test cases
    security_test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ;rm -rf /", "Command injection attempt", False, False),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ && echo test", "Command chaining attempt", False, False),
        ("javascript:alert('xss')", "JavaScript URL", False, False),
        ("file:///etc/passwd", "Local file access", False, False),
        ("ftp://example.com", "Wrong protocol", False, False),
        ("https://example.com", "Non-YouTube domain", True, False),
    ]
    
    print("Testing security validation:")
    for url, description, url_valid, youtube_valid in security_test_cases:
        url_result = validate_url(url)
        youtube_result = validate_youtube_url(url)
        
        print(f"  {description}: {url}")
        print(f"    URL Valid: {url_result} (expected: {url_valid})")
        print(f"    YouTube Valid: {youtube_result} (expected: {youtube_valid})")
        
        if url_result != url_valid:
            print(f"    ❌ URL validation failed - expected {url_valid}, got {url_result}")
        else:
            print(f"    ✅ URL validation passed")
            
        if youtube_result != youtube_valid:
            print(f"    ❌ YouTube validation failed - expected {youtube_valid}, got {youtube_result}")
        else:
            print(f"    ✅ YouTube validation passed")
        print()

def test_playlist_functionality():
    """Test playlist functionality"""
    print("Testing playlist functionality...")
    
    from utoob import is_playlist
    
    playlist_urls = [
        "https://www.youtube.com/playlist?list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy",
        "https://music.youtube.com/playlist?list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy",
        "https://www.youtube.com/watch?v=videoID&list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy",
        "https://youtube.com/playlist?list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy"
    ]
    
    non_playlist_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://example.com"
    ]
    
    print("Testing playlist detection:")
    for url in playlist_urls:
        result = is_playlist(url)
        print(f"  Playlist URL: {url}")
        print(f"    Detected as playlist: {result}")
        if not result:
            print(f"    ❌ FAILED - Should be detected as playlist!")
        else:
            print(f"    ✅ PASSED")
        print()
    
    for url in non_playlist_urls:
        result = is_playlist(url)
        print(f"  Non-playlist URL: {url}")
        print(f"    Detected as playlist: {result}")
        if result:
            print(f"    ❌ FAILED - Should not be detected as playlist!")
        else:
            print(f"    ✅ PASSED")
        print()

def main():
    print("Running focused tests on utoob application...")
    print("=" * 60)
    
    test_youtube_validation_issue()
    print()
    test_security_checks()
    print()
    test_playlist_functionality()
    print()
    
    print("=" * 60)
    print("Focused testing completed.")

if __name__ == "__main__":
    main()