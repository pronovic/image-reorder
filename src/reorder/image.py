# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import pathlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from PIL import Image
from PIL.ExifTags import TAGS

from reorder.interface import ImageData


def find_images(source: str, offsets: Optional[Dict[str, timedelta]] = None) -> List[ImageData]:
    """Recurses through a source directory, building a list of images in it."""
    images = []
    for path in pathlib.Path(source).rglob("*"):
        if path.is_file():
            image = _get_image_data(path, offsets)
            images.append(image)
    return sorted(images, key=lambda x: x.path)


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
