#!/usr/bin/env -S python3 -O

# typechecked is painfully slow! Remove -O to enable

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

import os
import copy
import hashlib # pylint: disable=unused-import
import json
import uuid
import sys
import re
from typing import Any, cast

from typeguard import typechecked

# MTD imports
from mtd.Endpoint import Endpoint
from mtd.Config import Config
from mtd.AccessHelper import AccessHelper
from mtd.SheetData import SheetData
from mtd.DataProtocols import DataProtocol
from mtd.SpecialTypes import ResponseData
from mtd.GlobalVars import GlobalVars
from mtd.ErrorHandler import jd, fatal
from mtd import SchemaHelper
from mtd import LibreOfficeHelper
from mtd.JSONTypes import JSONDict, castJDict, castJstr

from mtd.LibreOfficeHelper import MockXScriptContext
XSCRIPTCONTEXT = MockXScriptContext()

GlobalVars.selectButtons = False
GlobalVars.editButtons = True

# The name of the sheet everything else is driven from.
# This must have an on-sheet-changed event manually added in
# Sheet | Sheet-Events | Content changed
#   libreoffice|sheet-changed.py$on_sheet_change
# Everything else should "just work" from that point
MAINSheet = "MAIN"

# Contains the list of NINOS that we support
NINOSheet = "NINOS"

# {{{ GetAPI
class GetAPI:
  API: JSONDict
  @typechecked
  def __call__(self, filename:str="") -> JSONDict:
    if not hasattr(GetAPI, "API"):
      with open(filename, "r", encoding="utf-8") as f:
        GetAPI.API = castJDict(json.load(f))
    return GetAPI.API
# }}} GetAPI

SchemaHelper.getAPI = GetAPI()

# {{{ GetConfig
class GetConfig:
  _config: Config
  @typechecked
  def __call__(self, filename:str="") -> Config:
    if not hasattr(GetConfig, "_config"):
      GetConfig._config = Config(filename)
    return GetConfig._config
# }}} GetConfig

getConfig = GetConfig()

# row is the row that has the api on it.
# {{{ getAPIKeys
@typechecked
def getAPIKeys(sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> JSONDict:
  api = SchemaHelper.getAPI()

  row = 0
  while row < 10:
    cell = sheet.getCellByPosition(0, row)
    if cell.String == '_api':
      break
    row += 1

  cell = sheet.getCellByPosition(0, row)
  if cell.String != '_api':
    fatal(f"Didn't find _api on {sheet.Name}", {})

  # _api
  cell = sheet.getCellByPosition(1, row)
  if cell.String not in api:
    raise RuntimeError(f"Invalid api {cell.String}")
  api_key = cell.String
  api = api[api_key]
  row += 1

  # _major
  cell = sheet.getCellByPosition(1, row)
  if cell.String not in api:
    raise RuntimeError(f"Invalid major {cell.String}")
  major_key = cell.String
  api = api[major_key]
  row += 1

  # _minor
  cell = sheet.getCellByPosition(1, row)
  if cell.String not in api:
    raise RuntimeError(f"Invalid minor {cell.String}")
  minor_key = cell.String
  api = api[minor_key]
  row += 1

  servers = []
  for s in api["servers"]:
    if 'description' in s:
      servers.append(s['description'])
    else:
      servers.append("Sandbox" if "test-api" in s['url'] else "Production")

  api = api["paths"]

  # _path
  cell = sheet.getCellByPosition(1, row)
  if cell.String not in api:
    raise RuntimeError(f"Invalid endpoint {cell.String}")
  ep_key = cell.String
  api = api[ep_key]
  row += 1

  # _action
  cell = sheet.getCellByPosition(1, row)
  if cell.String not in api:
    raise RuntimeError(f"Invalid action {cell.String}")
  action_key = cell.String
  api = api[action_key]
  row += 1

  data:JSONDict = {
    "_control": {
      "_api": api_key,
      "_major": major_key,
      "_minor": minor_key,
      "_path": ep_key,
      "_action": action_key,
      "_parameters": [],
    }
  }

  cell = sheet.getCellByPosition(0, row)
  if cell.String == "_response":
    # _response
    api = api['responses']
    cell = sheet.getCellByPosition(1, row)
    if cell.String not in api:
      raise RuntimeError(f"Invalid response {cell.String}")
    data['_control']['_response'] = cell.String
    row += 1

    cell = sheet.getCellByPosition(1, row)
    data['_control']['_output'] = cell.String
    row += 1
  else:
    # _server
    cell = sheet.getCellByPosition(1, row)
    if cell.String not in servers:
      raise RuntimeError(f"Invalid server {cell.String}")
    data['_control']['_server'] = cell.String
    row += 1

#    # _arn_default!?
#    cell = sheet.getCellByPosition(1, row)
#    arn_default = ""
#    if cell.String != "":
#      arn_default = cell.String
#    data['_control']['_arn_default'] = arn_default
#    row += 1

  return data
# }}} getAPIKeys

# {{{ add_control_to_sheet
@typechecked
def add_control_to_sheet(sheet:LibreOfficeHelper.LibreOfficeODSSheet, name:str, label:str, col:int, row:int) -> None:
  sheet.buttons.append((name, label, col, row))
# }}} add_control_to_sheet

LibreOfficeHelper.add_control_to_sheet = add_control_to_sheet

# This is the outbound sheet callback.
# {{{ sheet_changed_callback
@typechecked
def sheet_changed_callback(event:Any) -> None:
#  print(f"Column is {event.CellAddress.Column}")
#  print(f"Row is {event.CellAddress.Row}")

  doc = XSCRIPTCONTEXT.getDocument()
  sheet = doc.CurrentController.ActiveSheet

  if sheet.Name not in GlobalVars.sheet_info:
    data = getAPIKeys(sheet)
    if '_response' in data['_control']:
      si = SchemaHelper.getInboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
    else:
      si = SchemaHelper.getOutboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
    GlobalVars.sheet_info[sheet.Name] = si
    si.recover(sheet)
  else:
    si = GlobalVars.sheet_info[sheet.Name]

  @typechecked
  def swap_quotes(s:str) -> str:
    return s.replace("'", "__SINGLE__").replace('"', "'").replace("__SINGLE__", '"')
  if not isinstance(event, EventDuck):
    cell = sheet.getCellByPosition(event.CellAddress.Column, event.CellAddress.Row)
    doc.CurrentController.ActiveSheet = sheet
    doc.CurrentController.select(cell)
    btn = ["EDIT", sheet.Name] + si.get_edit_keys(sheet, event.CellAddress.Row)
    print(f'Sheet "{sheet.Name}": Press ' + swap_quotes(f'{btn}'))

  si.recover(sheet)
  sheet.buttons = []
  si.render(sheet)
# }}} sheet_changed_callback

# {{{ class EventDuck
class EventDuck:
  @typechecked
  def __init__(self) -> None:
    self._store:dict[str,Any] = {}

  @typechecked
  def __getattr__(self, name:str) -> Any:
    if name in self._store:
      return self._store[name]
    value = EventDuck()
    self._store[name] = value
    return value

  @typechecked
  def __setattr__(self, name:str, value:Any) -> None:
    if name == "_store":
      super().__setattr__(name, value)
    else:
      self._store[name] = value

  @typechecked
  def __repr__(self) -> str:
    return f"Duck({self._store})"
# }}} class EventDuck

# {{{ cmd_test_click
@typechecked
def cmd_test_click(event:Any) -> None:
  cmd_test_click_impl(event, None)
# }}} cmd_test_click

# {{{ cmd_test_click_impl
@typechecked
def cmd_test_click_impl(event:Any, keys_:list[str|int|float|bool]|None) -> bool:
  if keys_ is not None:
    keys = keys_
  else:
    keys = list(DataProtocol.splitPrefix(event.Source.Model.Name))

  doc = XSCRIPTCONTEXT.getDocument()
  sheet = doc.CurrentController.ActiveSheet

  @typechecked
  def swap_quotes(s:str) -> str:
    return s.replace("'", "__SINGLE__").replace('"', "'").replace("__SINGLE__", '"')
  if not isinstance(event, EventDuck):
    print(f'Sheet "{sheet.Name}": Press ' + swap_quotes(f'{keys}'))

  if sheet.Name not in GlobalVars.sheet_info:
    # This happens if libreoffice is restarted and someone clicks on a button on an existing saved sheet.
    if sheet.Name == MAINSheet:
      recover_main_sheet()
    else:
      data = getAPIKeys(sheet)
      if '_response' in data['_control']:
        si = SchemaHelper.getInboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
      else:
        si = SchemaHelper.getOutboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
      GlobalVars.sheet_info[sheet.Name] = si
      si.recover(sheet)

  si = GlobalVars.sheet_info[sheet.Name]

  if keys[0] == "COPY":
    sheet = doc.Sheets.getByName(castJstr(keys[1]))
    GlobalVars.copyval = GlobalVars.sheet_info[castJstr(keys[1])].get(sheet, keys[2:])
    return True
  if keys[0] in ("EDIT", "DELETE", "ADD", ):
    if keys[0] == "EDIT" and keys[-1] == "_PASTE":
      keys[-1] = GlobalVars.copyval
    if keys[0] == "DELETE":
      si.delete(keys[2:])
      si.render(sheet)
    elif keys[0] == "ADD":
      si.add(keys[2:])
      si.render(sheet)
    else:
      si.edit(sheet, keys[2:])

    if not isinstance(event, EventDuck):
      event = EventDuck()
    if sheet.Name == MAINSheet:
      on_sheet_change(event)
    else:
      sheet_changed_callback(event)
    return True
  if keys[0] == "VALIDATE":
    sheet = doc.Sheets.getByName(castJstr(keys[1]))
    v = GlobalVars.sheet_info[castJstr(keys[1])].get(sheet, keys[2:-1])
    expected = keys[-1]
    if expected == "_PASTE":
      expected = GlobalVars.copyval
    if v != expected or type(v) != type(expected): # pylint: disable=unidiomatic-typecheck
      sheet.dumpAsText()
      fatal(f"Got '{v}' ({type(v)})  but need '{expected}' ({type(expected)})", {})
    return True
  if keys[0] == "GOTO":
    if len(keys) == 2:
      return True
    sheet = doc.Sheets.getByName(castJstr(keys[2]))
    v = GlobalVars.sheet_info[castJstr(keys[2])].get(sheet, keys[3:-1])
    expected = keys[-1]
    if expected == "_PASTE":
      expected = GlobalVars.copyval
    return v == expected and type(v) == type(expected) # pylint: disable=unidiomatic-typecheck
  if keys[0] == "SUBMIT":
    sheets = doc.Sheets
    endpoint = Endpoint(getConfig())
    result = endpoint.make_get_request(SchemaHelper.getAPI(), AccessHelper(si.to_json()), None, [])
    if result['_control']['_output'] == "xml":
      if result['_data'] is not None:
        response = ResponseData(result['_data'])
      elif result['_text'] != "":
        response = ResponseData(result['_text'])
      else:
        response = ResponseData()
    elif result['_control']['_output'] == "json":
      if result['_data'] is not None:
        response = ResponseData(result['_data'])
      else:
        response = ResponseData()
    elif result['_control']['_output'] == "None":
      response = ResponseData()
    else:
      fatal(f"Don't know how to handle {result}",{})
    headers = ResponseData(result['_parameters'])
    si = SchemaHelper.getInboundSchemas(result, response, headers)
    if len(keys) == 3:
      pfix = castJstr(keys[2]).replace("[test only]", "")
      if sheets.hasByName(pfix):
        sheets.removeByName(pfix)
      GlobalVars.sheet_info.pop(pfix, None)
    else:
      pfix = "response" # FIXME better name please!
    idx = 0
    name = pfix
    while sheets.hasByName(name):
      idx += 1
      name = f"{pfix}-{idx}"
    GlobalVars.sheet_info[name] = si
    sheets.insertNewByName(name, len(sheets))
    sheet = sheets.getByName(name)
    attach_on_sheet_changed_event(sheet)
  elif keys[0] == "GENSHEET":
    # openoffice doesn't (trivially) allow square brackets in the name.
    name = castJstr(keys[1]).replace("[test only]", "")
    sheets = doc.Sheets
    if sheets.hasByName(name):
      sheets.removeByName(name)
    GlobalVars.sheet_info.pop(name, None)
    # Insert the sheet, generating a unique name
    sheet = sheets.getByName(MAINSheet)
    data = getAPIKeys(sheet)
    si = SchemaHelper.getOutboundSchemas(data, ResponseData(valtype="UseDefault"), ResponseData(valtype="UseDefault"))
    if GlobalVars.warnings:
      jd({"warnings":GlobalVars.warnings})
      GlobalVars.warnings = []
    idx = 0
    # Insert the sheet, generating a unique name
    while sheets.hasByName(name):
      idx += 1
      name = f"{castJstr(keys[1]).replace('[test only]', '')}-{idx}"
    GlobalVars.sheet_info[name] = si
    sheets.insertNewByName(name, len(sheets))
    sheet = sheets.getByName(name)
    attach_on_sheet_changed_event(sheet)
  else:
    raise RuntimeError(f"Unhandled {keys}")
  sheet.buttons = []
  si.render(sheet)
  if GlobalVars.warnings:
    print("Warnings while importing:")
    jd({"warnings":GlobalVars.warnings})
  return True
# }}} cmd_test_click_impl

# {{{ execute_task
@typechecked
def execute_task(ctrl:JSONDict, idx:str|None, args:list[str], depth:str='') -> None:
  args = [str(uuid.uuid4())] + args
  print(f"\n*****{depth}Starting task {idx} {args}")

  def expand_arg(v:str) -> str:
    pattern = re.compile(r"_\$(\d+)_")
    return pattern.sub(lambda m: str(args[int(m.group(1))]), v,)

  def expand_args(p:list[str]) -> list[str]:
    n:list[str] = []
    for v in p:
      if isinstance(v, str):
        n.append(expand_arg(v))
      else:
        n.append(v)
    return n

  while True:
    if idx == "END":
      return
    if idx is None:
      fatal("Failed: all GOTO options failed (missing GOTO END?)", {})
    task_step = ctrl[idx]
    print(f"\n*****{depth}Step {idx} {task_step['description'] if 'description' in task_step else ''}")
    idx = None

    doc = XSCRIPTCONTEXT.getDocument()
    sheets = doc.Sheets

    press:list[list[str|float|int|bool]] = []
    if 'press' in task_step:
      press = copy.deepcopy(task_step['press'])

    inbound_sheet_name:str|None = None
    outbound_sheet_name:str|None = None

    for p in press:
      p = expand_args(p)

      if p[0] == "SUBMIT":
        if inbound_sheet_name is not None:
          fatal(f"Multiple SUBMIT buttons found in {idx}", {})
        inbound_sheet_name = castJstr(p[2])
      if p[0] == "GENSHEET":
        if outbound_sheet_name is not None:
          fatal(f"Multiple GENSHEET buttons found in {idx}", {})
        outbound_sheet_name = castJstr(p[1])

    cache = None
    if 'cache' in task_step:
      cache = expand_arg(task_step['cache'])

    if cache and os.path.exists(cache):
      if not inbound_sheet_name:
        fatal("cache but no inbound_sheet_name", {})

      print(f"{depth}Loading step from cache {cache}")
      with open(cache, "r", encoding="utf-8") as f:
        GlobalVars.warnings = []

        response = json.load(f)
        headers = ResponseData(response['_parameters']) if '_parameters' in response else ResponseData()
        if '_data' in response:
          if response['_data'] is None:
            rd = ResponseData()
          else:
            rd = ResponseData(response['_data'][response['_control']['_output']])
        else:
          rd = ResponseData(valtype="UseDefault")

        si = SchemaHelper.getInboundSchemas(response, rd, headers)
        if GlobalVars.warnings:
          print("Warnings while importing:")
          jd({"warnings":GlobalVars.warnings})
        GlobalVars.warnings = []

        GlobalVars.sheet_info[inbound_sheet_name] = si
        sheets.insertNewByName(inbound_sheet_name, len(sheets))
        sheet = sheets.getByName(inbound_sheet_name)
        sheet.buttons = []
        si.render(sheet)
        newpress:list[list[str|float|int|bool]] = []
        cp = False
        for btn_action in press:
          if not cp and btn_action[0] == "GOTO":
            newpress.append(btn_action)
          if cp:
            newpress.append(btn_action)
          if btn_action[0] == "SUBMIT":
            cp = True
        press = newpress

    for i, btn_action in enumerate(press):
      btn_action = expand_args(btn_action)
      if btn_action[0] in ("GENSHEET", ):
        si = GlobalVars.sheet_info[MAINSheet]
        doc.CurrentController.ActiveSheet = sheets.getByName(MAINSheet)
      elif btn_action[0] in ("ADD", "COPY", "DELETE", "EDIT", "GENSHEET", "PRINT", "SUBMIT", "VALIDATE"):
        si = GlobalVars.sheet_info[castJstr(btn_action[1])]
        doc.CurrentController.ActiveSheet = sheets.getByName(btn_action[1])
      elif btn_action[0] in ("GOTO", ):
        if len(btn_action) >= 3:
          si = GlobalVars.sheet_info[castJstr(btn_action[2])]
          doc.CurrentController.ActiveSheet = sheets.getByName(btn_action[2])
        else:
          si = GlobalVars.sheet_info[MAINSheet]
          doc.CurrentController.ActiveSheet = sheets.getByName(MAINSheet)
      elif btn_action[0] in ("GOSUB", ):
        execute_task(ctrl, btn_action[1], expand_args(btn_action[2:]))
        continue
      else:
        print(f"Skipping unknown action {btn_action[0]} in {idx}")
        continue

#      if 'ActiveSheet' in task_step:
#        si = GlobalVars.sheet_info[task_step['ActiveSheet']]
#        doc.CurrentController.ActiveSheet = sheets.getByName(task_step['ActiveSheet'])
#      else:
#        si = GlobalVars.sheet_info[MAINSheet]
#        doc.CurrentController.ActiveSheet = sheets.getByName(MAINSheet)

#      if i == 0:
#        print(f"Start: Active Sheet is {doc.CurrentController.ActiveSheet.Name}")
#        print(f"Sheets are {list(sheets.data)}")
#        doc.CurrentController.ActiveSheet.dumpAsText()
      print(f"About to execute {btn_action} : Sheets are {list(sheets.data)}")
      if btn_action[0] in ("SUBMIT", "GENSHEET", "PRINT"):
        doc.CurrentController.ActiveSheet.dumpAsText()
        print("-----------")
        if GlobalVars.warnings:
          print("Warnings while importing:")
          jd({"warnings":GlobalVars.warnings})
          GlobalVars.warnings = []

      event = EventDuck()
      event.Source.Model.Name = ':'.join([str(x).replace(':','\\:') for x in btn_action])
      event.CellAddress.Column = 1
      event.CellAddress.Row = -1
      for b in si.button_controls:
        keys = DataProtocol.splitPrefix(b.name)
        if keys == btn_action or \
            (keys[0] in ("GENSHEET", "EDIT") and keys[:-1] == btn_action[:-1]) or \
            (keys[0] == "SUBMIT" and btn_action[0] == "SUBMIT"):
          event.CellAddress.Row = b.row
          if keys[0] == "EDIT":
            event.CellAddress.Column = b.col-3
          else:
            event.CellAddress.Column = b.col
          break

      if btn_action[0] == "GOTO":
        if cmd_test_click_impl(event, btn_action):
          idx = castJstr(btn_action[1])
          break
        print(f"{btn_action} GOTO not followed")
      elif btn_action[0] == "EVAL":
        argno = int(castJstr(keys[1]))
        if len(args) <= argno:
          args.extend([0] * (argno+1 - len(args)))
        safe_globals:dict[str,Any] = {}
        safe_locals:dict[str,Any] = {"args": args, "now": lambda secs=0: datetime.now(timezone.utc) + timedelta(seconds=secs), }
        rv = eval(castJstr(keys[2]), safe_globals, safe_locals)
        if not isinstance(rv, (str, int, float, bool)):
          ErrorHandler.fatal("Didn't get str, int float or bool from translation function", {})
        args[argno] = rv

      elif event.CellAddress.Row != -1 or btn_action[0] in ("VALIDATE", "COPY"):
        # We need COPY here because there might be colons in the value we're calculating.
        cmd_test_click_impl(event, btn_action if btn_action[0] in ("VALIDATE","EDIT","COPY") else None)
      elif btn_action[0] in ("EDIT", "DELETE",):
        doc.CurrentController.ActiveSheet.dumpAsText()
        fatal(f"Skipped {btn_action} not found in buttons", {})
      elif btn_action[0] != "PRINT":
        print(f"Skipped {btn_action} not found in buttons")

    if outbound_sheet_name is not None:
      print(f"{depth}Generated Sheet:")
      sheet = sheets.getByName(outbound_sheet_name)
      sheet.dumpAsText()
      print("-----------")

    if inbound_sheet_name is not None:
      sheet = sheets.getByName(inbound_sheet_name)
      print(f"{depth}Response Sheet:")
      sheet = sheets.getByName(inbound_sheet_name)
      sheet.dumpAsText()
      print("-----------")

      if cache:
        with open(cache, "w", encoding="utf-8") as f:
          json.dump(GlobalVars.sheet_info[inbound_sheet_name].to_json(), f, indent=2)
          f.write("\n")
# }}} execute_task

# This ensures that the main sheet exists
# {{{ xrecover_main_sheet()
@typechecked
def xrecover_main_sheet(si:SheetData|None, sheet:LibreOfficeHelper.LibreOfficeODSSheet|None) -> None:

  mainschema:JSONDict = {
    "type": "object",
    "properties": {
      "_api": { "type": "string" },
      "_major": { "type": "string" },
      "_minor": { "type": "string" },
      "_path": { "type": "string" },
      "_action": { "type": "string" },
      "_server": { "type": "string" },
      "_id": {
        "oneOf": [
         {
            "type": "object",
            "title": "arn",
            "properties": {
              "_arn": { "type": "string" }
            },
            "required": [ "_arn" ],
            "additionalProperties": False
          },
          {
            "type": "object",
            "title": "nino",
            "properties": {
              "_nino": { "type": "string" }
            },
            "required": [ "_nino" ],
            "additionalProperties": False
          },
          {
            "type": "object",
            "title": "vrn",
            "properties": {
              "_vrn": { "type": "string" }
            },
            "required": [ "_vrn" ],
            "additionalProperties": False
          }
        ]
      }
    },
    "required": [ "_api", "_major", "_minor", "_path", "_action", "_server", "_id" ],
    "additionalProperties": False
  }
  apischema:JSONDict = {
    "_control": { "_output": "json", },
    "_schema": None,
    "_mainsheet": True,
  }

  api = SchemaHelper.getAPI()

  aschema = copy.deepcopy(apischema)
  control = aschema["_control"]
  mschema = copy.deepcopy(mainschema)

  def setkey(key:str, keys:list[str], defkey:str) -> str:
    mschema["properties"][key]["enum"] = keys
    v:str = castJstr(si.get(sheet, [ "", "json", key ])) if sheet is not None and si is not None else defkey
    if v not in keys:
      v = keys[0]
      if sheet is not None and si is not None:
        si.edit(sheet, [ "", "json", key, v] )
    mschema["properties"][key]["example"] = v
    control[key] = v
    return v

  keys = sorted([ castJstr(x) for x in api if any('servers' in api[x][major][minor] for major in api[x] for minor in api[x][major]) ])
  v = setkey("_api", keys, keys[0])
  api = api[v]

  keys = sorted([ castJstr(x) for x in api if any('servers' in api[x][minor] for minor in api[x]) ])
  v = setkey("_major", keys, keys[-1])
  api = api[v]

  keys = sorted([ castJstr(x) for x in api if 'servers' in api[x] ])
  v = setkey("_minor", keys, keys[-1])
  api = api[v]

  servers = []
  for s in api["servers"]:
    if 'description' in s:
      servers.append(s['description'])
    else:
      servers.append("Sandbox" if "test-api" in s['url'] else "Production")

  api = api["paths"]

  keys =  sorted(api.keys())
  v = setkey("_path", keys, keys[0])
  api = api[v]

  keys =  sorted(api.keys())
  v = setkey("_action", keys, keys[0])
  api = api[v]

  keys =  sorted(servers)
  v = setkey("_server", keys, keys[0])

  aschema['_schema'] = SchemaHelper.process_schema(mschema, ["MAIN"])

  si = SheetData(aschema, ResponseData(valtype="UseDefault"), ResponseData())
  if sheet is not None:
    si.recover(sheet)
    # We have to render to regenerate the button_controls array
    si.render(sheet)
  GlobalVars.sheet_info[MAINSheet] = si
# }}} xrecover_main_sheet


# This ensures that the main sheet exists
# {{{ recover_main_sheet()
@typechecked
def recover_main_sheet() -> None:
  doc = XSCRIPTCONTEXT.getDocument()
  sheets = doc.Sheets

  # Make sure that the MAIN sheet exists.
  if MAINSheet not in GlobalVars.sheet_info:

    # First ensure apischema is consistent with api
    xrecover_main_sheet(None, None)
    si = GlobalVars.sheet_info[MAINSheet]

    # We must render to a dummy sheet to set row info
    si.render(LibreOfficeHelper.MockODSSheet(""))

    # Now import the real sheet if it exists
    if sheets.hasByName(MAINSheet):
      sheet = sheets.getByName(MAINSheet)
      xrecover_main_sheet(si, sheet)

  if not sheets.hasByName(MAINSheet):
    sheets.insertNewByName(MAINSheet, 0)
    sheet = sheets.getByName(MAINSheet)
    cast(LibreOfficeHelper.MockODSSheet,GlobalVars.sheet_info[MAINSheet]).buttons = []
    GlobalVars.sheet_info[MAINSheet].render(sheet)

  # Make sure that the NINO sheet exists.
  if not sheets.hasByName(NINOSheet):
    sheets.insertNewByName(NINOSheet, 1)

  # This sheet is not protected so we overwrite every time
  sheet = sheets.getByName(NINOSheet)
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 0, 0, LibreOfficeHelper.CellData("ID"))
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 1, 0, LibreOfficeHelper.CellData("Type"))
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 2, 0, LibreOfficeHelper.CellData("Known Fact"))
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 3, 0, LibreOfficeHelper.CellData("Description"))
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 4, 0, LibreOfficeHelper.CellData("UserID"))   # These two are only relevant for testing with automateBrowser
  LibreOfficeHelper.dump_to_sheet_cell(sheet, 5, 0, LibreOfficeHelper.CellData("Password"))
# }}} recover_main_sheet

# This is the MAINSheet changed callback.
# {{{ on_sheet_change
@typechecked
def on_sheet_change(event:Any) -> None:
#  print(dir(event))
#  print(f"Column is {event.CellAddress.Column}")
#  print(f"Row is {event.CellAddress.Row}")

  recover_main_sheet()

  doc = XSCRIPTCONTEXT.getDocument()
  sheets = doc.Sheets

  sheet = sheets.getByName(MAINSheet)
  si = GlobalVars.sheet_info[MAINSheet]

  @typechecked
  def swap_quotes(s:str) -> str:
    return s.replace("'", "__SINGLE__").replace('"', "'").replace("__SINGLE__", '"')
  if not isinstance(event, EventDuck):
    cell = sheet.getCellByPosition(event.CellAddress.Column, event.CellAddress.Row)
    doc.CurrentController.ActiveSheet = sheet
    doc.CurrentController.select(cell)

    btn = ["EDIT", sheet.Name] + si.get_edit_keys(sheet, event.CellAddress.Row)
    print(f'Sheet "{sheet.Name}": Press ' + swap_quotes(f'{btn}'))

  # Unprotected it so we can update it
  sheet.unprotect("") # No password

  xrecover_main_sheet(si, sheet)
  si = GlobalVars.sheet_info[MAINSheet]

  # Clear entire sheet
  cells = sheet.getCellRangeByPosition(0, 10, 1, sheet.Rows.Count-1)
  cells.clearContents(1023)

  draw_page = sheet.DrawPage
  cc = draw_page.Count

  for i in range(cc-1, -1, -1):
    ctrl = draw_page.getByIndex(i)
    draw_page.remove(ctrl)

  sheet.buttons = []
  si.render(sheet)

  sheet.protect("") # No password

#  print("MAIN Sheet after on_sheet_change:")
#  sheet.dumpAsText()
#  sheet.protect("") # No password
# }}} on_sheet_change

# {{{ attach_on_sheet_changed_event
@typechecked
def attach_on_sheet_changed_event(sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> None:
  pass
# }}} attach_on_sheet_changed_event

if __name__ == "__main__":
  with open(sys.argv[1], "r", encoding="utf-8") as f:
    ctrl:JSONDict = json.load(f)

  # Handle top level includes.
  if 'include' in ctrl:
    saved = copy.copy(ctrl)
    for incfile in ctrl['include']:
      with open(incfile, "r", encoding="utf-8") as f:
        inc:JSONDict = json.load(f)
        ctrl.update(inc)

    # Restore any keys overwritten during the include
    ctrl.update(saved)

  # Handle second level includes.
  for k,v in ctrl.items():
    if not isinstance(v, dict):
      continue
    if "include" not in v:
      continue
    with open(v['include'], "r", encoding="utf-8") as f:
      v.pop("include", None)
      inc = json.load(f)
      p = inc['press']
      if 'press' in v:
        p += v['press']
      v['press'] = p
      actv = inc['ActiveSheet'] if 'ActiveSheet' in inc else MAINSheet
      if 'ActiveSheet' not in v:
        v['ActiveSheet'] = actv

  SchemaHelper.getAPI(ctrl['schema'])

  if 'config' in ctrl:
    getConfig(ctrl['config'])

  # We need the main sheet to exist.
  recover_main_sheet()

  execute_task(ctrl, 'START', [])

# vim: set sw=2 sts=2 ts=2 expandtab:
