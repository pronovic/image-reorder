# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
from typing import List

import click


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
)
def go(source: str, target: str, offsets: List[str]) -> None:
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
