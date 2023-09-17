# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import pathlib
from datetime import datetime
from typing import Optional

from attr import frozen


@frozen
class ImageData:
    path: pathlib.Path
    model: Optional[str]
    exif_date: Optional[datetime]
