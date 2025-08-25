# vim: set ft=python ts=4 sw=4 expandtab:
import math
import os
import pathlib
import shutil
from datetime import MINYEAR, datetime, timedelta
from typing import Any

import click
from PIL import Image
from PIL.ExifTags import TAGS

from reorder.interface import ImageData

_IMAGE_PREFIX = "image"
_MIN_DATE = datetime(MINYEAR, 1, 1).isoformat()  # noqa: DTZ001


def find_images(source: str, offsets: dict[str, timedelta] | None = None) -> list[ImageData]:
    """Recurses through a source directory, building a list of images in it."""
    images = []
    for path in pathlib.Path(source).rglob("*"):
        if path.is_file():
            image = _get_image_data(path, offsets)
            images.append(image)
    return images


def copy_images(source: str, target: str, offsets: dict[str, timedelta] | None = None) -> int:
    """Copy images from a source dir to a target dir, ordered by EXIF date and then source path."""
    if not os.path.exists(target):
        os.makedirs(target)
    images = find_images(source, offsets)
    images.sort(key=lambda x: f"{x.exif_date.isoformat() if x.exif_date else _MIN_DATE}|{x.path}")
    digits = math.ceil(math.log10(len(images) + 1))  # number of digits required to represent all images in list
    index = 0
    with click.progressbar(images, label="Copying files") as entries:
        for image in entries:
            index += 1
            sourcefile = str(image.path)
            prepend = _IMAGE_PREFIX + "{0:0{digits}}__".format(index, digits=digits)
            targetfile = os.path.join(target, prepend + os.path.basename(sourcefile))
            shutil.copyfile(sourcefile, targetfile)
    return index


def _get_image_data(path: pathlib.Path, offsets: dict[str, timedelta] | None) -> ImageData:
    """Get the image data for a file, applying offsets as necessary."""
    # In the original Python 2 implementation, I looked at both DateTime and DateTimeOriginal.
    # In the meantime, the EXIF implementation in Pillow has changed, and it takes more effort
    # to get at DateTimeOriginal.  For now, I'm going to look at only DateTime.
    tags = _get_exif_tags(path)
    model = tags.get("Model", None)
    date_time = tags.get("DateTime", None)
    exif_date = None
    if date_time:
        exif_date = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
        if offsets and model in offsets:
            exif_date += offsets[model]
    return ImageData(path=path, model=model, exif_date=exif_date)


def _get_exif_tags(path: pathlib.Path) -> dict[str | int, Any]:
    """Get the EXIF tags associated with an image on disk."""
    # See: https://stackoverflow.com/questions/4764932/in-python-how-do-i-read-the-exif-data-for-an-image
    tags = {}
    try:
        with Image.open(path) as image:
            for tag, value in image.getexif().items():
                decoded = TAGS.get(tag, tag)
                tags[decoded] = value
    except Exception:  # noqa: BLE001,S110
        pass
    return tags
