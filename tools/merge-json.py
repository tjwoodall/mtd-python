#!/usr/bin/env -S python3 -O

# typechecked is painfully slow! Remove -O to enable

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

import sys
import json
from pathlib import Path

from typeguard import typechecked
from mtd.JSONTypes import JSONType, JSONDict

all_data:JSONDict = {}

# {{{
@typechecked
def merge_minor(src:JSONDict, dst:JSONDict) -> None:
  for k,v in src.items():
    dst[k] = v
# }}}

# {{{
@typechecked
def merge_major(src:JSONDict, dst:JSONDict) -> None:
  for k,v in src.items():
    if k in dst:
      merge_minor(v, dst[k])
    else:
      dst[k] = v
# }}}

# {{{
@typechecked
def merge_api(src:JSONDict, dst:JSONDict) -> None:
  for k,v in src.items():
    if k in dst:
      merge_major(v, dst[k])
    else:
      dst[k] = v
# }}}

# This is a bit of a cheat, extraconfig and config never have overlapping primary keys so it "just works"
for filename in sys.argv[2:]:
  if Path(filename).exists():
    with open(filename, "r", encoding="utf-8") as f:
      data = json.load(f)
      merge_api(data, all_data)

def sort_keys(obj:JSONType, depth:int) -> JSONType:
  if depth == 0 or not isinstance(obj,dict):
    return obj  # stop sorting deeper
  return { k: sort_keys(v, depth - 1) for k, v in sorted(obj.items(), key=lambda x: x[0]) }

with open(sys.argv[1], 'w', encoding="utf-8") as out:
  out.write(json.dumps(sort_keys(all_data,3), indent=2) + "\n")

# vim: set sw=2 sts=2 ts=2 expandtab:
