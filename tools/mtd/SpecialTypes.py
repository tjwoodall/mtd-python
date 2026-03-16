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

from typeguard import typechecked

from .JSONTypes import JSONType, JSONDict, JSONList, castJDict, castJList, castJstr, castJint, castJfloat, castJbool

from . import ErrorHandler

# {{{ MissingData
class MissingData:
  @typechecked
  def __repr__(self) -> str:
    return "MissingData()"
# }}} MissingData

# {{{ UseDefault
class UseDefault:
  @typechecked
  def __repr__(self) -> str:
    return "UseDefault()"
# }}} UseDefault

# {{{ SchemaValidationError
class SchemaValidationError(Exception):
  pass
# }}} SchemaValidationError

# {{{ ResponseData
class ResponseData:
  @typechecked
  def __init__(self, val:JSONType|MissingData|UseDefault = MissingData(), valtype:str = "guess"):
    if ( valtype == "guess" and isinstance(val, MissingData) ) or valtype == "MissingData":
      self.valtype = "MissingData"
      return
    if ( valtype == "guess" and isinstance(val, UseDefault) ) or valtype == "UseDefault":
      self.valtype = "UseDefault"
      return
    if ( valtype == "guess" and isinstance(val, dict) ) or valtype == "object":
      if isinstance(val, (MissingData, UseDefault)):
        val = {}
      self.valtype = "object"
      self.dictval = castJDict(val)
      return
    if ( valtype == "guess" and isinstance(val, list) ) or valtype == "array":
      if isinstance(val, (MissingData, UseDefault)):
        val = []
      self.valtype = "array"
      self.listval = castJList(val)
      return
    if ( valtype == "guess" and isinstance(val, str) ) or valtype == "string":
      if isinstance(val, (MissingData, UseDefault)):
        val = "string"
      self.valtype = "string"
      self.strval = castJstr(val)
      return
    if ( valtype == "guess" and isinstance(val, bool) ) or valtype == "boolean":
      if isinstance(val, (MissingData, UseDefault)):
        val = False
      self.valtype = "boolean"
      self.boolval = castJbool(val)
      return
    if ( valtype == "guess" and isinstance(val, int) ) or valtype == "integer":
      if isinstance(val, (MissingData, UseDefault)):
        val = 0
      self.valtype = "integer"
      self.intval = castJint(val)
      return
    if ( valtype == "guess" and isinstance(val, float) ) or valtype == "number":
      if isinstance(val, (MissingData, UseDefault)):
        val = 0.0
      self.valtype = "number"
      self.floatval = castJfloat(val)
      return
    if ( valtype == "guess" and val is None ) or valtype == "null":
      self.valtype = "null"
      return
    ErrorHandler.fatal(f"Unhandled {valtype} {val} in ResponseData", {})

  @typechecked
  def __repr__(self) -> str:
    r = "Unsupported"
    if self.valtype == "MissingData":
      r = f"{self.valtype}"
    if self.valtype == "object":
      r = f"{self.valtype} {self.dictval}"
    if self.valtype == "array":
      r = f"{self.valtype} {self.listval}"
    if self.valtype == "string":
      r = f"{self.valtype} {self.strval}"
    if self.valtype == "boolean":
      r = f"{self.valtype} {self.boolval}"
    if self.valtype == "integer":
      r = f"{self.valtype} {self.intval}"
    if self.valtype == "number":
      r = f"{self.valtype} {self.floatval}"
    if self.valtype == "UseDefault":
      r = f"{self.valtype}"
    if self.valtype == "null":
      r = f"{self.valtype}"
    return r

  @typechecked
  def compatibleType(self, ctype:str) -> bool:
    if self.valtype == ctype:
      return True
    if self.valtype == "integer" and ctype == "number":
      return True
    return False

  @typechecked
  def getstr(self) -> str:
    if self.valtype == "string":
      return self.strval
    ErrorHandler.fatal(f"Got {self.valtype} but needed string", {})

  @typechecked
  def getint(self) -> int:
    if self.valtype == "integer":
      return self.intval
    ErrorHandler.fatal(f"Got {self.valtype} but needed integer", {})

  @typechecked
  def getfloat(self) -> float:
    if self.valtype == "number":
      return self.floatval
    if self.valtype == "integer":
      return self.intval
    ErrorHandler.fatal(f"Got {self.valtype} but needed number", {})

  @typechecked
  def getbool(self) -> bool:
    if self.valtype == "boolean":
      return self.boolval
    ErrorHandler.fatal(f"Got {self.valtype} but needed boolean", {})

  @typechecked
  def getlist(self) -> JSONList:
    if self.valtype == "array":
      return self.listval
    ErrorHandler.fatal(f"Got {self.valtype} but needed array", {})

  @typechecked
  def getdict(self) -> JSONDict:
    if self.valtype == "object":
      return self.dictval
    ErrorHandler.fatal(f"Got {self.valtype} but needed object", {})

  @typechecked
  def get(self) -> JSONType|MissingData|UseDefault:
    if self.valtype == "MissingData":
      return MissingData()
    if self.valtype == "object":
      return self.dictval
    if self.valtype == "array":
      return self.listval
    if self.valtype == "string":
      return self.strval
    if self.valtype == "boolean":
      return self.boolval
    if self.valtype == "integer":
      return self.intval
    if self.valtype == "number":
      return self.floatval
    if self.valtype == "UseDefault":
      return UseDefault()
    ErrorHandler.fatal(f"Unhandled {self.valtype}", {})
# }}} ResponseData

# vim: set sw=2 sts=2 ts=2 expandtab:
