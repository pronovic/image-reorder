# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

from typing import List
from unittest.mock import patch

from click.testing import CliRunner, Result

from reorder.cli import reorder as command


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


class TestGo:
    def test_h(self):
        result = invoke(["go", "-h"])
        assert result.exit_code == 0

    def test_help(self):
        result = invoke(["go", "--help"])
        assert result.exit_code == 0

    def test_missing_source(self):
        result = invoke(["go"])
        assert result.exit_code == 2

    def test_missing_target(self):
        result = invoke(["go", "source"])
        assert result.exit_code == 2

    def test_valid(self):
        result = invoke(["go", "source", "target"])
        assert result.exit_code == 0

    def test_valid_offset_one(self):
        result = invoke(["go", "--offset", "PowerShot A70=+06:55", "source", "target"])
        assert result.exit_code == 0

    def test_valid_offset_multiple(self):
        result = invoke(["go", "--offset", "a=+00:00", "-o", "b=-00:00", "source", "target"])
        assert result.exit_code == 0

    def test_invalid_offset(self):
        result = invoke(["go", "--offset", "bogus", "source", "target"])
        assert result.exit_code == 2
        assert "Invalid offset" in result.output
