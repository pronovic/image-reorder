# vim: set ft=python ts=4 sw=4 expandtab:
from datetime import timedelta

from reorder.image import copy_images, find_images
from reorder.interface import ImageData
from tests.reorder.testutils import IMAGE_DIR, exifdate, imagepath


class TestFindImages:
    def test_find_images_no_offset(self):
        expected = [
            ImageData(path=imagepath("nodate.jpg"), model="DMC-TS6", exif_date=None),
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:45:12")),
            ImageData(path=imagepath("pixel5a.jpg"), model="Pixel 5a", exif_date=exifdate("2023-09-03T09:36:43")),
        ]
        images = find_images(IMAGE_DIR)
        assert sorted(images, key=lambda x: x.path) == expected

    def test_find_images_with_offset(self):
        expected = [
            ImageData(path=imagepath("nodate.jpg"), model="DMC-TS6", exif_date=None),
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:48:12")),  # +3 minutes
            ImageData(path=imagepath("pixel5a.jpg"), model="Pixel 5a", exif_date=exifdate("2023-09-03T09:36:43")),
        ]
        offsets = {"Pixel 2": timedelta(minutes=3)}
        images = find_images(IMAGE_DIR, offsets=offsets)
        assert sorted(images, key=lambda x: x.path) == expected


class TestCopyImages:
    def test_copy_images(self, tmp_path):
        target = tmp_path / "target"
        target.mkdir()
        copy_images(IMAGE_DIR, target, offsets=None)
        copied = sorted([path for path in target.rglob("*") if path.is_file()])
        assert copied == [
            target / "image1__nodate.jpg",
            target / "image2__pixel5a.jpg",
            target / "image3__pixel2.jpg",
            target / "image4__panasonic.jpg",
        ]
