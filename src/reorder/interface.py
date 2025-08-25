# vim: set ft=python ts=4 sw=4 expandtab:
import pathlib
from datetime import datetime

from attr import frozen


@frozen
class ImageData:
    path: pathlib.Path
    model: str | None
    exif_date: datetime | None
