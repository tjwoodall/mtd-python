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

from typing import Any, Protocol, cast

from typeguard import typechecked

from . import ErrorHandler
from . import DataProtocols
from . import ObjectData
from . import ArrayData
from . import SelectData
from .JSONTypes import castJstr, castJint, castJfloat, castJbool

try:
  from com.sun.star.table.CellContentType import TEXT, VALUE, FORMULA, EMPTY # pylint: disable=import-error
except ImportError:
  FORMULA=1
  VALUE=2
  TEXT=3
  EMPTY=4

# {{{ Protocols
class LibreOfficeODSCellProtection(Protocol):
  IsLocked:bool

class LibreOfficeODSCellValidation(Protocol):
  Type:str
  ShowErrorMessage:bool
  IgnoreBlankCells:bool
  def setFormula1(self, f:str) -> None: ...
  @property
  def Formula1(self) -> str: ...
  @Formula1.setter
  def Formula1(self, val:str) -> None: ...

class LibreOfficeODSPosition(Protocol):
  X:int
  Y:int

class LibreOfficeODSCell(Protocol):
  Validation:LibreOfficeODSCellValidation
  CellProtection:LibreOfficeODSCellProtection
  Position:LibreOfficeODSPosition

  def clearContents(self, val:int) -> None: ...

  @property
  def String(self) -> str: ...
  @String.setter
  def String(self, val:str) -> None: ...

  @property
  def Formula(self) -> str: ...
  @Formula.setter
  def Formula(self, val:str) -> None: ...

  @property
  def Value(self) -> float: ...
  @Value.setter
  def Value(self, val:float) -> None: ...

  @property
  def Type(self) -> int: ...

class LibreOfficeODSControl(Protocol):
  pass

class LibreOfficeODSEvents(Protocol):
  pass

class LibreOfficeODSEvent(Protocol):
  pass

class LibreOfficeODSModel(Protocol):
  pass

class LibreOfficeODSForm(Protocol):
  Count: int
  def insertByIndex(self, x:int, y:LibreOfficeODSModel) -> None: ...
  def revokeScriptEvents(self, index:int) -> None: ...
  def registerScriptEvent(self, index:int, e:LibreOfficeODSEvent) -> None: ...

class LibreOfficeODSForms(Protocol):
  Count: int
  def insertByName(self, x:str, y:LibreOfficeODSForm) -> None: ...
  def __getitem__(self, key:int) -> LibreOfficeODSForm: ...

class LibreOfficeODSDrawPage(Protocol):
  def getByIndex(self, idx:int) -> LibreOfficeODSControl: ...
  Forms: LibreOfficeODSForms
  def add(self, x:int) -> None: ...
  Count: int
  def remove(self, ctrl:LibreOfficeODSControl) -> None: ...

class LibreOfficeODSCount(Protocol):
  Count: int

class LibreOfficeODSRow(Protocol):
  Height: int

class LibreOfficeODSRows(Protocol):
  def getByIndex(self, idx:int) -> LibreOfficeODSRow: ...

class LibreOfficeODSSheet(Protocol):
  Name:str
  cells:list[list[LibreOfficeODSCell]]
  DrawPage: LibreOfficeODSDrawPage
  Events: LibreOfficeODSEvents
  buttons:list[tuple[str,str,int,int]]
  def getRows(self) -> LibreOfficeODSRows: ...
  @property
  def Rows(self) -> LibreOfficeODSCount: ...
  @property
  def Columns(self) -> LibreOfficeODSCount: ...
  def getColumns(self) -> "LibreOfficeODSColumns": ...
  def getCellRangeByPosition(self, minc:int, minr:int, maxc:int, maxr:int) -> "LibreOfficeODSCellRange": ...
  def getCellByPosition(self, col:int, row:int) -> LibreOfficeODSCell: ...
  def protect(self, pw:str) -> None: ...
  def unprotect(self, pw:str) -> None: ...

class LibreOfficeODSColumn(Protocol):
  sheet:LibreOfficeODSSheet
  idx: int
  Width: int
  OptimalWidth: bool

class LibreOfficeODSColumns(Protocol):
  sheet:LibreOfficeODSSheet
  def getByIndex(self, idx:int) -> LibreOfficeODSColumn: ...

class LibreOfficeODSCellRange(Protocol):
  sheet:LibreOfficeODSSheet
  minc:int
  minr:int
  maxc:int
  maxr:int
  def clearContents(self, flag:int) -> None: ...

class XScriptContext(Protocol):
  def getDocument(self) -> Any: ...
# }}} Protocols

# {{{ CellData
class CellData:
  @typechecked
  def __init__(self, v:str|float|int|bool|None):
    if v is None:
      self.Empty:bool = True
      self.Type = ""
      self.String:str = ""
      self.Value:float|int = 0
      self.Formula:str = ""
    elif isinstance(v, str):
      self.Empty = False
      self.Type = "string"
      self.String = v
      self.Value = 0
      self.Formula = self.String
    elif isinstance(v, bool):
      self.Empty = False
      self.Type = "boolean"
      self.String = "TRUE" if v else "FALSE"
      self.Value = 1 if v else 0
      self.Formula = self.String
    else:
      self.Empty = False
      self.Type = "integer" if isinstance(v, int) else "number"
      self.String = str(v)
      self.Value = v
      self.Formula = self.String

  @typechecked
  def __eq__(self, other:Any) -> bool:
    if not isinstance(other, CellData):
      return False
    return  self.Empty == other.Empty and self.String == other.String and self.Value == other.Value and self.Formula == other.Formula

  @typechecked
  def __repr__(self) -> str:
    return f"E={self.Empty} S={self.String} V={self.Value} F={self.Formula}"

  @typechecked
  def to_value(self) -> str|int|bool|float|None:
    if self.Empty:
      return None
    if self.Type == "string":
      return self.String
    if self.Type in ("integer", "number"):
      return self.Value
    if self.Type == "boolean":
      return bool(self.Value)
    ErrorHandler.fatal(f"Unknown {self.Type} in {str(self)}", {})

  @classmethod
  @typechecked
  def from_cell(cls, c:LibreOfficeODSCell, ctype:str) -> CellData:
    if c.Type == EMPTY:
      return cls(None)
    if c.Type == FORMULA:
      return cls(c.Formula)
    if c.Type == VALUE:
      if ctype == "integer":
        return cls(int(c.Value))
      if ctype == "number":
        return cls(float(c.Value))
      if ctype == "boolean":
        return cls(bool(c.Value))
    # c.Type == TEXT or ctype == "string"
    return cls(c.String)
# }}} CellData

# {{{ MOCKS
class MockODSCellProtection(LibreOfficeODSCellProtection):
  @typechecked
  def __init__(self) -> None:
    self.IsLocked:bool = True

class MockODSCellValidation(LibreOfficeODSCellValidation):
  @typechecked
  def __init__(self) -> None:
    self.Type:str = ""
    self.ShowErrorMessage:bool = False
    self.IgnoreBlankCells = False

  @property
  @typechecked
  def Formula1(self) -> str:
    return str()
  @Formula1.setter
  @typechecked
  def Formula1(self, val:str) -> None:
    pass
  @typechecked
  def setFormula1(self, f:str) -> None:
    pass

class MockODSPosition(LibreOfficeODSPosition):
  @typechecked
  def __init__(self) -> None:
    self.X:int = 0
    self.Y:int = 0

class MockODSCell(LibreOfficeODSCell):
  @typechecked
  def __init__(self) -> None:
    self.CellProtection = MockODSCellProtection()
    self.Validation = MockODSCellValidation()
    self.Position = MockODSPosition()
    self._String:str = ""
    self._Value:float = 0
    self._Formula:str = ""
    self._Type = EMPTY

  @typechecked
  def __repr__(self) -> str:
    return f"T={self._Type} S={self._String} V={self._Value} F={self.Formula}"

  @property
  @typechecked
  def String(self) -> str:
    return self._String
  @String.setter
  @typechecked
  def String(self, val:str) -> None:
    self._Type = TEXT
    self._String = val
    self._Formula = ""
    self._Value = 0

  @property
  @typechecked
  def Value(self) -> float:
    return self._Value
  @Value.setter
  @typechecked
  def Value(self, val:float) -> None:
    self._Type = VALUE
    self._String = str(val)
    self._Formula = ""
    self._Value = val

  @property
  @typechecked
  def Formula(self) -> str:
    return self._Formula
  @Formula.setter
  @typechecked
  def Formula(self, val:str) -> None:
    # TODO - String should be result of eval formula
    self._Type = FORMULA
    self._String = val
    self._Formula = val
    self._Value = 0

  @property
  @typechecked
  def Type(self) -> int:
    return self._Type

  @typechecked
  def clearContents(self, val:int) -> None:
    self._Type = EMPTY

class MockODSControl(LibreOfficeODSControl):
  pass

class MockODSDrawPage(LibreOfficeODSDrawPage):
  @typechecked
  def __init__(self) -> None:
    self.Count:int = 0
    self.Forms:MockODSForms = MockODSForms()

  @typechecked
  def getByIndex(self, idx:int) -> MockODSControl:
    return MockODSControl()

  @typechecked
  def remove(self, ctrl:LibreOfficeODSControl) -> None:
    pass

  @typechecked
  def add(self, x:int) -> None:
    pass

class MockODSCount(LibreOfficeODSCount):
  @typechecked
  def __init__(self, c:int):
    self.Count = c

class MockODSCellRange(LibreOfficeODSCellRange):
  @typechecked
  def __init__(self, sheet:MockODSSheet, minc:int, minr:int, maxc:int, maxr:int) -> None:
    self.sheet = sheet
    self.minc = minc
    self.minr = minr
    self.maxc = maxc
    self.maxr = maxr

  @typechecked
  def clearContents(self, flag:int) -> None:
    # The only way we call is to clear the entire sheet
    self.sheet.cells = []

class MockODSColumn(LibreOfficeODSColumn):
  @typechecked
  def __init__(self, sheet:MockODSSheet, idx:int) -> None:
    self.sheet = sheet
    self.idx = idx
    self.Width:int = 0
    self.OptimalWidth:bool = False

class MockODSRow(LibreOfficeODSRow):
  @typechecked
  def __init__(self, sheet:MockODSSheet, idx:int) -> None:
    self.sheet = sheet
    self.idx = idx
    self.Height:int = 0

class MockODSRows(LibreOfficeODSRows):
  @typechecked
  def __init__(self, sheet:MockODSSheet) -> None:
    self.sheet = sheet

  @typechecked
  def getByIndex(self, idx:int) -> MockODSRow:
    return MockODSRow(self.sheet, idx)

class MockODSColumns(LibreOfficeODSColumns):
  @typechecked
  def __init__(self, sheet:MockODSSheet) -> None:
    self.sheet = sheet

  @typechecked
  def getByIndex(self, idx:int) -> MockODSColumn:
    return MockODSColumn(self.sheet, idx)

class MockODSEvents(LibreOfficeODSEvents):
  pass

class MockODSSheet(LibreOfficeODSSheet):
  @typechecked
  def __init__(self, name:str) -> None:
    self.cells = []
    self.DrawPage = MockODSDrawPage()
    self.Events = MockODSEvents()
    self.buttons:list[tuple[str,str,int,int]] = []
    self.Name = name

  @typechecked
  def getRows(self) -> MockODSRows:
    return MockODSRows(self)

  @property
  @typechecked
  def Rows(self) -> MockODSCount:
    return MockODSCount(len(self.cells))

  @property
  @typechecked
  def Columns(self) -> MockODSCount:
    if not self.cells:
      return MockODSCount(0)
    return MockODSCount(max(len(x) for x in self.cells))

  @typechecked
  def getColumns(self) -> MockODSColumns:
    return MockODSColumns(self)

  @typechecked
  def getCellRangeByPosition(self, minc:int, minr:int, maxc:int, maxr:int) -> MockODSCellRange:
    return MockODSCellRange(self, minc, minr, maxc, maxr)

  @typechecked
  def getCellByPosition(self, col:int, row:int) -> MockODSCell:
    while len(self.cells) <= row:
      self.cells.append([])
    datarow = self.cells[row]
    while len(datarow) <= col:
      datarow.append(MockODSCell())
    return cast(MockODSCell, datarow[col])

  @typechecked
  def protect(self, pw:str) -> None:
    pass

  @typechecked
  def unprotect(self, pw:str) -> None:
    pass

  @typechecked
  def dumpAsText(self) -> None:
    cols = max(len(x) for x in self.cells) if self.cells else 0
    for x in self.cells:
      x.extend([MockODSCell()] * (cols - len(x)))

    width:list[int] = []

    for col in range(0, cols):
      width.append(max(len(x[col].String) for x in self.cells))

    row = 0
    for x in self.cells:
      print(f"{row+1:4d}", end=" ")
      row += 1

      for col in range(0, cols):
        print(f"| {x[col].String}{' '*(width[col]-len(x[col].String))}", end=" ")
      print("|")

    @typechecked
    def swap_quotes(s:str) -> str:
      return s.replace("'", "__SINGLE__").replace('"', "'").replace("__SINGLE__", '"')

    for idx,b in enumerate(self.buttons):
      print(f"{idx:4d} row={b[3]:4d} col={b[2]:4d} action={swap_quotes(str(DataProtocols.DataProtocol.splitPrefix(b[0])))}")

class MockODSForm(LibreOfficeODSForm):
  @typechecked
  def __init__(self) -> None:
    self.Count:int = 0

  @typechecked
  def insertByIndex(self, x:int, y:LibreOfficeODSModel) -> None:
    pass

  @typechecked
  def revokeScriptEvents(self, index:int) -> None:
    pass

  @typechecked
  def registerScriptEvent(self, index:int, e:LibreOfficeODSEvent) -> None:
    pass

class MockODSForms(LibreOfficeODSForms):
  @typechecked
  def __init__(self) -> None:
    self.Count:int = 0

  @typechecked
  def insertByName(self, x:str, y:LibreOfficeODSForm) -> None:
    pass

  @typechecked
  def __getitem__(self, key:int) -> MockODSForm:
    return MockODSForm()

class MockController:
  @typechecked
  def __init__(self) -> None:
    self.ActiveSheet = MockODSSheet("")

  def select(self, cell:MockODSCell) -> None:
    pass

class MockSheets:
  @typechecked
  def __init__(self) -> None:
    self.data:dict[str,MockODSSheet] = {}

  @typechecked
  def __len__(self) -> int:
    return len(self.data)

  @typechecked
  def getByName(self, name:str) -> MockODSSheet:
    return self.data[name]

  @typechecked
  def hasByName(self, name:str) -> bool:
    return name in self.data

  @typechecked
  def insertNewByName(self, name:str, pos:int) -> None:
    self.data[name] = MockODSSheet(name)

  @typechecked
  def removeByName(self, name:str) -> None:
    del self.data[name]

class MockDocument:
  @typechecked
  def __init__(self) -> None:
    self.Sheets = MockSheets()
    self.CurrentController = MockController()

  def getCurrentController(self) -> MockController:
    return self.CurrentController

class MockXScriptContext(XScriptContext):
  @typechecked
  def __init__(self) -> None:
    self.document = MockDocument()

  @typechecked
  def getDocument(self) -> Any:
    return self.document
# }}} MOCKS

# {{{ auto_resize_column
@typechecked
def auto_resize_column(sheet:LibreOfficeODSSheet, col:int, maxrow:int) -> None:
#  columns = sheet.Columns
#  col = columns.getByIndex(col)
#  width = col.Width
#  print("Starting width:", width)
#  col.OptimalWidth = True
#  width = col.Width
#  print("Optimal width:", width)

#  max_width = 500
#
#  for row in range(0, maxrow):
#    cell = sheet.getCellByPosition(col, row)
#    v = cell.String
#    w = len(v) * 250
#    max_width = max(w, max_width)
#
#  sheet.getColumns().getByIndex(col).Width = max_width
  if col == 2:
    sheet.getColumns().getByIndex(col).Width = 500
  else:
    sheet.getColumns().getByIndex(col).OptimalWidth = True
# }}} auto_resize_column

# {{{ set_cell_protection
@typechecked
def set_cell_protection(cell:LibreOfficeODSCell, protected:bool) -> None:
# N.B. The sheet must be unprotected to unprotect a cell
  protection = cell.CellProtection
  protection.IsLocked = protected
  cell.CellProtection = protection
# }}} set_cell_protection

# {{{
@typechecked
def dump_to_sheet_cell(sheet:LibreOfficeODSSheet, col:int, row:int, data:CellData, protected:bool = True) -> None:
  cell = sheet.getCellByPosition(col, row)

  set_cell_protection(cell, False)
  # cell.Formula = "= A1 + B1" - cell.Type == FORMULA, cell.String="<value>" cell.Value="<computed result>"
  # cell.Value = 42 - cell.Type == VALUE, cell.String="42", cell.Formula==""
  # cell.String = "Hello" - cell.Type == TEXT, cell.Value == 0, cell.Formula = ""
#  print(f"{data} at {row+1} {col}")
  if data.Empty:
    cell.clearContents(1023)
  else:
    if data.Formula != "":
      cell.Formula = data.Formula
    if data.Type == "string":
      cell.String = castJstr(data.to_value())
    elif data.Type == "integer":
      cell.Value = castJint(data.to_value())
    elif data.Type == "number":
      cell.Value = castJfloat(data.to_value())
    elif data.Type == "boolean":
      cell.Value = castJbool(data.to_value())
    else:
      ErrorHandler.fatal("Unhandled {data.Type}", {})
  set_cell_protection(cell, protected)
# }}} dump_to_sheet_cel

# {{{ get_row_range
@typechecked
def get_row_range(sheet:LibreOfficeODSSheet, row:int) -> int:
  s = sheet.getCellByPosition(0, row).String
  if s.endswith(':{'):
    return ObjectData.ObjectData.get_row_range(sheet, row)
  if s.endswith(':['):
    return ArrayData.ArrayData.get_row_range(sheet, row)
  if s.endswith(':<'):
    return SelectData.SelectData.get_row_range(sheet, row)
  return row+1
# }}} get_row_range

# {{{ add_control_to_sheet
@typechecked
def add_control_to_sheet(sheet:LibreOfficeODSSheet, name:str, label:str, col:int, row:int) -> None:
  raise RuntimeError("add_control_to_sheet not initialized")
# }}} add_control_to_sheet

# {{{ clear_entire_sheet
@typechecked
def clear_entire_sheet(sheet:LibreOfficeODSSheet) -> None:
  rows = sheet.Rows.Count
  cols = sheet.Columns.Count
  cells = sheet.getCellRangeByPosition(0, 0, cols-1, rows-1)
  cells.clearContents(1023)
# }}} clear_entire_sheet

# {{{ set_dropdown_from_list
@typechecked
def set_dropdown_from_list(cell:LibreOfficeODSCell, values:list[str]) -> None:
  validation = cell.Validation
  validation.Type = "LIST"
#  validation.Operator = "EQUAL"
  validation.setFormula1('"' + '";"'.join(values) + '"')
  validation.ShowErrorMessage = True
  validation.IgnoreBlankCells = False
  cell.Validation = validation
# }}} set_dropdown_from_list

# vim: set sw=2 sts=2 ts=2 expandtab:
