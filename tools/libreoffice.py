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

import os
import copy
import hashlib # pylint: disable=unused-import
import json
import uuid
import re
import time
from typing import Any, Callable, TypeVar
import uno
from com.sun.star.awt import Size, Point  # pylint: disable=import-error
from com.sun.star.script import ScriptEventDescriptor # pylint: disable=import-error
from com.sun.star.beans import PropertyValue  # pylint: disable=import-error
from com.sun.star.ui.dialogs.TemplateDescription import FILEOPEN_SIMPLE # pylint: disable=import-error

import typeguard

# typechecked doesn't work inside libreoffice
_F = TypeVar("_F", bound=Callable[..., object])
def typechecked(fn: _F) -> _F:
  return fn
typeguard.typechecked = typechecked

# MTD imports
from mtd.Endpoint import Endpoint # pylint: disable=wrong-import-position
from mtd.Config import Config # pylint: disable=wrong-import-position
from mtd.AccessHelper import AccessHelper # pylint: disable=wrong-import-position
from mtd.SheetData import SheetData # pylint: disable=wrong-import-position
from mtd.DataProtocols import DataProtocol # pylint: disable=wrong-import-position
from mtd.SpecialTypes import ResponseData # pylint: disable=wrong-import-position
from mtd.GlobalVars import GlobalVars # pylint: disable=wrong-import-position
from mtd.ErrorHandler import jd, fatal # pylint: disable=wrong-import-position
from mtd import SchemaHelper # pylint: disable=wrong-import-position
from mtd import LibreOfficeHelper # pylint: disable=wrong-import-position
from mtd.JSONTypes import JSONDict, castJDict, castJstr # pylint: disable=wrong-import-position

XSCRIPTCONTEXT: LibreOfficeHelper.XScriptContext

GlobalVars.selectButtons = False
GlobalVars.editButtons = False

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
      macro = os.path.realpath(__file__)
      macro = os.path.dirname(macro)
      macro = os.path.dirname(macro)

      with open(macro + '/artifacts/application.json', 'r', encoding="utf-8") as f:
        GetAPI.API = castJDict(json.load(f))
    return GetAPI.API
# }}} GetAPI

SchemaHelper.getAPI = GetAPI()

# {{{ GetConfig
class GetConfig:
  _config: Config
  @typechecked
  def __call__(self) -> Config:
    if not hasattr(GetConfig, "_config"):
      macro = os.path.realpath(__file__)
      macro = os.path.dirname(macro)
      macro = os.path.dirname(macro)
      # FIXME - where to get this from?
      GetConfig._config = Config('test.db.json')
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
  # The dropdown is controlled into the next cell so we have to leave a gap on the LHS
  cursor = sheet.getCellByPosition(col, row).Position
  x = cursor.X
  y = cursor.Y
  w = sheet.getColumns().getByIndex(col).Width
  h = sheet.getRows().getByIndex(row).Height

  doc = XSCRIPTCONTEXT.getDocument() # pylint: disable=undefined-variable

  draw_page = sheet.DrawPage
  forms = draw_page.Forms
  if forms.Count:
    form = forms[0]
  else:
    form = doc.createInstance('com.sun.star.form.component.Form')
    forms.insertByName('MyForm', form)

  # Add the control to the form
  model = doc.createInstance('com.sun.star.form.component.CommandButton')
  model.Name = name
  model.Label = label
  index = form.Count
  form.insertByIndex(index, model)

  control = doc.createInstance('com.sun.star.drawing.ControlShape')
  control.setSize(Size(w,h))
  control.setPosition(Point(x,y))
  control.Control = model
  draw_page.add(control)

  # Add the event to the form
  url = 'vnd.sun.star.script'
  funcname = 'cmd_test_click'
  url = f'{url}:libreoffice|sheet-changed.py${funcname}?language=Python&location=user'

  event = ScriptEventDescriptor()
  event.AddListenerParam = ''
  event.EventMethod = 'mousePressed'
  event.ListenerType = 'XMouseListener'
  event.ScriptCode = url
  event.ScriptType = 'Script'

  form.revokeScriptEvents(index)
  form.registerScriptEvent(index, event)
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
    jd(si.to_json())
    # FIXME quick hack to test
    # TODO add applicationId and scope to sheet
    # FIXME This might block waiting for the user to do the OATH journey
    sheets = doc.Sheets
    endpoint = Endpoint(getConfig())
    result = endpoint.make_get_request(SchemaHelper.getAPI(), AccessHelper(si.to_json()), None, [])
    jd(result)
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
#    # FIXME temporary code to auto-unprotect everything and delete older things.
#    dellist = []
#    for sh in doc.Sheets:
#      try:
#        if sh.Name not in {MAINSheet, NINOSheet}:
#          dellist.append(sh.Name)
#          sh.unprotect("")
#      except com.sun.star.uno.RuntimeException: # type: ignore[name-defined] # pylint: disable=undefined-variable
#        pass
#    for sh in dellist[:-2]:
#      doc.Sheets.removeByName(sh)
#    # FIXME END temporary code

    # openoffice doesn't (trivially) allow square brackets in the name.
    name = castJstr(keys[1]).replace("[test only]", "")
    sheets = doc.Sheets
    # TJW FIXME remove
    if sheets.hasByName(name):
      sheets.removeByName(name)
    GlobalVars.sheet_info.pop(name, None)
    # TJW end
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
  elif keys[0] == "Import":
    fname = pick_file()
    if fname is None:
      return True
#    with open(fname, 'r', encoding="utf-8") as f:
#      j = json.load(f)
#    # FIXME handle null
#    si = SchemaHelper.getOutboundSchemas(j, ResponseData(j['_data']), ResponseData(j['_headers']))
#    print(si)
#    name = "import"
#    idx = 0
#    sheets = XSCRIPTCONTEXT.getDocument().Sheets
#    while name in sheets:
#      idx += 1
#      name = f"import-{idx}"
#    GlobalVars.sheet_info[name] = si
#    sheets.insertNewByName(name, len(sheets))
#    sheet = sheets.getByName(name)
    with open(fname, "r", encoding="utf-8") as f:
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
    for _,v in ctrl.items():
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

    # We need the main sheet to exist.
    recover_main_sheet()

    idxx = ctrl['start']

    execute_task(ctrl, idxx, [])
    return True

  elif keys[0] == "LoadResponse":
    pick_file()
    return True
  else:
    raise RuntimeError(f"Unhandled {keys}")
  si.render(sheet)
  return True
# }}} cmd_test_click_impl

# {{{ pick_file
@typechecked
def pick_file() -> str|None:
  ctx = uno.getComponentContext()
  smgr = ctx.getServiceManager()

  # Create the file picker dialog
  filepicker = smgr.createInstanceWithContext(
    "com.sun.star.ui.dialogs.FilePicker", ctx
  )

  # Set it to a simple "Open File" dialog
  filepicker.initialize((FILEOPEN_SIMPLE,))

  # Optional: filter for specific file types
  filepicker.appendFilter("Text files", "*.txt")
  filepicker.appendFilter("All files", "*.*")
  filepicker.setCurrentFilter("All files")

  macro = os.path.realpath(__file__)
  macro = os.path.dirname(macro)
  macro = os.path.dirname(macro)
  macro = os.path.dirname(macro)
#  filepicker.setDisplayDirectory(uno.systemPathToFileUrl(macro + '/mtdorig/tests/agent-authorisation-api'))
  filepicker.setDisplayDirectory(uno.systemPathToFileUrl('/home/tim/git/mtd/libreoffice/tests'))

  # Execute the dialog
  result = filepicker.execute()

  if result == 1:  # 1 = OK pressed
    files = filepicker.getFiles()
    # getFiles() returns a tuple of URLs like "file:///path/to/file"
    print(files)
    return str(uno.fileUrlToSystemPath(files[0]))

  return None
# }}} pick_file

# {{{ set_dropdown_from_other_sheet
@typechecked
def set_dropdown_from_other_sheet(cell:LibreOfficeHelper.LibreOfficeODSCell, name:str, col:int, first_row:int, last_row:int) -> None:
  validation = cell.Validation
  validation.Type = "LIST"
  validation.Formula1 = f"${name}.${chr(ord('A')+col)}${first_row}:${chr(ord('A')+col)}${last_row}"
  validation.IgnoreBlankCells = True
  cell.Validation = validation
# }}} set_dropdown_from_other_sheet

# {{{ execute_task
@typechecked
def execute_task(ctrl:JSONDict, idx:str|None, args:list[str], depth:str='') -> None:
  print(f"\n*****{depth}Starting task {idx}")
  args = [str(uuid.uuid4())] + args

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

    ctx = uno.getComponentContext()
    smgr = ctx.getServiceManager()

    toolkit = smgr.createInstanceWithContext(
        "com.sun.star.awt.Toolkit",
        ctx
    )

    task_step = ctrl[idx]
    print(f"\n*****{depth}Step {idx} {task_step['description'] if 'description' in task_step else ''}")
    idx = None

    if 'subtask' in task_step:
      execute_task(ctrl, task_step['subtask'], expand_args(task_step['args']) if 'args' in task_step else [], depth+'    ')

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
        if sheets.hasByName(inbound_sheet_name):
          sheets.removeByName(inbound_sheet_name)
        sheets.insertNewByName(inbound_sheet_name, len(sheets))
        sheet = sheets.getByName(inbound_sheet_name)
#        sheet.buttons = []
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
        time.sleep(1)
        toolkit.processEventsToIdle()

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
      else:
        print(f"Skipping unknown action {btn_action[0]} in {idx}")
        continue


#      if i == 0:
#        print(f"Start: Active Sheet is {doc.CurrentController.ActiveSheet.Name}")
#        print(f"Sheets are {list(sheets.data)}")
#        doc.CurrentController.ActiveSheet.dumpAsText()
#      if btn_action[0] in ("SUBMIT", "GENSHEET", "PRINT"):
#        print(f"About to execute {btn_action} : Sheets are {list(sheets.data)}")
#        doc.CurrentController.ActiveSheet.dumpAsText()
#        print("-----------")
#        if GlobalVars.warnings:
#          print("Warnings while importing:")
#          jd({"warnings":GlobalVars.warnings})
#          GlobalVars.warnings = []

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
      elif event.CellAddress.Row != -1 or btn_action[0] in ("VALIDATE", "COPY"):
        # We need COPY here because there might be colons in the value we're calculating.
        cmd_test_click_impl(event, btn_action if btn_action[0] in ("VALIDATE","EDIT","COPY") else None)
      elif btn_action[0] != "PRINT":
        print(f"Skipped {btn_action} not found in buttons")

      toolkit.processEventsToIdle()
      time.sleep(1)

    if outbound_sheet_name is not None:
      print(f"{depth}Generated Sheet:")
      sheet = sheets.getByName(outbound_sheet_name)
#      sheet.dumpAsText()
      print("-----------")

    if inbound_sheet_name is not None:
      sheet = sheets.getByName(inbound_sheet_name)
      print(f"{depth}Response Sheet:")
      sheet = sheets.getByName(inbound_sheet_name)
#      sheet.dumpAsText()
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

  si.render(sheet)

  sheet.protect("") # No password

#  print("MAIN Sheet after on_sheet_change:")
#  sheet.dumpAsText()
#  sheet.protect("") # No password
# }}} on_sheet_change

# {{{ attach_on_sheet_changed_event
@typechecked
def attach_on_sheet_changed_event(sheet:LibreOfficeHelper.LibreOfficeODSSheet) -> None:
  p1 = PropertyValue()
  p1.Name = "EventType"
  p1.Value = "Script"
  p1.Handle = -1
  p2 = PropertyValue()
  p2.Name = "Script"
  p2.Handle = -1
  url = 'vnd.sun.star.script'
  funcname = 'sheet_changed_callback'
  url = f'{url}:libreoffice|sheet-changed.py${funcname}?language=Python&location=user'
  p2.Value = url

  uno.invoke(sheet.Events, "replaceByName", ("OnChange", uno.Any("[]com.sun.star.beans.PropertyValue", (p1, p2))))
# }}} attach_on_sheet_changed_event

# vim: set sw=2 sts=2 ts=2 expandtab:
