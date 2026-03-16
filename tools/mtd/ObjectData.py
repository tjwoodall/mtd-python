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

import copy
from typing import overload, Literal

from typeguard import typechecked

from . import ArrayData
from . import SelectData
from . import ValueData

from .DataProtocols import DataProtocol

from .JSONTypes import JSONDict, castJDict, castJstr
from . import SpecialTypes
from . import ErrorHandler
from . import GlobalVars
from . import ButtonAdd
from . import SheetData
from . import SchemaHelper
from . import LibreOfficeHelper

import json
# {{{ ObjectData
class ObjectData(DataProtocol):
  # {{{ __init__
  @typechecked
  def __init__(self, name:str|None, required:bool, schema_:JSONDict|None, response:SpecialTypes.ResponseData):
    if response.valtype in ("MissingData", "UseDefault") and schema_ is None:
      ErrorHandler.fatal("ArrayData.ArrayData needs response or schema", {})

    schema:JSONDict = schema_ if schema_ else {}

#    print(f"ObjectData name={name} required={required} response={response} schema={json.dumps(schema, indent=2)}")
    self.schema = schema
    self.name = name
    self.required = required
    self.values:list[ArrayData.ArrayData|ObjectData|SelectData.SelectData|ValueData.ValueData] = []
    self.description = SchemaHelper.desc(schema)
    self.hidden = False
    self.title:str = SchemaHelper.title(schema)
    self.additionalProperties = True

    if response.valtype == "MissingData":
      if self.required:
        raise SpecialTypes.SchemaValidationError(f"Missing ObjectData value '{self.name}' - need required value '{self.schema}'")
      self.hidden = True
      response = SpecialTypes.ResponseData(valtype="UseDefault")

    r:set[str] = set(schema['required']) if 'required' in schema else set()

    @typechecked
    def getresp(key:str) -> SpecialTypes.ResponseData:
      if response.valtype in {"UseDefault", "MissingData"}:
        return response
      if response.valtype != "object":
        raise SpecialTypes.SchemaValidationError(f"Type mismatch, expected object but got {response}")
      if key not in response.getdict():
        return SpecialTypes.ResponseData()
      return SpecialTypes.ResponseData(response.getdict()[key])

    properties:set[str] = set()
    if 'properties' in schema:
      for k,v in schema['properties'].items():
        properties.add(k)
        resp = getresp(k)
        if isinstance(v, list):
          self.values.append(SelectData.SelectData(k, k in r, v, resp))
        elif SchemaHelper.get_type(v) in {'string', 'number', 'boolean', 'integer'}:
          self.values.append(ValueData.ValueData(k, k in r, v, resp))
        elif SchemaHelper.get_type(v) == 'array':
          self.values.append(ArrayData.ArrayData(k, k in r, v, resp))
        elif SchemaHelper.get_type(v) == 'object':
          self.values.append(ObjectData(k, k in r, v, resp))
        else:
          ErrorHandler.fatal(f"Don't know how to handle {SchemaHelper.get_type(v)}", v)
        r.discard(k)

    if r:
      raise SpecialTypes.SchemaValidationError(f"Missing required property {r}")

    if 'additionalProperties' in schema and schema["additionalProperties"] is False:
      if response.valtype not in {"MissingData", "UseDefault"}:
        if not properties >= set(response.getdict().keys()):
          raise SpecialTypes.SchemaValidationError(f"Unexpected properties {set(response.getdict().keys())-properties}")
      self.additionalProperties = False
      return

    if response.valtype in {"MissingData", "UseDefault"}:
      return

    s = schema['additionalProperties'] if 'additionalProperties' in schema and schema['additionalProperties'] is not True else None

    if response.valtype != "object":
      raise SpecialTypes.SchemaValidationError(f"Expected object but got {response.valtype}")
    for k in response.getdict():
      if k not in properties:
        resp = getresp(k)
        GlobalVars.GlobalVars.warnings.append(f"WARNING - Unexpected additionalProperties key={k}, value={resp}")
        if resp.valtype == "array":
          self.values.append(ArrayData.ArrayData(k, False, s, resp))
        elif resp.valtype == "object":
          self.values.append(ObjectData(k, False, s, resp))
        else:
          self.values.append(ValueData.ValueData(k, False, s, resp))
    return
  # }}} __init__

  # {{{ __repr__
  @typechecked
  def __repr__(self) -> str:
    r:str = f"ObjectData: name={self.name} hidden={self.hidden}"
    for k in self.values:
      r += "\n" + "\n".join("o " + line for line in f"{k}".splitlines())
    return r
  # }}} __repr__

  # {{{ render
  @typechecked
  def render(self, si:SheetData.SheetData, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, disableValidation:bool, prefix:str) -> int:
#    print(f"render ObjectData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 5, row, LibreOfficeHelper.CellData(self.description))
    if self.hidden:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}", f"OADD {self.name}", 3, row))
      return row+1

    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(f"{self.name}:{{" if self.name is not None else ":{"))
    if not self.required:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"DELETE:{prefix}", f"ODELETE {self.name}", 3, row))
    row += 1

    names=set()
    for d in self.values:
      names.add(d.name)
      row = d.render(si, sheet, row, disableValidation, f"{prefix}")

    if self.additionalProperties:
      idx = 0
      while f"additional-{idx}" in names:
        idx += 1
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}:additional-{idx}", f"Add optional property", 3, row))
      row += 1

    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData("}"))
    row += 1

    return row

  @staticmethod
  @typechecked
  def get_row_range(sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
    level = 0
    for r in range(row, row+2000):
      s = sheet.getCellByPosition(0, r).String
      if s.endswith(':{'): # nested object
        level += 1
      if s == '}':
        level -= 1
        if not level:
          return r+1
    ErrorHandler.fatal(f"Didn't find end of object between {row+1} and {row+2001}", {})
  # }}} render

  # {{{ recover
  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
#    print(f"recover ObjectData name '{self.name}' from row {row+1} values are {[d.name for d in self.values]}")
    cell = sheet.getCellByPosition(0, row)

    if cell.String == "":
      self.hidden = True
      return row
    if cell.String != (f"{self.name}:{{" if self.name is not None else ":{"):
      ErrorHandler.fatal(f"Recovering {cell.String} but we are {self.name}:{{", {})
    self.hidden = False
    endrow = self.get_row_range(sheet, row)
#    print(f"recover ObjectData name '{self.name}' from row {row+1} to {endrow+1}")
    row += 1

    names = {d.name for d in self.values}
    while row < endrow:
      s = sheet.getCellByPosition(0, row).String
      if s in ('}', ''):
        row += 1
        continue
      found = False
      for d in self.values:
        if d.name is None:
          ErrorHandler.fatal(f'object key is None {d}', {})
        if s == d.name or s[:-1] == d.name + ':':
          row = d.recover(sheet, row)
          found = True
          names.remove(d.name)  # discard doesn't require the value to exist
          break
      if not found:
        e = LibreOfficeHelper.get_row_range(sheet, row)
        if s.endswith(':<'):
          self.values.append(SelectData.SelectData(s.removesuffix(':<'), False, copy.deepcopy(SchemaHelper.anythingSelect), SpecialTypes.ResponseData(valtype="UseDefault")))
        elif s.endswith(':{'):
          self.values.append(ObjectData(s.removesuffix(':{'), False, copy.deepcopy(SchemaHelper.anythingObject), SpecialTypes.ResponseData(valtype="UseDefault")))
        elif s.endswith(':['):
          self.values.append(ArrayData.ArrayData(s.removesuffix(':['), False, copy.deepcopy(SchemaHelper.anythingList), SpecialTypes.ResponseData(valtype="UseDefault")))
        else:
          c = sheet.getCellByPosition(1, row).String
          self.values.append(ValueData.ValueData(s, False, SchemaHelper.get_schema_for_value(c), SpecialTypes.ResponseData(valtype="UseDefault")))
        row = self.values[-1].recover(sheet, row)
        assert e == row

    if names:
      for d in self.values:
        if d.name in names:
          d.hidden = True
#      print(f"Need to hide {names}", {})

    return row
  # }}} recover

  # {{{ to_json
  @typechecked
  def to_json(self) -> JSONDict|None:
    if self.hidden:
      return None

    data:JSONDict = {}
    for d in self.values:
      j = d.to_json()
      if j is not None:
        data.update(castJDict(j))

    if self.name:
      return { self.name: data }
    return data

  # }}} to_json

  # {{{ get_edit_keys
  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, target:int, prefix:str) -> tuple[int,list[str],LibreOfficeHelper.CellData]:
#    print(f"get_edit_keys ObjectData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    endrow = self.get_row_range(sheet, row)
    if endrow <= target:
      return endrow, [], LibreOfficeHelper.CellData(None)

    row += 1 # :{

    while row < endrow:
      s = sheet.getCellByPosition(0, row).String
      if s in ('}', ''):
        row += 1
        continue
      for d in self.values:
        if d.name is None:
          ErrorHandler.fatal(f'object key is None {d}', {})
        if s == d.name or s.startswith(d.name + ":"):
          row,rval,cv = d.get_edit_keys(sheet, row, target, prefix)
          if rval != []:
            return row,rval,cv
          break
    ErrorHandler.fatal(f"Failed to find {target} in get_edit_keys", {})
  # }}} get_edit_keys

  # {{{ _dispatch_v
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> None:
#    print(f"ObjectData::_dispatch_v({method}) {keys} {self.name}")
    if len(keys) < 1:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if len(keys) == 1:
      if method == "delete":
        self.hidden = True
      elif method == "add":
        self.hidden = False
      else:
        ErrorHandler.fatal("f{keys} for {method} in ObjectData", {})
      return None
    for d in self.values:
      if d.name == keys[1]:
        return getattr(d, method)(keys[1:]) # type: ignore[no-any-return]
    if len(keys) == 2 and method == "add":
      # This is add optionalParameter:
      self.values.append(SelectData.SelectData(castJstr(keys[1]), False, copy.deepcopy(SchemaHelper.anythingSelect), SpecialTypes.ResponseData(valtype="UseDefault")))
      return None
    raise RuntimeError(f"Invalid _dispatch_v({method}) action {keys} need {[x.name for x in self.values]}")
  # }}} _dispatch_v

  # {{{ _dispatch_s
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["get"]) -> str | int | float | bool: ...
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["edit"]) -> None: ...
  @typechecked
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"ObjectData::_dispatch_s({method}) {keys} {self.name}")
    if len(keys) < 1:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if self.hidden:
      ErrorHandler.fatal("dispatch_s on hidden", {})
    if len(keys) == 1:
      return len(self.values)
    for d in self.values:
      if d.name == keys[1]:
        return getattr(d, method)(sheet, keys[1:]) # type: ignore[no-any-return]
    raise RuntimeError(f"Invalid _dispatch_s({method}) action {keys} need {[x.name for x in self.values]}")
  # }}} _dispatch_s

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
  def get(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> str|int|float|bool:
    return self._dispatch_s(sheet, keys, "get")
  # }}} get

  # {{{ edit
  @typechecked
  def edit(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float]) -> None:
    self._dispatch_s(sheet, keys, "edit")
  # }}} edit
# }}} class ObjectData

# vim: set sw=2 sts=2 ts=2 expandtab:
