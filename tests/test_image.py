# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import os
import pathlib
from datetime import datetime, timedelta

from reorder.image import find_images
from reorder.interface import ImageData

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def imagepath(value: str) -> pathlib.Path:
    return pathlib.Path(os.path.join(IMAGE_DIR, value))


def exifdate(value: str) -> datetime:
    return datetime.fromisoformat(value)


class TestImage:
    def test_find_images(self):
        expected = [
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:45:12")),
            ImageData(path=imagepath("pixel5a.jpg"), model="Pixel 5a", exif_date=exifdate("2023-09-03T09:36:43")),
        ]
        images = find_images(IMAGE_DIR)
        assert sorted(images, key=lambda x: x.path) == expected

    def test_find_images_with_offset(self):
        expected = [
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:48:12")),  # +3 minutes
            ImageData(path=imagepath("pixel5a.jpg"), model="Pixel 5a", exif_date=exifdate("2023-09-03T09:36:43")),
        ]
        offsets = {"Pixel 2": timedelta(minutes=3)}
        images = find_images(IMAGE_DIR, offsets=offsets)
        assert sorted(images, key=lambda x: x.path) == expected
