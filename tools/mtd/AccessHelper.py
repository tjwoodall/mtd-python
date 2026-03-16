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

import json
import time

from typing import KeysView
from collections.abc import Generator

from typeguard import typechecked

from .JSONTypes import JSONType


# {{{
class AccessHelper:
  # {{{
  @typechecked
  def __init__(self, obj: JSONType) -> None:
    self.obj = obj
  # }}} __init__

  @typechecked
  def value(self) -> JSONType:
    return self.obj

  @typechecked
  def as_int(self) -> int:
    if not isinstance(self.obj, int):
      raise ValueError(f"Expected int, got {type(self.obj).__name__}")
    return self.obj

  @typechecked
  def as_str(self) -> str:
    if not isinstance(self.obj, str):
      raise ValueError(f"Expected str, got {type(self.obj).__name__}")
    return self.obj

  @typechecked
  def as_bool(self) -> bool:
    if not isinstance(self.obj, bool):
      raise ValueError(f"Expected bool, got {type(self.obj).__name__}")
    return self.obj

  @typechecked
  def is_none(self) -> bool:
    return self.obj is None

  @typechecked
  def len(self) -> int:
    assert isinstance(self.obj, (dict, list))
    return len(self.obj)

  # {{{
  def __eq__(self, obj: object) -> bool:
    raise TypeError("AccessHelper should not be equality compared")
  # }}} __eq__

  # {{{
  def __ne__(self, obj: object) -> bool:
    raise TypeError("AccessHelper should not be equality compared")
  # }}} __ne__

  # {{{
  @typechecked
  def getraw(self) -> JSONType:
    return self.obj
  # }}} getraw

  # {{{
  @typechecked
  def get_or_create(self, k: str, default: JSONType) -> AccessHelper:
    if not isinstance(self.obj, dict):
      raise RuntimeError("get_or_create expected a dict")
    if k not in self.obj:
      self.obj[k] = default
    return AccessHelper(self.obj[k])
  # }}} get_or_create

  # {{{
  @typechecked
  def get_or_default(self, k: str, default: JSONType) -> AccessHelper:
    if not isinstance(self.obj, dict):
      raise RuntimeError("get_or_default expected a dict")
    if k not in self.obj:
      return AccessHelper(default)
    return AccessHelper(self.obj[k])
  # }}} get_or_default

  # {{{
  @typechecked
  def get(self, k:str|int) -> AccessHelper:
    if isinstance(self.obj, dict) and isinstance(k,str):
      return AccessHelper(self.obj[k])
    if isinstance(self.obj, list) and isinstance(k,int):
      return AccessHelper(self.obj[k])
    raise RuntimeError("get expected a dict/str or list/int")
  # }}} get

  # {{{
  @typechecked
  def set(self, k: str, v: JSONType) -> None:
    if not isinstance(self.obj, dict):
      raise RuntimeError("set expected a dict")
    self.obj[k] = v
  # }}} set

  # {{{
  @typechecked
  def append(self, v: JSONType) -> None:
    if not isinstance(self.obj, list):
      raise RuntimeError("append expected a list")
    self.obj.append(v)
  # }}} append

  # {{{
  @typechecked
  def delete(self, k:str|int) -> None:
    if isinstance(self.obj, dict) and isinstance(k,str):
      del self.obj[k]
    if isinstance(self.obj, list) and isinstance(k,int):
      del self.obj[k]
    raise RuntimeError("get expected a dict/str or list/int")
  # }}} delete

  # {{{
  @typechecked
  def ts_get(self, key: str, t: int = 3600) -> None|str:
    if not isinstance(self.obj, dict):
      raise RuntimeError("ts_get expected a dict")
    if key not in self.obj:
      return None
    #Don't try to do this if it's 1970 :-)
    expire = self.get_or_default(f'_ts_{key}', default = 0).as_int() + t
    if int(time.time()) < expire:
      return self.get(key).as_str()
    return None
  # }}} ts_get

  # {{{
  @typechecked
  def ts_set(self, key : str, v: str) -> None:
    if not isinstance(self.obj, dict):
      raise RuntimeError("ts_set expected a dict")
    self.obj[f'_ts_{key}'] = int(time.time())
    self.obj[key] = v
  # }}} ts_set

  # {{{
  @typechecked
  def __iter__(self) -> Generator[AccessHelper,None,None]:
    if isinstance(self.obj, dict):
      for v in self.obj.values():
        yield AccessHelper(v)
    elif isinstance(self.obj, list):
      for v in self.obj:
        yield AccessHelper(v)
    else:
      raise RuntimeError("__iter__ expected a list of a dict")
  # }}} __iter__

  # {{{
  @typechecked
  def items(self) -> Generator[tuple[str,AccessHelper],None,None]:
    if not isinstance(self.obj, dict):
      raise RuntimeError("items expected a dict")
    for k, v in self.obj.items():
      yield k, AccessHelper(v)
  # }}} items

  # {{{
  @typechecked
  def keys(self) -> KeysView[str]:
    if not isinstance(self.obj, dict):
      raise RuntimeError("keys expected a dict")
    return self.obj.keys()
  # }}} keys

  # {{{
  @typechecked
  def values(self) -> Generator[AccessHelper,None,None]:
    yield from iter(self)
  # }}} values

  # {{{
  def __repr__(self) -> str:
    return f"AccessHelper({json.dumps(self.obj, indent=2)})"
  # }}} __repr__
# }}} class AccessHelper

# vim: set sw=2 sts=2 ts=2 expandtab:
