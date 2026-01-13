"""
File utility functions for download operations
"""

import os
import aiofiles
from pathlib import Path
from typing import List


async def merge_segments(segment_files: List[str], output_file: str, delete_segments: bool = True):
    """
    Merge multiple segment files into a single output file.
    
    Args:
        segment_files: List of segment file paths in order
        output_file: Output file path
        delete_segments: Whether to delete segment files after merging
    """
    async with aiofiles.open(output_file, 'wb') as outfile:
        for segment_file in segment_files:
            if os.path.exists(segment_file):
                async with aiofiles.open(segment_file, 'rb') as infile:
                    while True:
                        chunk = await infile.read(1024 * 1024)  # 1MB chunks
                        if not chunk:
                            break
                        await outfile.write(chunk)
    
    # Delete segment files
    if delete_segments:
        for segment_file in segment_files:
            try:
                if os.path.exists(segment_file):
                    os.remove(segment_file)
            except Exception as e:
                print(f"Warning: Could not delete segment file {segment_file}: {e}")


def create_segment_files(download_id: str, num_segments: int, temp_dir: Path) -> List[str]:
    """
    Create temporary segment file paths.
    
    Args:
        download_id: Download ID
        num_segments: Number of segments
        temp_dir: Temporary directory path
        
    Returns:
        List of segment file paths
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    return [
        str(temp_dir / f"{download_id}_segment_{i}.tmp")
        for i in range(num_segments)
    ]


def cleanup_temp_files(download_id: str, temp_dir: Path):
    """
    Clean up temporary files for a download.
    
    Args:
        download_id: Download ID
        temp_dir: Temporary directory path
    """
    try:
        for file in temp_dir.glob(f"{download_id}_segment_*.tmp"):
            file.unlink()
    except Exception as e:
        print(f"Warning: Could not cleanup temp files: {e}")


def get_file_icon_type(filename: str) -> str:
    """
    Get icon type based on file extension.
    
    Args:
        filename: Filename with extension
        
    Returns:
        Icon type string
    """
    ext = Path(filename).suffix.lower()
    
    video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
    audio_exts = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
    archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
    document_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
    executable_exts = {'.exe', '.msi', '.dmg', '.app', '.deb', '.rpm'}
    
    if ext in video_exts:
        return 'video'
    elif ext in audio_exts:
        return 'audio'
    elif ext in image_exts:
        return 'image'
    elif ext in archive_exts:
        return 'archive'
    elif ext in document_exts:
        return 'document'
    elif ext in executable_exts:
        return 'executable'
    else:
        return 'file'
