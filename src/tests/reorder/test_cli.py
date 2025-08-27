# vim: set ft=python ts=4 sw=4 expandtab:
from datetime import timedelta
from unittest.mock import patch

import pytest
from click.testing import CliRunner, Result

from reorder.cli import reorder as command
from reorder.interface import ImageData
from tests.reorder.testutils import exifdate, imagepath


def invoke(args: list[str]) -> Result:
    return CliRunner().invoke(command, args)


@pytest.fixture
def working_dir(tmp_path):
    working_dir = tmp_path / "working"
    working_dir.mkdir()
    yield working_dir
    for child in working_dir.glob("**/*"):
        if child.is_file():
            child.chmod(0o666)
        if child.is_dir():
            child.chmod(0o777)


class TestCommon:
    def test_h(self):
        result = invoke(["-h"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder [OPTIONS]")

    def test_help(self):
        result = invoke(["--help"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder [OPTIONS]")

    @patch("importlib.metadata.version")  # this is used underneath by @click.version_option()
    def test_version(self, version):
        version.return_value = "1234"
        result = invoke(["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("reorder, version 1234")

    def test_no_args(self):
        result = invoke([])
        assert result.exit_code == 2
        assert result.output.startswith("Usage: reorder [OPTIONS]")


class TestAnalyze:
    def test_h(self):
        result = invoke(["analyze", "-h"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder analyze [OPTIONS]")

    def test_help(self):
        result = invoke(["analyze", "--help"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder analyze [OPTIONS]")

    def test_missing_source(self):
        result = invoke(["analyze"])
        assert result.exit_code == 2
        assert result.output.startswith("Usage: reorder analyze [OPTIONS]")

    def test_non_existing_source(self, working_dir):
        source = working_dir / "source"
        result = invoke(["analyze", str(source)])
        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_file_source(self, working_dir):
        source = working_dir / "source"
        source.touch()  # it's a file
        result = invoke(["analyze", str(source)])
        assert result.exit_code == 2
        assert "is a file" in result.output

    def test_unreadable_source(self, working_dir):
        source = working_dir / "source"
        source.mkdir(mode=0o000)  # it's a directory, but not readable
        result = invoke(["analyze", str(source)])
        assert result.exit_code == 2
        assert "is not readable" in result.output

    @patch("reorder.cli.find_images")
    def test_empty_source(self, find_images, working_dir):
        source = working_dir / "source"
        source.mkdir()  # it's a directory
        find_images.return_value = []
        result = invoke(["analyze", str(source)])
        assert result.exit_code == 0
        assert result.output == "No images found.\n"
        find_images.assert_called_once_with(source, offsets=None)

    @patch("reorder.cli.find_images")
    def test_source_no_images(self, find_images, working_dir):
        source = working_dir / "source"
        source.mkdir()  # it's a directory
        find_images.return_value = [
            ImageData(path=imagepath("movie.mp4"), model=None, exif_date=None),
        ]
        result = invoke(["analyze", str(source)])
        assert result.exit_code == 0
        assert (
            result.output
            == """Total files: 1
Images found: 0
Models found:

"""
        )
        find_images.assert_called_once_with(source, offsets=None)

    @patch("reorder.cli.find_images")
    def test_source_with_images(self, find_images, working_dir):
        source = working_dir / "source"
        source.mkdir()  # it's a directory
        find_images.return_value = [
            ImageData(path=imagepath("movie.mp4"), model=None, exif_date=None),
            ImageData(path=imagepath("panasonic.jpg"), model="DMC-TS6", exif_date=exifdate("2023-09-08T20:25:14")),
            ImageData(path=imagepath("pixel2.jpg"), model="Pixel 2", exif_date=exifdate("2023-09-07T15:45:12")),
        ]
        result = invoke(["analyze", str(source)])
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
        find_images.assert_called_once_with(source, offsets=None)


class TestCopy:
    def test_h(self):
        result = invoke(["copy", "-h"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder copy [OPTIONS]")

    def test_help(self):
        result = invoke(["copy", "--help"])
        assert result.exit_code == 0
        assert result.output.startswith("Usage: reorder copy [OPTIONS]")

    def test_missing_source(self):
        result = invoke(["copy"])
        assert result.exit_code == 2
        assert result.output.startswith("Usage: reorder copy [OPTIONS]")

    def test_non_existing_source(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        result = invoke(["copy", str(source), str(target)])
        assert "does not exist" in result.output

    def test_file_source(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.touch()  # it's a file
        result = invoke(["copy", str(source), str(target)])
        assert "is a file" in result.output

    def test_unreadable_source(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir(mode=0o000)  # it's a directory, but not readable
        result = invoke(["copy", str(source), str(target)])
        assert "is not readable" in result.output

    def test_missing_target(self, working_dir):
        source = working_dir / "source"
        source.mkdir()
        result = invoke(["copy", str(source)])
        assert result.exit_code == 2
        assert result.output.startswith("Usage: reorder copy [OPTIONS]")

    def test_file_target(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.touch()  # it's a file
        result = invoke(["copy", str(source), str(target)])
        assert "is a file" in result.output

    def test_unreadable_target(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.mkdir(mode=0o000)  # it's a directory, but not readable
        result = invoke(["copy", str(source), str(target)])
        assert "is not readable" in result.output

    def test_unwritable_target(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.mkdir(mode=0o400)  # it's a directory, but not writable
        result = invoke(["copy", str(source), str(target)])
        assert "is not writable" in result.output

    def test_invalid_offset(self, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        result = invoke(["copy", "--offset", "bogus", str(source), str(target)])
        assert result.exit_code == 2
        assert "Invalid offset" in result.output

    @patch("reorder.cli.copy_images")
    def test_valid_target_exists(self, copy_images, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.mkdir()
        result = invoke(["copy", str(source), str(target)])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(source, target, offsets={})

    @patch("reorder.cli.copy_images")
    def test_valid_target_does_not_exist(self, copy_images, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        result = invoke(["copy", str(source), str(target)])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(source, target, offsets={})
        assert target.is_dir()  # make sure it was created

    @patch("reorder.cli.copy_images")
    def test_valid_offset_one(self, copy_images, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.mkdir()
        result = invoke(["copy", "--offset", "PowerShot A70=+06:55", str(source), str(target)])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(
            source,
            target,
            offsets={"PowerShot A70": timedelta(hours=6, minutes=55)},
        )

    @patch("reorder.cli.copy_images")
    def test_valid_offset_multiple(self, copy_images, working_dir):
        source = working_dir / "source"
        target = working_dir / "target"
        source.mkdir()
        target.mkdir()
        result = invoke(["copy", "--offset", "a=+06:55", "-o", "b=-00:03", str(source), str(target)])
        assert result.exit_code == 0
        copy_images.assert_called_once_with(
            source,
            target,
            offsets={
                "a": timedelta(hours=6, minutes=55),
                "b": timedelta(minutes=-3),
            },
        )
