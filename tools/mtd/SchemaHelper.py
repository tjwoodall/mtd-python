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
import copy
from typing import cast

from typeguard import typechecked

from .JSONTypes import JSONType, JSONDict, Jstr, JList, JDict, castJDict, JSONList
from . import SheetData
from . import SpecialTypes
from . import ErrorHandler
from . import GlobalVars

def getAPI(filename: str = "") -> JSONDict:
  raise RuntimeError("getAPI not initialized")

# {{{ get_gov_test_options
@typechecked
def get_gov_test_options(api:JSONDict) -> JSONList:
  if 'description' not in api:
    return []

  lines = [ [ y.strip() for y in x.strip().split('|') ] for x in api['description'].split('\n') if x.strip().startswith('|') ]

  # Header value row and divider row
  if len(lines) > 2:
    lines = lines[2:]
  else:
    lines = []

  # Why can't the vat-api be the same as everything else :-(
  linestd = [ [ y.strip() for y in x.strip().split('<td>') ] for x in api['description'].split('</tr>') ] #if x.strip().startswith('<tr>') ]

  # Header row
  if len(linestd) > 1:
    linestd = linestd[1:]
    lines = []
    for l in linestd:
      if len(l) > 2:
        for i,_ in enumerate(l):
          l[i] = re.sub(r'<[^>]*>', '', l[i])
        lines.append(l)

#  print(f"Gov-test-table", lines)
  return [ x[0] if len(x) == 2 else x[1] for x in lines ]
# }}} get_gov_test_options

# {{{ getOutboundSchemas
@typechecked
def getOutboundSchemas(apikeys:JSONDict, indata:SpecialTypes.ResponseData, headerdata:SpecialTypes.ResponseData) -> SheetData.SheetData:
  api = getAPI()

  extraheaders = { k:v for k,v in apikeys.items() if not k.startswith("_")}

  control = apikeys['_control']

  api_key = control['_api'] if '_api' in control else "MISSING_api"
  if api_key not in api:
    raise RuntimeError(f"Invalid api {api_key}")
  api = api[api_key]

  major_key = control['_major'] if '_major' in control else "MISSING_major"
  if major_key not in api:
    raise RuntimeError(f"Invalid major {major_key}")
  api = api[major_key]

  minor_key = control['_minor'] if '_minor' in control else "MISSING_minor"
  if minor_key not in api:
    raise RuntimeError(f"Invalid minor {minor_key}")
  api = api[minor_key]

  servers = []
  for s in api["servers"]:
    servers.append("Sandbox" if "test-api" in s['url'] else "Production")

  server_key = control['_server'] if '_server' in control else "MISSING_server"
  if server_key not in servers:
    raise RuntimeError(f"Invalid server {server_key} need one from {servers}")

  api = api["paths"]

  ep_key = control['_path'] if '_path' in control else "MISSING_path"
  if ep_key not in api:
    raise RuntimeError(f"Invalid endpoint {ep_key}")
  api = api[ep_key]

  common_parameters = api['parameters'] if 'parameters' in api else []

  action_key = control['_action'] if '_action' in control else "MISSING_action"
  if action_key not in api:
    raise RuntimeError(f"Invalid action {action_key}")
  api = api[action_key]

  arn_default = control['_arn_default'] if '_arn_default' in control else ""

  data:JSONDict = {
    "_control": {
      "_api": api_key,
      "_major": major_key,
      "_minor": minor_key,
      "_path": ep_key,
      "_action": action_key,
      "_server": server_key,
      "_arn_default": arn_default,
    },
    "_parameters": [],
    "_schema": None,
  }
  for u in common_parameters + ( api['parameters'] if 'parameters' in api else [] ):
    if u['name'] not in {'xAccept', 'xContent-Type', 'Authorization', 'Content-Length'}:
      data['_parameters'].append(u)

  data['Gov-Test-Opts'] = get_gov_test_options(api)
  security = cast(JSONList, api["security"])
  if len(security) != 1:
    raise RuntimeError("Don't know how to handle multiple security types")
  secinfo = cast(JSONDict, security[0])
  if "User-Restricted" in secinfo:
    data['_User-Restricted'] = True

  if "requestBody" in api:
    body = api['requestBody']
    body = body['content']
    if 'application/json' in body:
      data["_control"]["_output"] = "json"
      body = body['application/json']
      schema = body['schema']
    elif "application/x-ndjson" in body:
      data["_control"]["_output"] = "ndjson"
      body = body['application/x-ndjson']
      schema = body['schema']
    elif "application/xml" in body:
      data["_control"]["_output"] = "xml"
      schema = { "anyOf": copy.deepcopy(anythingSelect) }
    else:
      schema = None
      data["_control"]["_output"] = "none"
      GlobalVars.GlobalVars.warnings.append(f"WARNING - Ignoring {list(body.keys())}")
    if schema:
#      print(f"process_schema on {hashlib.md5(json.dumps(schema).encode()).hexdigest()}")
      data['_schema'] = process_schema(schema, ["root"])
  else:
    data["_control"]["_output"] = "none"
    for k in 'title', 'summary', 'description':
      if k in api:
        data[k] = api[k]

  if extraheaders != {}:
    if headerdata.valtype not in ("MissingData", "UseDefault"):
      extraheaders.update(headerdata.getdict())
    headerdata = SpecialTypes.ResponseData(extraheaders)

#  print(f"SheetData.SheetData on {hashlib.md5(json.dumps(data).encode()).hexdigest()}")
  return SheetData.SheetData(data, indata, headerdata)
# }}} getOutboundSchemas

# {{{ getInboundSchemas
@typechecked
def getInboundSchemas(apikeys:JSONDict, indata:SpecialTypes.ResponseData, headerdata:SpecialTypes.ResponseData) -> SheetData.SheetData:
  api = getAPI()

  extraheaders = { k:v for k,v in apikeys.items() if not k.startswith("_")}

  control = apikeys['_control']

  api_key = control['_api'] if '_api' in control else "MISSING_api"
  if api_key not in api:
    raise RuntimeError(f"Invalid api {api_key}")
  api = api[api_key]

  major_key = control['_major'] if '_major' in control else "MISSING_major"
  if major_key not in api:
    raise RuntimeError(f"Invalid major {major_key}")
  api = api[major_key]

  minor_key = control['_minor'] if '_minor' in control else "MISSING_minor"
  if minor_key not in api:
    raise RuntimeError(f"Invalid minor {minor_key}")
  api = api[minor_key]

  api = api["paths"]

  ep_key = control['_path'] if '_path' in control else "MISSING_path"
  if ep_key not in api:
    raise RuntimeError(f"Invalid endpoint {ep_key}")
  api = api[ep_key]

  action_key = control['_action'] if '_action' in control else "MISSING_action"
  if action_key not in api:
    raise RuntimeError(f"Invalid action {action_key}")
  api = api[action_key]

  api = api["responses"]

  response_key = control['_response'] if '_response' in control else "MISSING_response"
  if response_key not in api:
    raise RuntimeError(f"Invalid response {response_key}")
  api = api[response_key]

  # FIXME - I don't like this - can we force json in _control?
  output_key = control['_output'] if '_output' in control else "json"

  data:JSONDict = {
    "_control": {
      "_api": api_key,
      "_major": major_key,
      "_minor": minor_key,
      "_path": ep_key,
      "_action": action_key,
      "_output": output_key,
      "_response": response_key,
    },
    "_parameters": [],
    "_schema": None,
  }

  for k,v in api['headers'].items() if 'headers' in api else {}.items():
    if 'content' in v:
      # only the vat-api does this, why?
      v = v['content']
      v = v['text/plain']
    h = copy.copy(v)
    h["name"] = k
    data['_parameters'].append(h)

  if 'content' in api:
    api = api['content']
    if output_key == "json":
      api = api['application/json']
      schema = api['schema']
    elif output_key == "xml":
      schema = { "anyOf": copy.deepcopy(anythingSelect) }
    elif output_key == "None":
      schema = None
    else:
      ErrorHandler.fatal(f"No inbound schema stuff {output_key}", {})
#      schema = None
#      GlobalVars.GlobalVars.warnings.append(f"WARNING - Ignoring {list(api.keys())}")
    if schema:
      data['_schema'] = process_schema(schema, ["root"])

  if extraheaders != {}:
    if headerdata.valtype not in ("MissingData", "UseDefault"):
      extraheaders.update(headerdata.getdict())
    headerdata = SpecialTypes.ResponseData(extraheaders)

#  print(f"SheetData.SheetData on {hashlib.md5(json.dumps(data).encode()).hexdigest()}")
  return SheetData.SheetData(data, indata, headerdata)
# }}} getInboundSchemas

# {{{ has_schema_selector
@typechecked
def has_schema_selector(schema:JSONDict) -> bool:
  return 'oneOf' in schema or 'anyOf' in schema or 'allOf' in schema
# }}} has_schema_selector

# {{{ process_schema_selector
@typechecked
def process_schema_selector(schema:JSONDict, path:list[str]) -> JSONList|JSONDict:
  if 'oneOf' in schema:
    select = 'oneOf'
  elif 'anyOf' in schema:
    select = 'anyOf'
  elif 'allOf' in schema:
    select = 'allOf'
  else:
    raise RuntimeError("Unhandled in process_schema_selector")

  updates:list[JSONDict]=[]
  for s in schema[select]:
    if set(s) != {"description"}:
      updates.append(castJDict(copy.deepcopy(process_schema(s, path+[select]))))
  pos = 0
  while pos < len(updates)-1:
    # If we have a oneOf with multiple enums then we want a value that matches any one enum
    # If we have a allOf with multiple enums then we need a value that matches all enums
    # If we have a anyOf with multiple enums then we need a value that matches any enum
    if 'enum' in JDict(updates, pos) and 'enum' in JDict(updates, pos+1):
      r:set[JSONType]=set()
      if select == "oneOf":
        r = set(JList(JDict(updates, pos), "enum")) ^ set(JList(JDict(updates, pos+1), "enum"))
      elif select == "allOf":
        r = set(JList(JDict(updates, pos), "enum")) & set(JList(JDict(updates, pos+1), "enum"))
      elif select == "anyOf":
        r = set(JList(JDict(updates, pos), "enum")) | set(JList(JDict(updates, pos+1), "enum"))
      JDict(updates, pos)["enum"] = list(r)
      JDict(updates, pos)['description'] = desc(JDict(updates, pos)) + '/' + desc(JDict(updates, pos+1))
      JDict(updates, pos).pop('title', None)
      JDict(updates, pos).pop('summary', None)
      del updates[pos+1]
    elif select == 'allOf' and ( get_type(JDict(updates, pos)) == "object" or get_type(JDict(updates, pos+1)) == "object" ):
      # This should be prevented by yaml-to-json
      if get_type(JDict(updates, pos)) != "object" or get_type(JDict(updates, pos+1)) != "object":
        raise RuntimeError("Type mismatch")

      for k,v in JDict(updates, pos+1).items():
        if k == 'properties' and 'properties' in JDict(updates, pos):
          JDict(JDict(updates, pos), "properties").update(v)
        elif k == 'required' and 'required' in JDict(updates, pos):
          r = set(JList(JDict(updates, pos), "required")) | set(JList(JDict(updates, pos+1), "required"))
          JDict(updates, pos)["required"] = list(r)
        else:
          JDict(updates, pos)[k] = v
      del updates[pos+1]
    elif select == 'allOf' and get_type(JDict(updates, pos)) == "array" and get_type(JDict(updates, pos+1)) == "array":
      GlobalVars.GlobalVars.warnings.append(f"WARNING - multiple arrays in allOf, we do not merge")
      pos = pos+1
    else:
      pos = pos+1
  if len(updates) == 1:
    if 'title' in schema:
      updates[0]['title'] = schema['title']
    return updates[0]
  return updates
# }}} process_schema_selector

# N.B. We use a special "type": "anything" to avoid this needing to be recursive
anythingObject:JSONDict = {
    "title": "object/additional",
    "type": "object",
    "additionalProperties": True
  }

anythingList:JSONDict = {
    "type": "array",
    "items": {
      "type": "anything"
    }
  }

# TODO (can we support nullable: True - which we don't currently?
anythingSelect:JSONList = [
  {
    "type": "string",
  },
  {
    "type": "integer"
  },
  {
    "type": "number"
  },
  {
    "type": "boolean"
  },
  {
    "type": "null"
  },
  anythingObject,
  anythingList
]

# {{{ process_schema_object
@typechecked
def process_schema_object(schema:JSONDict, path:list[str]) -> JSONDict|JSONList:
  if has_schema_selector(schema):
    return process_schema_selector(schema, path+["selector"])

  if "properties" not in schema:
    return schema

  data = copy.deepcopy(schema)

  properties = JDict(schema, 'properties')

  for k in properties:
    data['properties'][k] = process_schema(properties[k], path+["properties", k])
  return data
# }}} process_schema_object

# {{{ process_schema_array
@typechecked
def process_schema_array(schema:JSONDict, path:list[str]) -> JSONDict:
  data = schema.copy()
  data['items'] = process_schema(schema['items'], path+["items"])
  data['title'] = title(schema)
#  print(f"process_schema_array set title to {data['title']}")
  return data
# }}} process_schema_array

# {{{ get_type
@typechecked
def get_type(schema:JSONDict) -> str|None:
  if "type" in schema:
    return Jstr(schema, "type")
  if any(k in schema for k in ("allOf", "oneOf", "anyOf")):
    for key in ("allOf", "oneOf", "anyOf"):
      if key in schema:
        select = key
        break
    commonType = None
    for s in JDict(schema, select):
      t = get_type(castJDict(s))
      if t is not None:
        if commonType is None:
          commonType = t
        if t != commonType:
          ErrorHandler.fatal(f"Different types {commonType} {t} in selector", schema)
    return commonType
  if "pattern" in schema or "format" in schema:
    return "string"
  if "enum" in schema or "example" in schema:
    v = None
    if "example" in schema:
      v = schema['example']
    elif "enum" in schema:
      v = schema['enum'][0]
    if isinstance(v, dict):
      return "object"
    if isinstance(v, list):
      return "array"
    if isinstance(v, str):
      return "string"
    return None
  if "properties" in schema:
    return "object"
  return None
# }}} get_type

# {{{ process_schema
@typechecked
def process_schema(schema:JSONDict, path:list[str]) -> JSONDict|JSONList:
  if has_schema_selector(schema):
    return process_schema_selector(schema, path+["selector"])

  t = get_type(schema)
  if t == "object":
    return process_schema_object(schema, path+["object"])
  if t == "array":
    return process_schema_array(schema, path+["array"])
  if t in { "string", "boolean", "number", "integer", "anything", "null", }:
    return schema
  ErrorHandler.fatal(f"Unhandled type {t}", schema)
# }}} process_schema

# {{{ desc
@typechecked
def desc(schema:JSONDict) -> str:
  d = ""
  if 'title' in schema:
    d = d + '/' + schema['title'].replace('\n',' ')
  if 'description' in schema:
    d = d + '/' + schema['description'].replace('\n',' ')
  if 'summary' in schema:
    d = d + '/' + schema['summary'].replace('\n',' ')
  if d != '':
    return d[1:]
  return ""
# }}} desc

# {{{ title
@typechecked
def title(schema:JSONDict) -> str:
  if 'title' in schema:
    return Jstr(schema, 'title').replace('\n',' ')
  if 'summary' in schema:
    return Jstr(schema, 'summary').replace('\n',' ')
  if 'description' in schema:
    return Jstr(schema, 'description').replace('\n',' ')
  return ""
# }}} title


# {{{ get_schema_for_value
@typechecked
def get_schema_for_value(c:str) -> JSONDict:
  try:
    int(c)
    return {"type":"integer"}
  except ValueError:
    pass
  try:
    float(c)
    return {"type":"number"}
  except ValueError:
    pass
  if c in ("True", "False"):
    return {"type":"boolean"}
  return {"type":"string"}
# }}} get_schema_for_value



# vim: set sw=2 sts=2 ts=2 expandtab:
