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

import re
from typing import Protocol, overload, Literal

from typeguard import typechecked

from .JSONTypes import JSONType, JSONDict
from . import SpecialTypes
from . import LibreOfficeHelper
from . import SheetData

# {{{ DataProtocolBase
class DataProtocolBase(Protocol):
  @typechecked
  def __init__(self, schema:JSONDict, response:SpecialTypes.ResponseData, parameters:SpecialTypes.ResponseData) -> None: ...

  @typechecked
  def __repr__(self) -> str: ...

  @typechecked
  def to_json(self) -> JSONType: ...

  @typechecked
  def delete(self, keys:list[str|int|bool|float]) -> None: ...

  @typechecked
  def add(self, keys:list[str|int|bool|float]) -> None: ...

  @typechecked
  def get(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> str|int|float|bool|None: ...

  @typechecked
  def edit(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> None: ...

  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None: ...

  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["get"]) -> str | int | float | bool: ...
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["edit"]) -> None: ...
  @typechecked
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None: ...


# }}} class DataProtocolBase

# {{{ DataProtocol
class DataProtocol(DataProtocolBase, Protocol):
  @typechecked
  def calcPrefix(self, prefix:str, name:str|None) -> str:
    name=name.replace(':','\\:') if name is not None else ''
    return f"{prefix}:{name}"

  @staticmethod
  @typechecked
  def splitPrefix(s:str) -> list[str]:
    parts = re.split(r'(?<!\\):', s)
    parts = [p.replace(r'\:', ':') for p in parts]
    return parts

  @typechecked
  def render(self, si:SheetData.SheetData, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, disableValidation:bool, prefix:str) -> int: ...

  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int: ...

  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, target:int, prefix:str) -> tuple[int,list[str],LibreOfficeHelper.CellData]: ...
# }}} class DataProtocol

# {{{ SheetDataProtocol
class SheetDataProtocol(DataProtocolBase, Protocol):
  @typechecked
  def render(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> int: ...

  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> None: ...

  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, target:int) -> list[str|int|float|bool|None]: ...
# }}} class SheetDataProtocol

# vim: set sw=2 sts=2 ts=2 expandtab:
