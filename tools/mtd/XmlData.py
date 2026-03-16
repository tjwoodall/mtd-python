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
import xmltodict
from typing import overload, Literal

from typeguard import typechecked

from . import ArrayData
from . import SelectData
from . import ObjectData
from . import ValueData

from .DataProtocols import DataProtocol

from .JSONTypes import JSONType, JSONList, castJstr
from . import SpecialTypes
from . import ErrorHandler
from . import GlobalVars
from . import ButtonAdd
from . import SheetData
from . import SchemaHelper
from . import LibreOfficeHelper

# {{{ XmlData
class XmlData(DataProtocol):
  # {{{ __init__
  @typechecked
  def __init__(self, name:str|None, required:bool, schema:JSONList, response:SpecialTypes.ResponseData):
    #print(f"XmlData {name} {required} {json.dumps(schema)} {response}")
    self.schema = schema
    self.name = name
    self.required = required
    self.values:list[ArrayData.ArrayData|ObjectData.ObjectData|SelectData.SelectData|ValueData.ValueData] = []
    self.description = "SELECT"
    self.value:str|None = None
    self.hidden = False
    self.row = -1
    self.TJW_skip_recover = False

    if response.valtype == "MissingData":
      if self.required:
        raise SpecialTypes.SchemaValidationError(f"Missing XmlData value '{self.name}' - need required value '{self.schema}'")
      self.hidden = True
      response = SpecialTypes.ResponseData(valtype="UseDefault")

    for idx,v in enumerate(schema):
      saved_warnings = GlobalVars.GlobalVars.warnings
      GlobalVars.GlobalVars.warnings = []
      if isinstance(v, list):
        self.values.append(SelectData.SelectData(self.name, True, v, response))
      else:
        try:
          if 'properties' in v or ( 'type' in v and v['type'] == "object"):
            self.values.append(ObjectData.ObjectData(None, True, v, response))
          elif 'items' in v or ( 'type' in v and v['type'] == "array" ):
            self.values.append(ArrayData.ArrayData(None, True, v, response))
          else:
            self.values.append(ValueData.ValueData(None, True, v, response))
        except SpecialTypes.SchemaValidationError as e:
          GlobalVars.GlobalVars.warnings = saved_warnings
          GlobalVars.GlobalVars.warnings.append(f"WARNING dropped invalid schema '{SchemaHelper.title(v)}' for {e}")
          continue
      GlobalVars.GlobalVars.warnings = saved_warnings + GlobalVars.GlobalVars.warnings

      if self.values[-1].title == '':
        self.values[-1].title = f"{idx}"
      else:
        self.values[-1].title = f"{self.values[-1].title}-{idx}"

#      if self.value is None:
#        self.value = self.values[-1].title

    if not self.values:
      if GlobalVars.GlobalVars.warnings:
        ErrorHandler.jd({"warnings":GlobalVars.GlobalVars.warnings})
      raise SpecialTypes.SchemaValidationError("No alternatives validate")

    self.title:str = f"select 1 of {len(self.values)}"
  # }}} __init__

  # {{{ __repr__
  @typechecked
  def __repr__(self) -> str:
    r:str = f"XmlData name={self.name} value={self.value}:"
    for k in self.values:
      joinstr = "*" if k.title == self.value else " "
      r += f"\n{joinstr}XmlData {k.title}\n"
      r += "\n".join(joinstr + " " + line for line in f"{k}".splitlines())
    return r
  # }}} __repr__

  # {{{ render
  @typechecked
  def render(self, si:SheetData.SheetData, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, disableValidation:bool, prefix:str) -> int:
#    print(f"render XmlData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    self.row = row
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 5, row, LibreOfficeHelper.CellData(self.description))
    if self.hidden:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"ADD:{prefix}", f"SADD {self.name}", 3, row))
      return row + 1

    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(f"{self.name}:<" if self.name is not None else ":<"))
    if not self.required:
      si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"DELETE:{prefix}", f"SDELETE {self.name}", 3, row))
    row += 1

    cell = sheet.getCellByPosition(1, row)
    LibreOfficeHelper.set_cell_protection(cell, False)
    LibreOfficeHelper.set_dropdown_from_list(cell, [str(x.title) for x in self.values])
    if self.value not in {x.title for x in self.values}:
      self.value = self.values[0].title
    cell.String = self.value
    # We must save the value of the current sheet data for recover

    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(f"{self.value}"))

    si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"EDIT:{prefix}:{[x.title for x in self.values]}", f"SEDIT {self.name}", 4, row))
    for idx,val in enumerate(self.values):
      if val.title == self.value:
        if idx > 0:
          si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"SELECT:{prefix}:{self.values[idx-1].title}", f"SELECT {self.values[idx-1].title}", 3, row))
        elif idx+1 < len(self.values):
          si.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"SELECT:{prefix}:{self.values[idx+1].title}", f"SELECT {self.values[idx+1].title}", 3, row))
        break

    row += 1
    v = [x for x in self.values if x.title == self.value]
    row = v[0].render(si, sheet, row, disableValidation, f"{prefix}")
    LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, row, LibreOfficeHelper.CellData(">"))
    row += 1
    return row

  @staticmethod
  @typechecked
  def get_row_range(sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
    level = 0
    for r in range(row, row+2000):
      s = sheet.getCellByPosition(0, r).String
      if s.endswith(':<'): # nested select
        level += 1
      if s == '>':
        level -= 1
        if not level:
          return r+1
    ErrorHandler.fatal(f"Didn't find end of select between {row+1} and {row+2001}", {})
  # }}} render

  # {{{ recover
  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int) -> int:
#    print(f"recover XmlData name '{self.name}' from row {row+1}")
    self.row = row
    if self.TJW_skip_recover:
      self.TJW_skip_recover = False
      return self.get_row_range(sheet, row)
    cell = sheet.getCellByPosition(0, row)
    if cell.String == "":
      self.hidden = True
      return row+1
    if cell.String != (f"{self.name}:<" if self.name is not None else ":<"):
      ErrorHandler.fatal(f"Recovering {cell.String} but we are {self.name}:<", {})
    endrow = self.get_row_range(sheet, row)
#    print(f"recover XmlData name '{self.name}' from row {row+1} to {endrow+1}")
    row += 1
    cell0 = sheet.getCellByPosition(0, row)
    cell1 = sheet.getCellByPosition(1, row)
    row += 1

    if self.value is None:
      self.value = cell0.String
    elif cell0.String != cell1.String:
      self.value = cell1.String
      cell0.String = f"{self.value}"
      return endrow

#    print(f"Looking for {self.value} in {[x.title for x in self.values]}")
    vl = [x for x in self.values if x.title == self.value] + self.values

    # This is one of the most frustrating bits about the HMRC api other than
    # all the bugs. They've overloaded the messages, often on taxYear, but not
    # bothered to add a discriminator. That makes state management far more
    # difficult than it should be and, for example, requires request parsing
    # to remember what tax year the request was made for.
    first_response = None
    for v in vl:
      try:
        lastrow = v.recover(sheet, row)
        if lastrow+1 == endrow and first_response is None:
          first_response = v
      except SpecialTypes.SchemaValidationError:
        pass

      if first_response is not None:
        row = v.recover(sheet, row)
        self.value = v.title
        cell0.String = f"{self.value}"
        return row+1

    raise SpecialTypes.SchemaValidationError("Cannot recover on select")
  # }}} recover

  # {{{ to_json
  @typechecked
  def to_json(self) -> JSONType:
    if self.hidden:
      return None
#    print(f"Looking for {self.value} in {[x.title for x in self.values]}")
    v = [x for x in self.values if x.title == self.value]
    jsn = v[0].to_json()
    if isinstance(jsn, dict):
      if len(jsn.keys()) == 1:
        jsn = xmltodict.unparse(jsn)
    if self.name:
      return { self.name: jsn }
    return jsn
  # }}} to_json

  # {{{ get_edit_keys
  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, row:int, target:int, prefix:str) -> tuple[int,list[str],LibreOfficeHelper.CellData]:
#    print(f"get_edit_keys XmlData on row {row+1} name '{self.name}' prefix '{prefix}'")
    prefix = self.calcPrefix(prefix, self.name)
    if self.hidden:
      return row+1,[],LibreOfficeHelper.CellData(None)

    endrow = self.get_row_range(sheet, row)
    if endrow <= target:
      return endrow, [],LibreOfficeHelper.CellData(None)

    row += 1  # :<
    if target == row:
      cell = sheet.getCellByPosition(1, row)
      val:str|int|float|bool = cell.String
      l = self.splitPrefix(prefix)
      return row+1,l,LibreOfficeHelper.CellData(val)

    row += 1  # self.value
    v = [x for x in self.values if x.title == self.value]
    row,rval,cv = v[0].get_edit_keys(sheet, row, target, f"{prefix}")
    return endrow,rval,cv
  # }}} get_edit_keys

  # {{{ _dispatch_v
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"XmlData::_dispatch_v({method}) {keys} {self.name}")
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
        ErrorHandler.fatal("f{keys} for {method} in XmlData", {})
      return None
    if self.hidden:
      ErrorHandler.fatal("get on hidden", {})
#    print(f"Looking for {self.value} in {[x.title for x in self.values]}")
    v = [x for x in self.values if x.title == self.value]
    return getattr(v[0], method)(keys[1:]) # type: ignore[no-any-return]
  # }}} _dispatch_v

  # {{{ _dispatch_s
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["get"]) -> str | int | float | bool: ...
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["edit"]) -> None: ...
  @typechecked
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"XmlData::_dispatch_s({method) {keys} {self.name}")
    if len(keys) < 1:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if len(keys) == 1:
      if method == "get":
        cell = sheet.getCellByPosition(1, self.row+1)
        return cell.String
      ErrorHandler.fatal("f{keys} for {method} in XmlData", {})
    if self.hidden:
      ErrorHandler.fatal("dispatch_s on hidden", {})
#    print(f"Looking for {self.value} in {[x.title for x in self.values]}")
    if len(keys) == 2:
      if method == "edit":
        v = [itm for itm,x in enumerate(self.values) if x.title == f"{castJstr(keys[1])}"]
        if v:
          LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, self.row+1, LibreOfficeHelper.CellData(f"{castJstr(keys[1])}"), len(self.values)==1)
        else:
          # FIXME convert xml to json
          xdata = xmltodict.parse(f"{castJstr(keys[1])}")
          x = XmlData(self.name, self.required, self.schema, SpecialTypes.ResponseData(xdata))
          self.values = x.values
          self.value = x.value
          self.TJW_skip_recover = True
        return None
    v = [itm for itm,x in enumerate(self.values) if x.title == self.value]
    return getattr(self.values[v[0]], method)(sheet, keys[1:]) # type: ignore[no-any-return]
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
# }}} class XmlData

# vim: set sw=2 sts=2 ts=2 expandtab:
