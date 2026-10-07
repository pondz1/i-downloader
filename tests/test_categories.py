"""Tests for category detection and file organization"""

from src.utils.categories import (
    get_category_from_filename,
    get_category_from_content_type,
    get_category_name,
)


def test_get_category_from_filename():
    assert get_category_from_filename("movie.mp4") == "videos"
    assert get_category_from_filename("song.mp3") == "audio"
    assert get_category_from_filename("photo.png") == "images"
    assert get_category_from_filename("notes.pdf") == "documents"
    assert get_category_from_filename("package.zip") == "archives"
    assert get_category_from_filename("installer.dmg") == "programs"
    assert get_category_from_filename("linux.iso") == "all"


def test_get_category_from_content_type():
    assert get_category_from_content_type("video/mp4") == "videos"
    assert get_category_from_content_type("audio/mpeg") == "audio"
    assert get_category_from_content_type("image/jpeg") == "images"
    assert get_category_from_content_type("application/pdf") == "documents"
    assert get_category_from_content_type("application/zip") == "archives"
    assert get_category_from_content_type("application/octet-stream") == "all"


def test_get_category_name():
    assert get_category_name("videos") == "Videos"
    assert get_category_name("images") == "Images"
    assert get_category_name("unknown") == "All Files"
