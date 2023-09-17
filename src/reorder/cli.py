# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
import re
from datetime import timedelta
from typing import Dict, Tuple

import click
from click import UsageError

_OFFSET_PATTERN = re.compile(r"(^)(.*)(=)([+-])([0-9][0-9])(:)([0-9][0-9])($)")


def _parse_offsets(offsets: Tuple[str]) -> Dict[str, timedelta]:
    """Parse offsets, returning a dict from camera model to timedelta."""
    parsed = {}
    for offset in offsets:
        result = _OFFSET_PATTERN.match(offset)
        if not result:
            raise UsageError("Invalid offset; use format 'PowerShot A70=+06:55'")
        model = result.group(2)
        plus_or_minus = result.group(4)
        hours = int(result.group(5))
        minutes = int(result.group(7))
        delta = timedelta(hours=hours, minutes=minutes)
        if plus_or_minus == "-":
            delta *= -1
        parsed[model] = delta
    return parsed


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="image-reorder", prog_name="reorder")
def reorder() -> None:
    """Reorder images from multiple cameras."""


@reorder.command()
@click.argument("source", metavar="<source-dir>")
def analyze(source: str) -> None:
    """
    Analyze images in a source directory.

    Finds all images in a source directory and generates some information
    about those images, including camera models and start/end dates.
    """


@reorder.command()
@click.argument("source", metavar="<source-dir>")
@click.argument("target", metavar="<target-dir>")
@click.option(
    "--offset",
    "-o",
    "offsets",
    metavar="<offset>",
    help="Time offset like 'PowerShot A70=+06:55'",
    multiple=True,
)
def go(source: str, target: str, offsets: Tuple[str]) -> None:
    """
    Reorder images in a source directory.

    Finds all images in a source directory and reorders them into a target
    directory by EXIF creation date.  The target folder will be created if
    it does not already exist.

    If the clocks on the cameras are not in sync, you may optionally
    provide a time offset by camera model.  The configured hours and
    minutes will be added to the the actual EXIF time. Use a format like
    "PowerShot A70=+06:55".  The `reorder analyze` command will show you
    all of the different camera models among your images.
    """
    parsed = _parse_offsets(offsets)
