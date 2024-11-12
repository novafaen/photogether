#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Save and retrieve file information from database."""

import sqlite3
from pathlib import Path
from typing import Optional, Self
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    filename: str
    path: Path
    sha256: str
    created_timestamp: Optional[datetime]
    modified_timestamp: Optional[datetime]
    type: str


class Database:
    """Database layer."""

    def __init__(self: Self, db_path: Path = Path('sorted.db')) -> None:
        """Inititalte database.

        :param Path db_path: Path to database file, default to `sorted.py`.
        :return: None
        """
        if not isinstance(db_path, Path):
            raise TypeError('db_path must be of type Path.')

        self._conn = sqlite3.connect(db_path)
        self._cursor = self._conn.cursor()

    def close(self: Self) -> None:
        """Close database connection.

        :return: None
        """
        self._cursor.close()
        self._cursor = None
        self._conn.close()
        self._conn = None

    def initialize_database(self: Self) -> None:
        """Initiate database file."""
        if self._cursor is None or self._conn is None:
            raise ConnectionError('Could not initiate database, connection is closed.')

        self._cursor.execute('''
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
        self._cursor.execute('''
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
        self._conn.commit()

    def insert_file_info(self: Self, file_info: FileInfo) -> None:
        """Insert file information into the database.

        :param file_info: FileInfo dataclass containing file information.
        :return: None
        """
        if not isinstance(file_info, FileInfo):
            raise TypeError('Could not save file info to database: Incorrect type.')

        self._cursor.execute('''
            INSERT INTO files (filename, path, sha256, created_timestamp, modified_timestamp, type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            file_info.filename,
            str(file_info.path),
            file_info.sha256,
            file_info.created_timestamp.isoformat() if file_info.created_timestamp else None,
            file_info.modified_timestamp.isoformat() if file_info.modified_timestamp else None,
            file_info.type
        ))

        # Insert into duplicates if hash already exists
        self._cursor.execute('SELECT id FROM files WHERE sha256 = ?', (file_info.sha256,))
        if self._cursor.fetchone():
            self._cursor.execute('''
                INSERT INTO duplicates (sha256, filename, path, created_timestamp, modified_timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                file_info.sha256,
                file_info.filename,
                str(file_info.path),
                file_info.created_timestamp.isoformat() if file_info.created_timestamp else None,
                file_info.modified_timestamp.isoformat() if file_info.modified_timestamp else None
            ))
        self._conn.commit()

    def file_exists_by_filename(self: Self, filename: str) -> bool:
        """Check if a file exists in the database by its filename.

        :param filename: Name of the file to check.
        :return: True if the file exists, False otherwise.
        """
        self._cursor.execute('SELECT 1 FROM files WHERE filename = ?', (filename,))
        result = self._cursor.fetchone()
        return result is not None

    def file_exists_by_hash(self: Self, sha256: str) -> bool:
        """Check if a file exists in the database by its SHA-256 hash.

        :param sha256: SHA-256 hash of the file to check.
        :return: True if the file exists, False otherwise.
        """
        self._cursor.execute('SELECT 1 FROM files WHERE sha256 = ?', (sha256,))
        result = self._cursor.fetchone()
        return result is not None

    def get_files_by_hash(self: Self, sha256: str) -> Optional[list]:
        """Get all files that have the given SHA-256 hash.

        :param sha256: SHA-256 hash of the file to look for.
        :return: List of files with the same hash or None if no matches are found.
        """
        self._cursor.execute('SELECT filename, path, created_timestamp, modified_timestamp FROM duplicates WHERE sha256 = ?', (sha256,))
        rows = self._cursor.fetchall()
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
