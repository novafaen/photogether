#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dataclass to store FileInfo."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class FileInfo:
    """File information."""

    filename: str
    path: Path
    sha256: str
    created_timestamp: Optional[datetime]
    modified_timestamp: Optional[datetime]
    type: str