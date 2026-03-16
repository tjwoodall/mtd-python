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

from . import SelectData
from . import ObjectData
from . import ValueData
from .DataProtocols import DataProtocol
from .JSONTypes import JSONDict, JSONList, Jstr
from . import ErrorHandler
from . import ButtonAdd
from . import SpecialTypes
from . import SheetData
from . import SchemaHelper
from . import LibreOfficeHelper

# {{{ ArrayData
class ArrayData(DataProtocol):
  # {{{ __init__
  @typechecked
  def __makeDefaultValue(self, items:JSONList|JSONDict) -> SelectData.SelectData|ValueData.ValueData|ArrayData|ObjectData.ObjectData|None:
    if isinstance(items, list):
      return SelectData.SelectData(None, True, items, SpecialTypes.ResponseData(valtype="UseDefault"))
    if SchemaHelper.get_type(items) in {'string', 'number', 'boolean', 'integer'}:
      return ValueData.ValueData(None, True, items, SpecialTypes.ResponseData(valtype="UseDefault"))
    if SchemaHelper.get_type(items) == 'array':
      return ArrayData(None, True, items, SpecialTypes.ResponseData(valtype="UseDefault"))
    if SchemaHelper.get_type(items) == 'object':
      return ObjectData.ObjectData(None, True, items, SpecialTypes.ResponseData(valtype="UseDefault"))
    ErrorHandler.fatal(f"Don't know how to handle {SchemaHelper.get_type(items)}", {})

  @typechecked
  def __init__(self, name:str|None, required:bool, schema_:JSONDict|None, response:SpecialTypes.ResponseData):
    if response.valtype in ("MissingData", "UseDefault") and schema_ is None:
      ErrorHandler.fatal("ArrayData needs response or schema", {})

    schema:JSONDict = schema_ if schema_ else {"items": {"type":"anything"}}

#    print(f"ArrayData name={name} required={required} response={response} schema={json.dumps(schema, indent=2)}")

    self.schema = schema
    self.name = name
    self.required = required
    self.items:list[SelectData.SelectData|ValueData.ValueData|ArrayData|ObjectData.ObjectData] = [] # This is the list of data
    self.description = SchemaHelper.desc(schema) if schema else "None"
    self.hidden = False

    items = schema['items']

    if response.valtype == "MissingData":
      if self.required:
        raise SpecialTypes.SchemaValidationError(f"Missing ArrayData value '{self.name}'- need required value '{self.schema}'")
      self.hidden = True
      response = SpecialTypes.ResponseData(valtype="UseDefault")

    if response.valtype not in ("UseDefault", "array"):
      raise SpecialTypes.SchemaValidationError(f"Needed array but got {response.valtype}")

    lresponses = response.getlist() if response.valtype != "UseDefault" else [SpecialTypes.UseDefault()]

    if items == SchemaHelper.anythingSelect:
      self.title = 'list/anything'
      if response.valtype == "UseDefault":
        return
    if items == {"type":"anything"}:
      self.schema['items'] = copy.deepcopy(SchemaHelper.anythingSelect)
      self.title = 'list/anything'
      if response.valtype == "UseDefault":
        return

    for r in lresponses:
      if items is None:
        if isinstance(r, list):
          value:ArrayData|ObjectData.ObjectData|ValueData.ValueData|SelectData.SelectData = ArrayData(None, False, None, SpecialTypes.ResponseData(r))
          self.title = value.title
        elif isinstance(r, dict):
          value = ObjectData.ObjectData(None, False, None, SpecialTypes.ResponseData(r))
          self.title = value.title
        else:
          value = ValueData.ValueData(None, True, items, SpecialTypes.ResponseData(r))
          self.title = Jstr(schema, 'title') if 'title' in schema else 'NOTITLE'
      elif isinstance(items, list):
        value = SelectData.SelectData(None, True, items, SpecialTypes.ResponseData(r))
        self.title = value.title
      else:
        t = SchemaHelper.get_type(items)
        if t == "anything":
          if isinstance(r, list):
            t = "array"
          elif isinstance(r, dict):
            t = "object"
        if t == "anything":
          value = ValueData.ValueData(None, True, SchemaHelper.get_schema_for_value(r), SpecialTypes.ResponseData(r))
          self.title = Jstr(schema, 'title') if 'title' in schema else 'NOTITLE'
        elif t in {'string', 'number', 'boolean', 'integer'}:
          value = ValueData.ValueData(None, True, items, SpecialTypes.ResponseData(r))
          self.title = Jstr(schema, 'title') if 'title' in schema else 'NOTITLE'
        elif t == 'array':
          value = ArrayData(None, True, items, SpecialTypes.ResponseData(r))
          self.title = value.title
        elif t == 'object':
          value = ObjectData.ObjectData(None, True, items, SpecialTypes.ResponseData(r))
          self.title = value.title
        else:
          ErrorHandler.fatal(f"Don't know how to handle {t}", {})

      self.items.append(value)
  # }}} __init__

  # {{{ __repr__
  @typechecked
  def __repr__(self) -> str:
    r:str = f"ArrayData name='{self.name}':"
    for i,k in enumerate(self.items):
      r += f"\n {i} {k}"
    return r
  # }}} __repr__

  # {{{ render
  @typechecked
  def render(self, si:SheetData.SheetData, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, disableValidation:bool, prefix:str) -> int:
#    print(f"render ArrayData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 5, row, LibreOfficeHelper.CellData(self.description))
    if self.hidden:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}", f"AADD {self.name}", 3, row))
      return row+1

    # First row is the entire array - we can delete the entire array if its not required or we can add an array item at the beginning
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(f"{self.name}:[" if self.name is not None else ":["))
    if not self.required:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"DELETE:{prefix}", f"ADELETE {self.name}", 3, row))
    si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}:0", f"AADD {self.name}:[0]", 4, row))
    row += 1
    for idx,v in enumerate(self.items):
      LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(f"[{idx}]"))
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}:{idx+1}", f"AADD {self.name}:[{idx+1}]", 4, row))
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"DELETE:{prefix}:{idx}", f"ADELETE {self.name}:[{idx}]", 3, row))
      # Render the array item on third row
      row = v.render(si, sheet, row+1, disableValidation, f"{prefix}:{idx}")
    # End the array
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData("]"))
    row += 1
    return row

  @staticmethod
  @typechecked
  def get_row_range(sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
    level = 0
    for r in range(row, row+2000):
      s = sheet.getCellByPosition(0, r).String
      if s.endswith(':['): # handle nested array
        level += 1
      if s == ']':
        level -= 1
        if not level:
          return r+1
    ErrorHandler.fatal(f"Didn't find end of array between {row+1} and {row+2001}", {})
  # }}} render

  # {{{ recover
  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
#    print(f"recover ArrayData name '{self.name}' from {row+1}")
    cell = sheet.getCellByPosition(0, row)
    if cell.String == "":
      self.hidden = True
      return row+1
    if cell.String != (f"{self.name}:[" if self.name is not None else ":["):
      ErrorHandler.fatal(f"Recovering {cell.String} but we are {self.name}:[", {})
    endrow = self.get_row_range(sheet, row)
#    print(f"recover ArrayData name '{self.name}' from row {row+1} to {endrow+1}")
    self.hidden = False
    row += 1  # Skip the array header
    idx = 0

    while row < endrow:
      s = sheet.getCellByPosition(0, row).String
      if s in (']', ''):
        row += 1
        continue
      if s != f"[{idx}]":
        ErrorHandler.fatal(f"Expected [{idx}] but got '{s}'", {})
      row += 1
      if idx >= len(self.items):
        items = copy.deepcopy(self.schema['items'])
        if items == SchemaHelper.anythingSelect:
          s = sheet.getCellByPosition(0, row).String
          if s.endswith(':<'):
            pass
          elif s.endswith(':{'):
            items = copy.deepcopy(SchemaHelper.anythingObject)
          elif s.endswith(':['):
            items = copy.deepcopy(SchemaHelper.anythingList)
          else:
            items = SchemaHelper.get_schema_for_value(sheet.getCellByPosition(1, row).String)
        nv = self.__makeDefaultValue(items)
        if nv is None:
          ErrorHandler.fatal(f"Can't add to array", {})
        self.items.append(nv)
      e = LibreOfficeHelper.get_row_range(sheet, row)
      row = self.items[idx].recover(sheet, row)
      assert row == e
      idx += 1

    self.items[:] = self.items[:idx]

    return row
  # }}} recover

  # {{{ to_json
  @typechecked
  def to_json(self) -> JSONDict|JSONList|None:
    if self.hidden:
      return None
    data:JSONList = []
    for v in self.items:
      js = v.to_json()
      if js is not None:
        data.append(v.to_json())

    if self.name is not None:
      return { self.name: data }
    return data

  # }}} to_json

  # {{{ get_edit_keys
  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, target:int, prefix:str) -> tuple[int,list[str],LibreOfficeHelper.CellData]:
#    print(f"get_edit_keys ArrayData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    if self.hidden:
      return row+1, [], LibreOfficeHelper.CellData(None)

    row += 1
    for idx,v in enumerate(self.items):
      row,rval,cv = v.get_edit_keys(sheet, row+1, target, f"{prefix}:{idx}")
      if rval != []:
        return row,rval,cv
    row += 1
    return row,[],LibreOfficeHelper.CellData(None)
  # }}} get_edit_keys

  # {{{ _dispatch_v
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> None:
#    print(f"ArrayData::_dispatch_v({method}) {keys} {self.name}")
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
    if len(keys) == 2:
      if method == "delete":
        del self.items[int(keys[1])]
        return None
      if method == "add":
        v = self.__makeDefaultValue(self.schema['items'])
        if v is not None:
          self.items.insert(int(keys[1]), v)
        return None
    return getattr(self.items[int(keys[1])], method)(keys[2:]) # type: ignore[no-any-return]
  # }}} _dispatch_v

  # {{{ _dispatch_s
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["get"]) -> str | int | float | bool: ...
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["edit"]) -> None: ...
  @typechecked
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"ArrayData::_dispatch_s({method}) {keys} {self.name}")
    if len(keys) < 1:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if self.hidden:
      ErrorHandler.fatal("dispatch_s on hidden", {})
    if len(keys) == 1:
      return len(self.items)
    if len(keys) < 3:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    return getattr(self.items[int(keys[1])], method)(sheet, keys[2:]) # type: ignore[no-any-return]
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
# }}} class ArrayData

# vim: set sw=2 sts=2 ts=2 expandtab:
