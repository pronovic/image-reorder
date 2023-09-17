# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import math
import os
import pathlib
import shutil
from datetime import MINYEAR, datetime, timedelta
from typing import Any, Dict, List, Optional

import click
from PIL import Image
from PIL.ExifTags import TAGS

from reorder.interface import ImageData

_IMAGE_PREFIX = "image"
_MIN_DATE = datetime(MINYEAR, 1, 1).isoformat()


def find_images(source: str, offsets: Optional[Dict[str, timedelta]] = None) -> List[ImageData]:
    """Recurses through a source directory, building a list of images in it."""
    images = []
    for path in pathlib.Path(source).rglob("*"):
        if path.is_file():
            image = _get_image_data(path, offsets)
            images.append(image)
    return images


def copy_images(source: str, target: str, offsets: Optional[Dict[str, timedelta]] = None) -> int:
    """Copy images from a source dir to a target dir, ordered by EXIF date and then source path."""
    if not os.path.exists(target):
        os.makedirs(target)
    images = find_images(source, offsets)
    images.sort(key=lambda x: "%s|%s" % (x.exif_date.isoformat() if x.exif_date else _MIN_DATE, x.path))
    digits = int(math.ceil(math.log(len(images) + 1, 10)))  # number of digits required to represent all images in list
    index = 0
    with click.progressbar(images, label="Copying files") as entries:
        for image in entries:
            index += 1
            sourcefile = str(image.path)
            prepend = _IMAGE_PREFIX + "{0:0{digits}}__".format(index, digits=digits)
            targetfile = os.path.join(target, prepend + os.path.basename(sourcefile))
            shutil.copyfile(sourcefile, targetfile)
    return index


def _get_image_data(path: pathlib.Path, offsets: Optional[Dict[str, timedelta]]) -> ImageData:
    """Get the image data for a file, applying offsets as necessary."""
    # In the original Python 2 implementation, I looked at both DateTime and DateTimeOriginal.
    # In the meantime, the EXIF implementation in Pillow has changed, and it takes more effort
    # to get at DateTimeOriginal.  For now, I'm going to look at only DateTime.
    tags = _get_exif_tags(path)
    model = tags["Model"] if "Model" in tags else None
    date_time = tags["DateTime"] if "DateTime" in tags else None
    exif_date = None
    if date_time:
        exif_date = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
        if offsets and model in offsets:
            exif_date += offsets[model]
    return ImageData(path=path, model=model, exif_date=exif_date)


def _get_exif_tags(path: pathlib.Path) -> Dict[str | int, Any]:
    """Get the EXIF tags associated with an image on disk."""
    # See: https://stackoverflow.com/questions/4764932/in-python-how-do-i-read-the-exif-data-for-an-image
    tags = {}
    try:
        info = Image.open(path).getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            tags[decoded] = value
    except Exception:  # pylint: disable=broad-exception-caught:
        pass
    return tags
