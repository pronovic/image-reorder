# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

"""
Utility functionality.
"""

from typing import Optional


def upper_case(value: Optional[str]) -> Optional[str]:
    if value is not None:
        return value.upper()
    else:
        return None
