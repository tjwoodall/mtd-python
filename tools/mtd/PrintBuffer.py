# Copyright (C) 2026 Tim Woodall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import io
import sys
from typing import Any

from typeguard import typechecked

# {{{
class _PrintBuffer(io.StringIO):
  __stdout = sys.stdout

  # {{{
  @typechecked
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
  # }}} __init__

  # {{{
  @staticmethod
  @typechecked
  def reset() -> None:
    sys.stdout = _PrintBuffer.__stdout
  # }}} reset

  # {{{
  @staticmethod
  @typechecked
  def getText() -> Any:
    assert isinstance(sys.stdout, io.StringIO), "getText called while stdout is not redirected"
    return sys.stdout.getvalue()
  # }}} getText
# }}} class _PrintBuffer

# vim: set sw=2 sts=2 ts=2 expandtab:
