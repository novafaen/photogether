#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Index files and get file information."""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

# Define known file extensions for pictures and videos
PICTURE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}

# Regex pattern to match filenames with common timestamp structures (e.g., IMG_20211012_123456.jpg)
TIMESTAMP_REGEX = [
    # 1970-01-01 03.14.15
    r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) ' \
    r'(?P<hour>\d{2}).(?P<minute>\d{2}).(?P<second>\d{2})',
    # 19700101_031415
    r'(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_' \
    r'(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})',
    # IMG_20190830_214259
    r'(IMG|video|MVIMG|VID)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})_' \
    r'(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})(_\d)*'
]


def get_file_info(file_path: Path) -> Dict[str, Union[str, datetime, None]]:
    """Get information about a file, including timestamps, type, and SHA hash.

    :param file_path: Path to the file.
    :return: Dictionary with file information.
    """
    file_stat = file_path.stat()
    file_info = {
        'filename': file_path.name,
        'extension': file_path.suffix,
        'created_timestamp': datetime.fromtimestamp(file_stat.st_ctime),
        'created_timestamp_dict': {
            'year': datetime.fromtimestamp(file_stat.st_ctime).year,
            'month': datetime.fromtimestamp(file_stat.st_ctime).month,
            'day': datetime.fromtimestamp(file_stat.st_ctime).day,
            'hour': datetime.fromtimestamp(file_stat.st_ctime).hour,
            'minute': datetime.fromtimestamp(file_stat.st_ctime).minute,
            'second': datetime.fromtimestamp(file_stat.st_ctime).second
        },
        'modified_timestamp': datetime.fromtimestamp(file_stat.st_mtime),
        'modified_timestamp_dict': {
            'year': datetime.fromtimestamp(file_stat.st_mtime).year,
            'month': datetime.fromtimestamp(file_stat.st_mtime).month,
            'day': datetime.fromtimestamp(file_stat.st_mtime).day,
            'hour': datetime.fromtimestamp(file_stat.st_mtime).hour,
            'minute': datetime.fromtimestamp(file_stat.st_mtime).minute,
            'second': datetime.fromtimestamp(file_stat.st_mtime).second
        },
        'type': 'unknown',
        'filename_timestamp': None,
        'sha256': None
    }

    # Determine file type
    if file_info['extension'].lower() in PICTURE_EXTENSIONS:
        file_info['type'] = 'picture'
    elif file_info['extension'].lower() in VIDEO_EXTENSIONS:
        file_info['type'] = 'video'

    # Check for timestamp in filename
    for timestamp_format in TIMESTAMP_REGEX:
        match = re.match(timestamp_format, file_info['filename'])
        if match is not None:
            year, month, day, hour, minute, second = \
                match.group('year'), match.group('month'), match.group('day'), \
                match.group('hour'), match.group('minute'), match.group('second')

            file_info['filename_timestamp_dict'] = {
                'year': int(year),
                'month': int(month),
                'day': int(day),
                'hour': int(hour) if hour else 0,
                'minute': int(minute) if minute else 0,
                'second': int(second) if second else 0
            }
            file_info['filename_timestamp'] = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second)
            )

    # Calculate SHA-256 hash of the file
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    file_info['sha256'] = sha256_hash.hexdigest()

    return file_info

def index_folder(folder: Union[str, Path]) -> List[Dict[str, Union[str, datetime, None]]]:
    """Index all files in a folder.

    :param folder: Folder to index.
    :return: List of dictionaries with information about each file.
    """
    folder_path = Path(folder).resolve()
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"The folder '{folder}' does not exist or is not a directory.")

    indexed_files = []
    for file in folder_path.rglob('*'):
        if file.is_file():
            indexed_files.append(get_file_info(file))

    return indexed_files