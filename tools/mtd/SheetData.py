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

from typing import cast, overload, Literal

from typeguard import typechecked

from . import ValueData
from . import ObjectData
from . import ArrayData
from . import XmlData
from . import SelectData

from .DataProtocols import SheetDataProtocol

from .JSONTypes import JSONDict
from .SpecialTypes import ResponseData
from . import SpecialTypes
from . import LibreOfficeHelper
from . import SchemaHelper
from . import ErrorHandler
from . import GlobalVars
from . import ButtonAdd

# {{{ SheetData
class SheetData(SheetDataProtocol):
  # {{{ __init__
  @typechecked
  def __init__(self, schema:JSONDict, response:SpecialTypes.ResponseData, parameters:SpecialTypes.ResponseData):
#    print(f"SheetData schema={json.dumps(schema, indent=2)} response={response} parameters={parameters}")
    self.schema = schema
    self.control = ObjectData.ObjectData("_control", True, {"additionalProperties":False}, SpecialTypes.ResponseData(valtype="UseDefault"))
    self.parameters:ObjectData.ObjectData|None = None
    self.value: ArrayData.ArrayData|ObjectData.ObjectData|SelectData.SelectData|ValueData.ValueData|XmlData.XmlData|None = None
    self.name:str = ''
    self.title:str = ''
    self.output:str = schema['_control']['_output']
    self.button_controls:list[ButtonAdd.ButtonAdd] = []

    if '_schema' in schema:
      subschema = schema['_schema']
      if isinstance(subschema, list):
        if self.output == "xml":
          self.value = XmlData.XmlData(self.output, True, subschema, response)
        else:
          self.value = SelectData.SelectData(self.output, True, subschema, response)
        self.title = self.value.title
      elif subschema is not None:
        self.title = SchemaHelper.title(subschema)
        if 'properties' in subschema:
          self.value = ObjectData.ObjectData(self.output, True, subschema, response)
        elif 'items' in subschema:
          self.value = ArrayData.ArrayData(self.output, True, subschema, response)
        elif 'type' in subschema and subschema['type'] == "string":
          self.value = ValueData.ValueData(self.output, True, subschema, response)
        else:
          raise RuntimeError(f"Unhandled {subschema}")
      else:
        self.title = SchemaHelper.title(schema)
    else:
      ErrorHandler.fatal("Missing _schema in", schema)

    if self.title == '':
      self.title = f'{schema["_control"]["_api"]}-{schema["_control"]["_action"]}'

    if '_mainsheet' in schema:
      return

    @typechecked
    def has_param(n:str) -> bool:
      if self.parameters is None:
        return False
      for p in self.parameters.values:
        if p.name == n:
          return True
      return False

    need_user_auth = False

    # These are parameters that we need to do the submission via the Endpoint
    control = schema["_control"]
    self.control.values.append(ValueData.ValueData( '_api',    True, { 'enum': [ control['_api'] ],    'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    self.control.values.append(ValueData.ValueData( '_major',  True, { 'enum': [ control['_major'] ],  'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    self.control.values.append(ValueData.ValueData( '_minor',  True, { 'enum': [ control['_minor'] ],  'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    self.control.values.append(ValueData.ValueData( '_path',   True, { 'enum': [ control['_path'] ],   'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    self.control.values.append(ValueData.ValueData( '_action', True, { 'enum': [ control['_action'] ], 'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    if '_response' in schema["_control"]:
      self.control.values.append(ValueData.ValueData( '_response', True, { 'enum': [ control['_response'] ], 'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
      self.control.values.append(ValueData.ValueData( '_output', True, { 'enum': [ control['_output'] ], 'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
    else:
      need_user_auth = '_User-Restricted' in schema
      self.control.values.append(ValueData.ValueData( '_server',            True,  { 'enum': [ control['_server'] ], 'example': control['_server'], 'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
      self.control.values.append(ValueData.ValueData( '_output', True, { 'enum': [ control['_output'] ], 'type': 'string' }, SpecialTypes.ResponseData(valtype="UseDefault")))
      self.control.values.append(ValueData.ValueData( '_disableValidation', False, { 'description': 'Add this parameter to allow submission even if schema validation fails', 'example': True, 'type': 'boolean',}, SpecialTypes.ResponseData()))
      self.control.values[-1].hidden = True

    for p in schema['_parameters']:
      if (control['_api'], control['_major'], control['_minor'], control['_path']) == ("txm-fph-validator-api", "1", "0", "/test/fraud-prevention-headers/{api}/validation-feedback"):
        if 'allOf' in p['schema']:
          t = p['schema']['allOf']
          p['schema'] = t[0]
          for i in t:
            p['schema'].update(i)
      if p['name'] in schema:
        value = SpecialTypes.ResponseData(schema[p['name']])
      elif parameters.valtype in ("UseDefault", "MissingData"):
        value = parameters
      elif p['name'] in parameters.getdict():
        value = SpecialTypes.ResponseData(parameters.getdict()[p['name']])
      else:
        value = SpecialTypes.ResponseData(valtype="UseDefault")
      pdata = ValueData.ValueData(p['name'], 'required' in p and p['required'], p['schema'], value)
      if pdata.name == 'Gov-Test-Scenario' and control['_server'] != "Sandbox":
        continue
      if self.parameters is None:
        self.parameters = ObjectData.ObjectData("_parameters", True, {"additionalProperties":False}, SpecialTypes.ResponseData(valtype="UseDefault"))
      self.parameters.values.append(pdata)
      if pdata.name == 'Gov-Test-Scenario':
        pdata.allowed_values = schema['Gov-Test-Opts']
        pdata.hidden = True
      if pdata.name == 'arn' and control['_arn_default']:
        pdata.value = control['_arn_default']
      if parameters.valtype not in ("UseDefault", "MissingData"):
        pdata.hidden = False

    if '_response' in schema["_control"]:
      return

    if has_param('nino') or has_param('vrn'):
      self.control.values.append(ValueData.ValueData(
        'arn', False,
        {
          'type': "string",
          'description': 'Add this parameter with an appropriate ARN to submit as agent',
          'example': control['_arn_default'],
        }, SpecialTypes.ResponseData()))
      if control['_arn_default'] == "":
        self.control.values[-1].hidden = True

    if need_user_auth:
      self.control.values.append(ValueData.ValueData( '_username', True, { 'description': 'The user authorised to do the operation', 'example': 'username', 'type': 'string',}, SpecialTypes.ResponseData('username')))

    if control['_server'] != "Sandbox":
      return

    # This is needed for the authentication
    if control['_api'] == "agent-authorisation-api":
      if self.parameters is None:
        self.parameters = ObjectData.ObjectData("_parameters", True, {"additionalProperties":False}, SpecialTypes.ResponseData(valtype="UseDefault"))
      self.parameters.values.append(ValueData.ValueData("nino", False, {'type':'string'}, SpecialTypes.ResponseData(valtype="UseDefault")))


    self.control.values.append(ValueData.ValueData( 'automateBrowser', False, { 'description': 'Set this parameter to false to execute the sandbox authentication manually', 'example': False, 'type': 'boolean',}, SpecialTypes.ResponseData()))
    self.control.values[-1].hidden = True
    if need_user_auth:
      self.control.values.append(ValueData.ValueData( '_userId', False, { 'description': 'Add this parameter to pass a userId to automate browser', 'example': 'userId', 'type': 'string',}, SpecialTypes.ResponseData()))
      self.control.values[-1].hidden = True
      self.control.values.append(ValueData.ValueData( '_password', False, { 'description': 'Add this parameter to pass a password to automate browser', 'example': 'password', 'type': 'string',}, SpecialTypes.ResponseData()))
      self.control.values[-1].hidden = True
  # }}} __init__

  # {{{ __repr__
  @typechecked
  def __repr__(self) -> str:
    r:str = f"SheetData: name={self.name}"
    r += "\n" + "\n".join(" " + line for line in f"{self.control}".splitlines())
    r += "\n" + "\n".join(" " + line for line in f"{self.parameters}".splitlines())
    r += "\n" + "\n".join(" " + line for line in f"{self.value}".splitlines())
    for b in self.button_controls:
      r += f"\n  {b}"
    return r

  # }}} __repr__

  # {{{ render
  @typechecked
  def render(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> int:
    sheet.unprotect("") # No password

    draw_page = sheet.DrawPage
    cc = draw_page.Count

    for i in range(cc-1, -1, -1):
      ctrl = draw_page.getByIndex(i)
      draw_page.remove(ctrl)

    LibreOfficeHelper.clear_entire_sheet(sheet)
    self.button_controls.clear()

    if '_mainsheet' in self.schema:
      row = 0
    else:
      LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, 1, LibreOfficeHelper.CellData(self.title))
      row = 3

    disableValidation = False
    row = self.control.render(self, sheet, row, disableValidation, f"{sheet.Name}:")

    if self.parameters is not None:
      row = self.parameters.render(self, sheet, row+1, disableValidation, f"{sheet.Name}:")

    if self.value is not None:
      row = self.value.render(self, sheet, row+1, disableValidation, f"{sheet.Name}:")

    if '_mainsheet' not in self.schema:
      row = row+1
      self.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"SUBMIT:{sheet.Name}", "SUBMIT", 0, row+1))
      row = row+1
    else:
      row += 2
    #  sheet.dumpAsText()
      data:JSONDict = { "_control": { }
      }
      for v in cast(ObjectData.ObjectData, self.value).values:
        if isinstance(v, ValueData.ValueData):
          data["_control"][v.name] = v.value.to_value()
      si = SchemaHelper.getOutboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
      title = si.title
      self.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"GENSHEET:{title}", f"Generate {title}", 0, row))
      row = row+1
      self.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"LoadResponse", f"Load response", 0, row))
    #  LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, row, LibreOfficeHelper.CellData("Load a response into a new sheet"))
      row = row+1
      self.button_controls.append(ButtonAdd.ButtonAdd(sheet, f"Import", f"Import", 0, row))
    #  LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, row, LibreOfficeHelper.CellData("Import a file into the selected API for sending"))
      row = row+1

    for b in self.button_controls:
      if not GlobalVars.GlobalVars.editButtons and b.name.startswith("EDIT:"):
        continue
      if not GlobalVars.GlobalVars.selectButtons and b.name.startswith("SELECT:"):
        continue
      LibreOfficeHelper.dump_to_sheet_cell(sheet, b.col, b.row, LibreOfficeHelper.CellData(f"{b.label}"))

    LibreOfficeHelper.auto_resize_column(sheet, 0, row) # key
    LibreOfficeHelper.auto_resize_column(sheet, 1, row) # value
    LibreOfficeHelper.auto_resize_column(sheet, 2, row) # space
    LibreOfficeHelper.auto_resize_column(sheet, 3, row) # buttons
    LibreOfficeHelper.auto_resize_column(sheet, 4, row) # buttons
    LibreOfficeHelper.auto_resize_column(sheet, 5, row) # notes

    for b in self.button_controls:
      if not GlobalVars.GlobalVars.editButtons and b.name.startswith("EDIT:"):
        continue
      if not GlobalVars.GlobalVars.selectButtons and b.name.startswith("SELECT:"):
        continue
      LibreOfficeHelper.add_control_to_sheet(sheet, b.name, b.label, b.col, b.row)

    sheet.protect("") # No password

    return row
  # }}} render

  # {{{ recover
  @typechecked
  def recover(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> None:
    if '_mainsheet' in self.schema:
      row = 0
    else:
      row = 3

#    print(f"recover SheettData name '{self.name}' from row {row+1}")
    row = self.control.recover(sheet, row)
    row += 1
    # FIXME - do we need to check if this is parameters?
    if self.parameters is not None:
      row = self.parameters.recover(sheet, row)
      row += 1
#    print(f"recover SheetData from {row+1}")
    if self.value is not None:
      row = self.value.recover(sheet, row)
  # }}} recover

  # {{{ to_json
  @typechecked
  def to_json(self) -> JSONDict:
    data:JSONDict = {
      "_data": {},
      "_parameters": {},
      "_control": {},
      "_output": self.output
    }
    js = self.control.to_json()
    if js is not None:
      data.update(js)
    if self.parameters is not None:
      js = self.parameters.to_json()
      if js is not None:
        data.update(js)
    if self.value is not None:
      data['_data'] = self.value.to_json()
    else:
      data['_data'] = None
    return data
  # }}} to_json

  # {{{ get_edit_keys
  @typechecked
  def get_edit_keys(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, target:int) -> list[str|int|float|bool|None]:
    if '_mainsheet' in self.schema:
      row = 0
    else:
      row = 3

    row,rval,cv = self.control.get_edit_keys(sheet, row, target, "")
    if rval != []:
      return [*rval,cv.to_value()]

    if self.parameters is not None:
      row,rval,cv = self.parameters.get_edit_keys(sheet, row+1, target, "")
      if rval != []:
        return [*rval,cv.to_value()]

    if self.value is not None:
      row,rval,cv = self.value.get_edit_keys(sheet, row+1, target, "")
      if rval != []:
        return [*rval,cv.to_value()]

    return []
  # }}} get_edit_keys

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

  # {{{ _dispatch_v
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["delete"]) -> None: ...
  @overload
  def _dispatch_v(self, keys:list[str|int|bool|float], method: Literal["add"]) -> None: ...
  @typechecked
  def _dispatch_v(self, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"SheetData::_dispatch_v({method}) {keys} {self.name}")
    if len(keys)< 2:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if keys[1] == "_control":
      return getattr(self.control, method)(keys[1:])  # type: ignore[no-any-return]
    if keys[1] == "_parameters":
      if self.parameters is None:
        ErrorHandler.fatal(f"{keys} but no parameters", {})
      return getattr(self.parameters, method)(keys[1:]) # type: ignore[no-any-return]
    if self.value is None:
      ErrorHandler.fatal(f"{self.value} is None", {})
    return getattr(self.value, method)(keys[1:])  # type: ignore[no-any-return]
  # }}} _dispatch

  # {{{ _dispatch_s
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["get"]) -> str | int | float | bool: ...
  @overload
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method: Literal["edit"]) -> None: ...
  @typechecked
  def _dispatch_s(self, sheet:LibreOfficeHelper.LibreOfficeODSSheet, keys:list[str|int|bool|float], method:str) -> str|int|float|bool|None:
#    print(f"SheetData::_dispatch_s({method}) {keys} {self.name}")
    if len(keys)< 2:
      ErrorHandler.fatal(f"Keys too short {keys}", {})
    if keys[0] != str(self.name if self.name is not None else ""):
      ErrorHandler.fatal(f"{keys[0]} != {self.name}", {})
    if keys[1] == "_control":
      return getattr(self.control, method)(sheet, keys[1:]) # type: ignore[no-any-return]
    if keys[1] == "_parameters":
      if self.parameters is None:
        ErrorHandler.fatal(f"{keys} but no parameters", {})
      return getattr(self.parameters, method)(sheet, keys[1:])  # type: ignore[no-any-return]
    if self.value is None:
      ErrorHandler.fatal(f"{self.value} is None", {})
    return getattr(self.value, method)(sheet, keys[1:]) # type: ignore[no-any-return]
  # }}} _dispatch

# }}} class SheetData

# vim: set sw=2 sts=2 ts=2 expandtab:
