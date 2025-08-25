# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import os
import pathlib
from datetime import datetime

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def imagepath(value: str) -> pathlib.Path:
    return pathlib.Path(os.path.join(IMAGE_DIR, value))


def exifdate(value: str) -> datetime:
    return datetime.fromisoformat(value)
