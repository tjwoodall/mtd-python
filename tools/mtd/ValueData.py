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

from typing import overload, Literal, Any
from datetime import datetime, timezone, timedelta

from typeguard import typechecked

from .JSONTypes import JSONDict, castJstr, castJint, castJfloat, castJbool

from . import SchemaHelper
from . import LibreOfficeHelper
from . import ButtonAdd
from . import SheetData
from . import ErrorHandler
from . import SpecialTypes
from . import DataProtocols
from . import GlobalVars

import json

# {{{ ValueData
class ValueData(DataProtocols.DataProtocol):
  # {{{ __init__
  @typechecked
  def __init__(self, name:str|None, required:bool, schema_:JSONDict|None, response:SpecialTypes.ResponseData):
#    print(f"ValueData name={name} required={required} response={response} schema={json.dumps(schema_)}")
    if schema_ is not None:
      schema:JSONDict = schema_
    else:
      schema = {"type":response.valtype}

    self.schema = schema
    self.name = name if name != "" else "_value"
    self.required = required
    self.allowed_values = schema['enum'] if 'enum' in schema else None
    self.description = SchemaHelper.desc(schema)
    t = SchemaHelper.get_type(schema)
    if t is None:
      ErrorHandler.fatal(f"Can't get type for ValueData", {})
    self.type = t
    self.hidden = False
    self.row = -1

    if self.allowed_values is None and self.type == "boolean":
      self.allowed_values = [ True, False ]

    if self.type == "null":
      self.allowed_values = [ None ]

    if self.type == "string":
      self.title = f"str/{name if name is not None else ''}"
    elif self.type == "integer":
      self.title = f"int/{name if name is not None else ''}"
    elif self.type == "number":
      self.title = f"float/{name if name is not None else ''}"
    elif self.type == "boolean":
      self.title = f"bool/{name if name is not None else ''}"
    elif self.type == "null":
      self.title = f"null/{name if name is not None else ''}"
    else:
      ErrorHandler.fatal(f"Unhandled type {self.type}", {})

    self.value = LibreOfficeHelper.CellData(None)

    if response.valtype not in {"MissingData", "UseDefault"}:
      if not response.compatibleType(self.type):
        raise SpecialTypes.SchemaValidationError(f"type mismatch in ValueData: got {response} but need {self.schema}")
      if self.type == "string":
        self.value = LibreOfficeHelper.CellData(response.getstr())
      if self.type == "integer":
        self.value = LibreOfficeHelper.CellData(response.getint())
      if self.type == "number":
        self.value = LibreOfficeHelper.CellData(response.getfloat())
      if self.type == "boolean":
        self.value = LibreOfficeHelper.CellData(response.getbool())
      if self.type == "null":
        self.value = LibreOfficeHelper.CellData(None)

      if self.allowed_values is not None and self.value.to_value() not in self.allowed_values:
        raise SpecialTypes.SchemaValidationError(f"Value mismatch: got {response} but need one from {self.allowed_values}")

      return

    if response.valtype == "MissingData":
      if self.required:
        raise SpecialTypes.SchemaValidationError(f"Missing ValueData value '{self.name}' - need required value '{self.schema}'")
      self.hidden = True

    if 'example' in schema:
      self.value = LibreOfficeHelper.CellData(schema['example'])
    elif self.allowed_values is not None:
      self.value = LibreOfficeHelper.CellData(self.allowed_values[0])
    elif self.type == "string":
      self.value = LibreOfficeHelper.CellData("string")
    elif self.type == "integer":
      self.value = LibreOfficeHelper.CellData(0)
    elif self.type == "number":
      self.value = LibreOfficeHelper.CellData(0.0)
    elif self.type == "boolean":
      self.value = LibreOfficeHelper.CellData(False)
  # }}} __init__

  # {{{ __repr__
  @typechecked
  def __repr__(self) -> str:
    return f"ValueData: name={self.name} value={self.value} type={self.type}"
  # }}} __repr__

  # {{{ render
  @typechecked
  def render(self, si:SheetData.SheetData, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, disableValidation:bool, prefix:str) -> int:
#    print(f"render ValueData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    self.row = row
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 5, row, LibreOfficeHelper.CellData(self.description))
    if self.hidden:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}", f"VADD {self.name}", 3, row))
      return row+1

    if not self.required:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"DELETE:{prefix}", f"VDELETE {self.name}", 3, row))

    if self.allowed_values is not None and len(self.allowed_values) > 1:
      cell = sheet.getCellByPosition(1, row)
      LibreOfficeHelper.set_dropdown_from_list(cell, [str(x) for x in self.allowed_values])

    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(self.name))
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, row, self.value, self.allowed_values is not None and len(self.allowed_values)==1)

    if self.allowed_values is None:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"EDIT:{prefix}:<{self.type}>", f"VEDIT {self.name}", 4, row))
#    elif len(self.allowed_values)>1:
    else:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"EDIT:{prefix}:{self.allowed_values}", f"VEDIT {self.name}", 4, row))

    return row+1
  # }}} render

  # {{{ recover
  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
#    print(f"recover ValueData name '{self.name}' {self.type} from {row+1} to {row+2}")
    cell = sheet.getCellByPosition(0, row)
    self.row = row
    if LibreOfficeHelper.CellData.from_cell(cell, "string") == LibreOfficeHelper.CellData(f""):
      self.hidden = True
      return row+1
    if LibreOfficeHelper.CellData.from_cell(cell, "string") != LibreOfficeHelper.CellData(self.name):
      ErrorHandler.fatal(f"Recovering {LibreOfficeHelper.CellData.from_cell(cell, 'string')} but we are {LibreOfficeHelper.CellData(self.name)} on row{row+1}", {})

    self.hidden = False
    cell = sheet.getCellByPosition(1, row)
    self.value = LibreOfficeHelper.CellData.from_cell(cell, str(self.type))

    return row + 1
  # }}} recover

  # {{{ to_json
  @typechecked
  def to_json(self) -> JSONDict|str|int|float|bool|None:
    if self.hidden:
      return None
    value = self.value.to_value()
    if self.name:
      return { self.name: value }
    return value
  # }}} to_json

  # {{{ get_edit_keys
  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, target:int, prefix:str) -> tuple[int,list[str],LibreOfficeHelper.CellData]:
#    print(f"get_edit_keys ValueData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    if target != row or self.hidden:
      return row+1,[],LibreOfficeHelper.CellData(None)
    cell = sheet.getCellByPosition(0, row)
    if LibreOfficeHelper.CellData.from_cell(cell, "string") != LibreOfficeHelper.CellData(self.name):
      ErrorHandler.fatal(f"Recovering {LibreOfficeHelper.CellData.from_cell(cell, 'string')} but we are {LibreOfficeHelper.CellData(self.name)}", {})
    cell = sheet.getCellByPosition(1, row)
    value = LibreOfficeHelper.CellData.from_cell(cell, str(self.type))
    l = self.splitPrefix(prefix)
    return row+1,l,value
  # }}} get_edit_keys

  # {{{ _dispatch_v
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> None:
#    print(f"ValueData::_dispatch_v({method}) {keys} {self.name}")
    if len(keys) != 1:
      ErrorHandler.fatal(f"Keys wrong {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if method == "delete":
      self.hidden = True
    elif method == "add":
      self.hidden = False
    else:
      ErrorHandler.fatal("f{keys} for {method} in ObjectData", {})
  # }}} _dispatch_v

  # {{{ delete
  @typechecked
  def delete(self, keys:list[str|int|bool|float]) -> None:
    self._dispatch_v(keys, "delete")
  # }}} delete

  # {{{ add
  @typechecked
  def add(self, keys:list[str|int|bool|float]) -> None:
    self._dispatch_v(keys, "add")
  # }}} add

  # {{{ get
  @typechecked
  def get(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> str|int|float|bool|None:
#    print(f"ValueData::get {keys} row={self.row}")
    if len(keys) in (1, 2):
      if keys[0] != str(self.name if self.name is not None else ""):
        ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
      if self.hidden:
        ErrorHandler.fatal("get on hidden", {})
      cell = sheet.getCellByPosition(1, self.row)
      value = LibreOfficeHelper.CellData.from_cell(cell, str(self.type))
      if len(keys) == 2:
        safe_globals:dict[str,Any] = {}
        safe_locals:dict[str,Any] = {"value": value.to_value(), "now": lambda secs=0: datetime.now(timezone.utc) + timedelta(seconds=secs), }
        rv = eval(castJstr(keys[1]), safe_globals, safe_locals)
        if not isinstance(rv, (str, int, float, bool)):
          ErrorHandler.fatal("Didn't get str, int float or bool from translation function", {})
        return rv
      return value.to_value()
    ErrorHandler.fatal(f"get called on ValueData with keys {keys}", {})
  # }}} get

  # {{{ edit
  @typechecked
  def edit(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> None:
#    print(f"ValueData::edit {sheet.Name if sheet is not None else 'NONE'}{keys} row={self.row}")
    if keys:
      if keys[0] != str(self.name if self.name is not None else ""):
        ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if len(keys) == 2:
      if self.type == "string":
        svalue:str|int|float|bool = castJstr(keys[1])
      elif self.type == "integer":
        svalue = castJint(keys[1])
      elif self.type == "number":
        svalue = castJfloat(keys[1])
      elif self.type == "boolean":
        svalue = castJbool(keys[1])
      else:
        ErrorHandler.fatal(f"Unhandled type {self.type}", {})
      value = LibreOfficeHelper.CellData(svalue)
      if self.allowed_values and svalue not in self.allowed_values:
        GlobalVars.GlobalVars.warnings.append(f"ValueData: setting {svalue} but expected one from {self.allowed_values}")
      LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, self.row, value, self.allowed_values is not None and len(self.allowed_values)==1)
      return
    ErrorHandler.fatal(f"edit called on ValueData with keys {keys}", {})
  # }}} edit
# }}} class ValueData

# vim: set sw=2 sts=2 ts=2 expandtab:
