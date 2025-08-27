# vim: set ft=python ts=4 sw=4 expandtab:
from datetime import datetime
from pathlib import Path

from attr import frozen


@frozen
class ImageData:
    path: Path
    model: str | None
    exif_date: datetime | None
