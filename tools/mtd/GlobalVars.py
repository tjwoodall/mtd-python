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

from . import SheetData

# {{{ GlobalVars
class GlobalVars:
  warnings: list[str] = []
  copyval: int|str|bool|float = 0
  editButtons: bool = True
  selectButtons: bool = False
  sheet_info:dict[str,SheetData.SheetData] = {}

  # Used for partitioning test-*-renderer.py for Makefile performance
  partition:int = 0
  partitions:int = 1
  @staticmethod
  def in_partition(i: int) -> bool:
    return i % GlobalVars.partitions == GlobalVars.partition

# }}} class GlobalVars

# vim: set sw=2 sts=2 ts=2 expandtab:
