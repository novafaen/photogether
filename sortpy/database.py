#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Save and retrieve file information from database."""

import sqlite3
from pathlib import Path
from typing import Optional


def initialize_database(db_path: Path = Path("file_info.db")):
    """Initialize the SQLite database to store file information."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            created_timestamp TEXT,
            modified_timestamp TEXT,
            type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duplicates (
            id INTEGER PRIMARY KEY,
            sha256 TEXT NOT NULL,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            created_timestamp TEXT,
            modified_timestamp TEXT,
            FOREIGN KEY (sha256) REFERENCES files (sha256)
        )
    ''')
    conn.commit()
    conn.close()

def insert_file_info(file_info: dict, db_path: str = "file_info.db"):
    """Insert file information into the database.

    :param file_info: Dictionary containing file information.
    :param db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (filename, path, sha256, created_timestamp, modified_timestamp, type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        file_info['filename'],
        str(file_info['path']),
        file_info['sha256'],
        file_info['created_timestamp'].isoformat() if file_info['created_timestamp'] else None,
        file_info['modified_timestamp'].isoformat() if file_info['modified_timestamp'] else None,
        file_info['type']
    ))

    # Insert into duplicates if hash already exists
    cursor.execute('SELECT id FROM files WHERE sha256 = ?', (file_info['sha256'],))
    if cursor.fetchone():
        cursor.execute('''
            INSERT INTO duplicates (sha256, filename, path, created_timestamp, modified_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            file_info['sha256'],
            file_info['filename'],
            str(file_info['path']),
            file_info['created_timestamp'].isoformat() if file_info['created_timestamp'] else None,
            file_info['modified_timestamp'].isoformat() if file_info['modified_timestamp'] else None
        ))
    conn.commit()
    conn.close()

def file_exists_by_filename(filename: str, db_path: str = "file_info.db") -> bool:
    """Check if a file exists in the database by its filename.

    :param filename: Name of the file to check.
    :param db_path: Path to the SQLite database file.
    :return: True if the file exists, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM files WHERE filename = ?', (filename,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def file_exists_by_hash(sha256: str, db_path: str = "file_info.db") -> bool:
    """Check if a file exists in the database by its SHA-256 hash.

    :param sha256: SHA-256 hash of the file to check.
    :param db_path: Path to the SQLite database file.
    :return: True if the file exists, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM files WHERE sha256 = ?', (sha256,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_files_by_hash(sha256: str, db_path: str = "file_info.db") -> Optional[list]:
    """Get all files that have the given SHA-256 hash.

    :param sha256: SHA-256 hash of the file to look for.
    :param db_path: Path to the SQLite database file.
    :return: List of files with the same hash or None if no matches are found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT filename, path, created_timestamp, modified_timestamp FROM duplicates WHERE sha256 = ?', (sha256,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [
            {
                'filename': row[0],
                'path': row[1],
                'created_timestamp': row[2],
                'modified_timestamp': row[3]
            } for row in rows
        ]
    return None
