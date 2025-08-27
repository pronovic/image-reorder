# vim: set ft=python ts=4 sw=4 expandtab:
from datetime import datetime
from pathlib import Path

IMAGE_DIR = Path(__file__).parent / "fixtures" / "samples"


def imagepath(value: str) -> Path:
    return IMAGE_DIR / value


def exifdate(value: str) -> datetime:
    return datetime.fromisoformat(value)
