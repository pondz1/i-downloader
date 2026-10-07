"""Tests for helper utility functions"""

from src.utils.helpers import (
    format_size,
    format_speed,
    format_time,
    extract_filename_from_url,
    extract_filename_from_header,
    is_valid_url,
    sanitize_filename,
)


def test_format_size():
    assert format_size(0) == "0 B"
    assert format_size(500) == "500.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024 * 2) == "2.00 GB"


def test_format_speed():
    assert format_speed(0) == "0 B/s"
    assert format_speed(1024 * 512) == "512.00 KB/s"
    assert format_speed(1024 * 1024 * 10) == "10.00 MB/s"


def test_format_time():
    assert format_time(-1) == "∞"
    assert format_time(30) == "30s"
    assert format_time(75) == "1:15"
    assert format_time(3665) == "1:01:05"


def test_extract_filename_from_url():
    assert extract_filename_from_url("https://example.com/files/archive.zip") == "archive.zip"
    assert extract_filename_from_url("https://example.com/image.png?size=large") == "image.png"
    assert extract_filename_from_url("https://example.com/") == "download"


def test_extract_filename_from_header():
    header = 'attachment; filename="document.pdf"'
    assert extract_filename_from_header(header) == "document.pdf"

    # RFC 5987 UTF-8 encoded filename
    header_utf8 = "attachment; filename*=UTF-8''report_2026.pdf"
    assert extract_filename_from_header(header_utf8) == "report_2026.pdf"

    # Path traversal protection
    traversal_header = 'attachment; filename="../../../etc/passwd"'
    extracted = extract_filename_from_header(traversal_header)
    assert ".." not in extracted
    assert extracted == "passwd"


def test_is_valid_url():
    assert is_valid_url("https://example.com/test.zip") is True
    assert is_valid_url("http://localhost:8000/file") is True
    assert is_valid_url("ftp://example.com/file") is False
    assert is_valid_url("not a url") is False


def test_sanitize_filename():
    assert sanitize_filename("test:file/name?.mp4") == "test_file_name_.mp4"
    assert sanitize_filename('sample"quote"<>|*') == "sample_quote_____"
