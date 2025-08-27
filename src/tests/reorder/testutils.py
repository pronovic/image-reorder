# vim: set ft=python ts=4 sw=4 expandtab:
import os
from datetime import datetime
from pathlib import Path

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def imagepath(value: str) -> Path:
    return Path(os.path.join(IMAGE_DIR, value))


def exifdate(value: str) -> datetime:
    return datetime.fromisoformat(value)
