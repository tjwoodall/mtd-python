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

from typing import NoReturn
import sys
import json

from typeguard import typechecked

from .JSONTypes import JSONType
from . import SpecialTypes

# {{{ jd
@typechecked
def jd(data:JSONType|SpecialTypes.MissingData|SpecialTypes.UseDefault) -> None:
  if isinstance(data, SpecialTypes.MissingData):
    print("MissingData()")
  elif isinstance(data, SpecialTypes.UseDefault):
    print("UseDefault()")
  else:
    print(json.dumps(data, indent=2))
# }}} jd

# {{{ fatal
@typechecked
def fatal(err:str, obj:JSONType) -> NoReturn:
  sys.stdout.flush()
  print("-------- FATAL --------")
  jd(obj)
  print("-----------------------")
  print(err)
  raise RuntimeError(err)
# }}} fatal

# vim: set sw=2 sts=2 ts=2 expandtab:
