# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import os
from datetime import timedelta
from typing import List
from unittest.mock import patch

from click.testing import CliRunner, Result

from reorder.cli import reorder as command
from reorder.interface import ImageData

from .testutils import exifdate, imagepath

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def invoke(args: List[str]) -> Result:
    return CliRunner().invoke(command, args)


class TestCommon:
    def test_h(self):
        result = invoke(["-h"])
        assert result.exit_code == 0

    def test_help(self):
        result = invoke(["--help"])
        assert result.exit_code == 0

    @patch("importlib.metadata.version")  # this is used underneath by @click.version_option()
    def test_version(self, version):
        version.return_value = "1234"
        result = invoke(["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("reorder, version 1234")

    def test_no_args(self):
        result = invoke([])
        assert result.exit_code == 0


class TestAnalyze:
    def test_h(self):
        result = invoke(["analyze", "-h"])
        assert result.exit_code == 0

    def test_help(self):
        result = invoke(["analyze", "--help"])
        assert result.exit_code == 0

    def test_missing_source(self):
        result = invoke(["analyze"])
        assert result.exit_code == 2

    @patch("reorder.cli.find_images")
    def test_empty_source(self, find_images):
        find_images.return_value = []
        result = invoke(["analyze", "source"])
        assert result.exit_code == 0
        assert result.output == "No images found.\n"

    @patch("reorder.cli.find_images")
    def test_source_no_images(self, find_images):
        find_images.return_value = [
            ImageData(path=imagepath("movie.mp4"), model=None, exif_date=None),
        ]
        result = invoke(["analyze", "source"])
        assert result.exit_code == 0
        assert (
            result.output
            == """Total files: 1
Images found: 0
Models found:

"""
        )

    @patch("reorder.cli.find_images")
    def test_source_with_images(self, find_images):
        find_images.return_value = [
            ImageData(path=imagepath("movie.mp4"), model=None, exif_date=None),
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:45:12")),
        ]
        result = invoke(["analyze", "source"])
        assert result.exit_code == 0
        assert (
            result.output
            == """Total files: 3
Images found: 2
Models found:
  - DMC-TS6
  - Pixel 2
"""
        )


class TestCopy:
    def test_h(self):
        result = invoke(["copy", "-h"])
        assert result.exit_code == 0

    def test_help(self):
        result = invoke(["copy", "--help"])
        assert result.exit_code == 0

    def test_missing_source(self):
        result = invoke(["copy"])
        assert result.exit_code == 2

    def test_missing_target(self):
        result = invoke(["copy", "source"])
        assert result.exit_code == 2

    def test_invalid_offset(self):
        result = invoke(["copy", "--offset", "bogus", "source", "target"])
        assert result.exit_code == 2
        assert "Invalid offset" in result.output

    @patch("reorder.cli.copy_images")
    def test_valid(self, copy_images):
        result = invoke(["copy", "source", "target"])
        assert result.exit_code == 0
        copy_images.assert_called_once_with("source", "target", offsets={})

    @patch("reorder.cli.copy_images")
    def test_valid_offset_one(self, copy_images):
        result = invoke(["copy", "--offset", "PowerShot A70=+06:55", "source", "target"])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(
            "source",
            "target",
            offsets={"PowerShot A70": timedelta(hours=6, minutes=55)},
        )

    @patch("reorder.cli.copy_images")
    def test_valid_offset_multiple(self, copy_images):
        result = invoke(["copy", "--offset", "a=+06:55", "-o", "b=-00:03", "source", "target"])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(
            "source",
            "target",
            offsets={
                "a": timedelta(hours=6, minutes=55),
                "b": timedelta(minutes=-3),
            },
        )
