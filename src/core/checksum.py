"""
Checksum verification for downloaded files
"""

import hashlib
from pathlib import Path
from typing import Optional


class ChecksumVerifier:
    """Verify file checksums (MD5, SHA1, SHA256)"""

    SUPPORTED_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }

    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """
        Calculate the hash of a file.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')

        Returns:
            Hexadecimal hash string

        Raises:
            ValueError: If algorithm is not supported
            FileNotFoundError: If file doesn't exist
        """
        if algorithm not in ChecksumVerifier.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. "
                           f"Supported: {list(ChecksumVerifier.SUPPORTED_ALGORITHMS.keys())}")

        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_func = ChecksumVerifier.SUPPORTED_ALGORITHMS[algorithm]()

        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    @staticmethod
    def verify_checksum(file_path: str, expected: str, algorithm: str = 'sha256') -> bool:
        """
        Verify a file's checksum matches the expected value.

        Args:
            file_path: Path to the file
            expected: Expected checksum value
            algorithm: Hash algorithm used for expected checksum

        Returns:
            True if checksums match, False otherwise
        """
        try:
            actual = ChecksumVerifier.calculate_file_hash(file_path, algorithm)
            # Normalize to lowercase for comparison
            return actual.lower() == expected.lower().strip()
        except Exception:
            return False

    @staticmethod
    def get_checksum_display(checksum: str, algorithm: str = 'sha256') -> str:
        """
        Get a formatted display string for a checksum.

        Args:
            checksum: The checksum value
            algorithm: Hash algorithm

        Returns:
            Formatted string like "SHA256: abc123..."
        """
        if not checksum:
            return "No checksum"

        # Truncate long checksums for display
        display_hash = checksum[:12] + "..." if len(checksum) > 12 else checksum
        return f"{algorithm.upper()}: {display_hash}"
