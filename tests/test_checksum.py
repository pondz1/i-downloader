"""Tests for checksum verification"""

import hashlib
import tempfile
from pathlib import Path
import pytest

from src.core.checksum import ChecksumVerifier


def test_calculate_file_hash():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Hello i-Downloader!")
        temp_path = f.name

    try:
        # Expected SHA256
        expected_sha256 = hashlib.sha256(b"Hello i-Downloader!").hexdigest()
        actual_sha256 = ChecksumVerifier.calculate_file_hash(temp_path, "sha256")
        assert actual_sha256 == expected_sha256

        # Expected MD5
        expected_md5 = hashlib.md5(b"Hello i-Downloader!").hexdigest()
        actual_md5 = ChecksumVerifier.calculate_file_hash(temp_path, "md5")
        assert actual_md5 == expected_md5

        # Expected SHA1
        expected_sha1 = hashlib.sha1(b"Hello i-Downloader!").hexdigest()
        actual_sha1 = ChecksumVerifier.calculate_file_hash(temp_path, "sha1")
        assert actual_sha1 == expected_sha1
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_verify_checksum():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Integrity test payload")
        temp_path = f.name

    try:
        sha256 = hashlib.sha256(b"Integrity test payload").hexdigest()
        assert ChecksumVerifier.verify_checksum(temp_path, sha256, "sha256") is True
        assert ChecksumVerifier.verify_checksum(temp_path, sha256.upper(), "sha256") is True
        assert ChecksumVerifier.verify_checksum(temp_path, "wronghash", "sha256") is False
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_unsupported_algorithm():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"data")
        temp_path = f.name

    try:
        with pytest.raises(ValueError):
            ChecksumVerifier.calculate_file_hash(temp_path, "unsupported_algo")
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_get_checksum_display():
    assert ChecksumVerifier.get_checksum_display("", "sha256") == "No checksum"
    full_hash = "abcdef0123456789abcdef0123456789"
    display = ChecksumVerifier.get_checksum_display(full_hash, "sha256")
    assert display.startswith("SHA256: abcdef012345...")
