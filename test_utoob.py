#!/usr/bin/env python3
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock
import io

# Add the project directory to Python path
sys.path.insert(0, '/home/letlhogonolo-mokolometsa/rootfolder/private_folder--admin_only/repos/utoob_cli/utoob')

def test_url_validation():
    """Test URL validation functions"""
    print("Testing URL validation functions...")
    
    # Import the functions from the module
    from utoob import validate_url, validate_youtube_url, sanitize_filename
    
    # Test validate_url function
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtu.be/dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://localhost:8080",
        "https://192.168.1.1:8080"
    ]
    
    invalid_urls = [
        "ftp://youtube.com/watch?v=dQw4w9WgXcQ",  # Wrong protocol
        "https://example.com/;rm -rf /",  # Command injection attempt
        "javascript:alert('xss')",  # XSS attempt
        "",  # Empty string
        "not-a-url",  # Not a URL
        "https://",  # Incomplete URL
        "../path/traversal",  # Path traversal attempt
        "file:///etc/passwd"  # Local file access attempt
    ]
    
    print("  Testing valid URLs:")
    for url in valid_urls:
        result = validate_url(url)
        print(f"    {url} -> {result}")
        assert result == True, f"Valid URL {url} failed validation"
    
    print("  Testing invalid URLs:")
    for url in invalid_urls:
        result = validate_url(url)
        print(f"    {url} -> {result}")
        assert result == False, f"Invalid URL {url} passed validation"
    
    # Test validate_youtube_url function
    valid_youtube_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtu.be/dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/v/dQw4w9WgXcQ",
        "https://www.youtube.com/attribution_link?a=xyz",
        "https://www.youtube.com/playlist?list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy",
        "https://music.youtube.com/playlist?list=PLo2GGUbFsI6lm7V8hoqgNQuOdBJD-aPuy"
    ]
    
    invalid_youtube_urls = [
        "https://www.google.com",
        "https://soundcloud.com/track",
        "https://example.com/watch?v=dQw4w9WgXcQ",  # Non-youtube domain
        "https://www.youtube.com/",  # No video ID
        "https://www.youtube.com/watch?v=too_short",  # Video ID too short
        "https://www.youtube.com/watch?v=way_too_long_video_id_that_exceeds_11_chars",
        "javascript:alert('xss')",  # XSS attempt
        ""  # Empty string
    ]
    
    print("  Testing valid YouTube URLs:")
    for url in valid_youtube_urls:
        result = validate_youtube_url(url)
        print(f"    {url} -> {result}")
        assert result == True, f"Valid YouTube URL {url} failed validation"
    
    print("  Testing invalid YouTube URLs:")
    for url in invalid_youtube_urls:
        result = validate_youtube_url(url)
        print(f"    {url} -> {result}")
        assert result == False, f"Invalid YouTube URL {url} passed validation"
    
    # Test sanitize_filename function
    test_cases = [
        ("normal_filename.txt", "normal_filename.txt"),
        ("file<with>special:chars.txt", "file_with_special_chars.txt"),
        ("file\"with\"quotes.txt", "file_with_quotes.txt"),
        ("file/with/slashes.txt", "file_with_slashes.txt"),
        ("file\\with\\backslashes.txt", "file_with_backslashes.txt"),
        ("file|with|pipes.txt", "file_with_pipes.txt"),
        ("file?with?question.txt", "file_with_question.txt"),
        ("file*with*asterisk.txt", "file_with_asterisk.txt"),
        ("../path_traversal.txt", "_path_traversal.txt"),
        ("..\\windows_path_traversal.txt", "_windows_path_traversal.txt"),
        ("very_long_filename_" + "x" * 300 + ".txt", "very_long_filename_" + "x" * (255-20) + ".txt"),  # Should be truncated
    ]
    
    print("  Testing filename sanitization:")
    for input_name, expected in test_cases:
        result = sanitize_filename(input_name)
        print(f"    {input_name} -> {result}")
        # Check that result doesn't exceed 255 characters
        assert len(result) <= 255, f"Sanitized filename exceeds 255 chars: {len(result)}"
        # For most cases, we check that dangerous chars are replaced
        if input_name != expected:
            # Verify dangerous characters are replaced
            assert '<' not in result, f"Sanitized filename contains '<': {result}"
            assert '>' not in result, f"Sanitized filename contains '>': {result}"
            assert ':' not in result, f"Sanitized filename contains ':': {result}"
            assert '"' not in result, f"Sanitized filename contains '\"': {result}"
            assert '/' not in result, f"Sanitized filename contains '/': {result}"
            assert '\\' not in result, f"Sanitized filename contains '\\': {result}"
            assert '|' not in result, f"Sanitized filename contains '|': {result}"
            assert '?' not in result, f"Sanitized filename contains '?': {result}"
            assert '*' not in result, f"Sanitized filename contains '*': {result}"
            # Check for path traversal
            assert '../' not in result, f"Sanitized filename contains '../': {result}"
            assert '..\\' not in result, f"Sanitized filename contains '..\\': {result}"

    print("✓ All URL validation tests passed!")
    return True

def test_playlist_detection():
    """Test playlist detection function"""
    print("Testing playlist detection...")
    
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
    
    print("  Testing playlist URLs:")
    for url in playlist_urls:
        result = is_playlist(url)
        print(f"    {url} -> {result}")
        assert result == True, f"Playlist URL {url} not detected as playlist"
    
    print("  Testing non-playlist URLs:")
    for url in non_playlist_urls:
        result = is_playlist(url)
        print(f"    {url} -> {result}")
        assert result == False, f"Non-playlist URL {url} detected as playlist"
    
    print("✓ Playlist detection tests passed!")
    return True

def test_database_operations():
    """Test database operations"""
    print("Testing database operations...")
    
    from utoob import init_database, check_history, add_to_history, DB_FILE
    import sqlite3
    import os
    
    # Initialize database
    init_database()
    
    # Check that DB file exists
    assert os.path.exists(DB_FILE), f"Database file {DB_FILE} was not created"
    
    # Add an entry to history
    test_url = "https://www.youtube.com/watch?v=test123"
    test_title = "Test Video"
    test_path = "/path/to/test.mp4"
    
    # Check that it's not in history initially
    result = check_history(test_url)
    assert result is None, f"URL {test_url} already exists in history"
    
    # Add to history
    add_to_history(test_url, test_title, test_path)
    
    # Check that it's now in history
    result = check_history(test_url)
    assert result is not None, f"URL {test_url} was not added to history"
    assert result[0] == test_title, f"Title mismatch: expected {test_title}, got {result[0]}"
    
    # Try adding the same URL again (should not cause error due to UNIQUE constraint handling)
    add_to_history(test_url, test_title, test_path)
    
    print("✓ Database operations tests passed!")
    return True

def test_config_operations():
    """Test configuration operations"""
    print("Testing configuration operations...")
    
    from utoob import load_config, save_config, CONFIG_FILE
    import json
    import os
    
    # Load initial config (should have default values)
    config = load_config()
    assert "download_path" in config, "Config should have download_path key"
    assert config["download_path"] == "downloads", f"Default download path should be 'downloads', got {config['download_path']}"
    
    # Save a new config
    new_config = {"download_path": "/custom/downloads", "other_setting": "value"}
    save_config(new_config)
    
    # Load and verify
    loaded_config = load_config()
    assert loaded_config == new_config, f"Config mismatch: expected {new_config}, got {loaded_config}"
    
    # Verify config file exists
    assert os.path.exists(CONFIG_FILE), f"Config file {CONFIG_FILE} was not created"
    
    # Restore default config for other tests
    save_config({"download_path": "downloads"})
    
    print("✓ Configuration operations tests passed!")
    return True

def test_security_vulnerability_checks():
    """Test for potential security vulnerabilities"""
    print("Testing security vulnerability checks...")
    
    from utoob import validate_url, validate_youtube_url, sanitize_filename
    
    # Test for command injection vulnerabilities in URL validation
    injection_attempts = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ;rm -rf /",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ && rm -rf /",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ | cat /etc/passwd",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ`cat /etc/passwd`",
        "https://www.youtube.com/watch?v=$(cat /etc/passwd)",
        "https://www.youtube.com/;rm -rf /",
        "file:///etc/passwd",
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>"
    ]
    
    print("  Testing command injection attempts:")
    for attempt in injection_attempts:
        url_valid = validate_url(attempt)
        youtube_valid = validate_youtube_url(attempt)
        print(f"    {attempt[:50]}... -> URL: {url_valid}, YouTube: {youtube_valid}")
        assert url_valid == False, f"Security vulnerability: URL validation passed malicious input: {attempt}"
        assert youtube_valid == False, f"Security vulnerability: YouTube validation passed malicious input: {attempt}"
    
    # Test path traversal in sanitize_filename
    traversal_attempts = [
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        "/etc/passwd/..",
        "../../../../../../../../../../../tmp/"
    ]
    
    print("  Testing path traversal attempts:")
    for attempt in traversal_attempts:
        sanitized = sanitize_filename(attempt)
        print(f"    {attempt} -> {sanitized}")
        # Ensure traversal patterns are removed/replaced
        assert '../' not in sanitized, f"Path traversal not properly sanitized: {sanitized}"
        assert '..\\' not in sanitized, f"Path traversal not properly sanitized: {sanitized}"
        # Ensure no dangerous paths remain
        assert 'etc/passwd' not in sanitized.lower(), f"Sensitive path not sanitized: {sanitized}"
    
    print("✓ Security vulnerability checks passed!")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("Testing edge cases and error handling...")
    
    from utoob import validate_url, validate_youtube_url, sanitize_filename
    
    # Test extremely long URLs
    long_url = "https://www.youtube.com/watch?v=" + "a" * 10000
    result = validate_url(long_url)
    # Should still validate as a proper URL structure
    print(f"  Long URL validation: {result}")
    
    # Test special characters in filenames
    special_filenames = [
        "file with spaces.txt",
        "file_with_üñíçødé_chars.txt",  # Unicode
        "file_with_emoji_😀.txt",
        "file_with_numbers_12345.txt",
        "file_with.dots.in.name.txt",
        "file-with-dashes.txt",
        "file_with_underscores.txt",
        "file_with(parentheses).txt",
        "file_with[brackets].txt",
        "file_with{braces}.txt"
    ]
    
    print("  Testing special filenames:")
    for filename in special_filenames:
        sanitized = sanitize_filename(filename)
        print(f"    {filename} -> {sanitized}")
        # Ensure the sanitized version is still reasonable
        assert len(sanitized) <= 255, f"Sanitized filename too long: {len(sanitized)}"
        # Should not contain dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in dangerous_chars:
            assert char not in sanitized, f"Dangerous character '{char}' not removed from: {sanitized}"
    
    print("✓ Edge cases and error handling tests passed!")
    return True

def main():
    """Run all tests"""
    print("Starting comprehensive testing of utoob CLI application...")
    print("=" * 60)
    
    try:
        test_url_validation()
        print()
        
        test_playlist_detection()
        print()
        
        test_database_operations()
        print()
        
        test_config_operations()
        print()
        
        test_security_vulnerability_checks()
        print()
        
        test_edge_cases()
        print()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! The utoob CLI application appears to be working correctly.")
        print("✅ URL validation is working properly")
        print("✅ Security measures are in place")
        print("✅ Database operations are functional")
        print("✅ Configuration management works")
        print("✅ Playlist detection is accurate")
        print("✅ Edge cases are handled properly")
        
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()