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

from typeguard import typechecked

from . import LibreOfficeHelper

# {{{ ButtonAdd
class ButtonAdd:
  @typechecked
  def __init__(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, name:str, label:str, col:int, row:int):
    self.name = f"{name}"
    self.label = label
    self.col = col
    self.row = row

  def __repr__(self) -> str:
    return f"ButtonAdd name={self.name} label={self.label} row={self.row} col={self.col}"

# }}} ButtonAdd

# vim: set sw=2 sts=2 ts=2 expandtab:
