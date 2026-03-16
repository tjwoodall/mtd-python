#!/usr/bin/env -S python3 -O

# typechecked is painfully slow! Remove -O to enable
# 60m vs <2m for make -j8 json

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

import json
import sys
import shutil
from copy import deepcopy

from pathlib import Path
from typing import Any, cast, NoReturn

from typeguard import typechecked

from mtd.JSONTypes import JSONType, JSONDict, JSONList, JDict, Jbool, Jstr, JList, castJDict
from mtd import ApiReader

# {{{
@typechecked
def print_stack(indent:str = "", one_line:bool=False, last_file:bool=False) -> None:
  if last_file:
    for r in ref_stack[::-1]:
      p = r.split('#',1)[0]
      if p.endswith(".yaml") or p.endswith(".json"):
        print(f"{indent}{r}")
        return
  if one_line:
    print(indent + ' / '.join(ref_stack))
    return
  for r in ref_stack:
    print(f"{indent}{r}")
    indent += "  "
# }}} print_stack

# {{{
@typechecked
def fatal(err:str, obj:JSONType) -> NoReturn:
  sys.stdout.flush()
  print("-------- FATAL --------", file=sys.stderr)
  print_stack()
  print("-----------------------", file=sys.stderr)
  print(json.dumps(obj, indent=2), file=sys.stderr)
  print("-----------------------", file=sys.stderr)
  raise RuntimeError(err)
# }}} fatal

# {{{
@typechecked
def rename_key(obj:JSONDict, src:str, dst:str, act:str|None = None) -> None:
  if src in obj:
    if dst in obj:
      fatal(f"{src} and {dst} in dict", obj)
    if act:
      print(f"Renaming key {src} to {dst} for {act}")
#      print_stack("  ", last_file=True)
#      print("--------------------")
#      print(json.dumps(obj, indent=2))
#      print("--------------------")
    obj[dst] = obj[src]
    del obj[src]
#    if act:
#      print(json.dumps(obj, indent=2))
#      print("--------------------")
# }}} rename_key

# {{{
@typechecked
def add_key(obj:JSONDict, key:str, value:JSONType, act:str|None = None) -> None:
  if key in obj:
    fatal(f"{key} already present", obj)
  if act:
    print(f"Adding key {key} with value {value} for {act}")
#    print_stack("  ", last_file=True)
#    print("--------------------")
#    print(json.dumps(obj, indent=2))
#    print("--------------------")
  obj[key] = value
#  if act:
#    print(json.dumps(obj, indent=2))
#    print("--------------------")
# }}} add_key

# {{{
@typechecked
def del_key(obj:JSONDict, key:str, act:str|None = None) -> None:
  if key in obj:
    if act:
      print(f"Deleting key {key} for {act}")
#      print_stack("  ", last_file=True)
#      print("--------------------")
#      print(json.dumps(obj, indent=2))
#      print("--------------------")
    del obj[key]
#    if act:
#      print(json.dumps(obj, indent=2))
#      print("--------------------")
# }}} del_key

# {{{
@typechecked
def change_value(obj:JSONDict, key:str, src:JSONType, dst:JSONType, act:str|None = None) -> None:
  if key in obj:
    if obj[key] == src:
      if act:
        print(f"Changing key {key} with value {src} to value {dst} for {act}")
#        print_stack("  ", last_file=True)
#        print("--------------------")
#        print(json.dumps(obj, indent=2))
#        print("--------------------")
      obj[key] = dst
#      if act:
#        print(json.dumps(obj, indent=2))
#        print("--------------------")
# }}} change_value

ref_stack:list[str] = []
# {{{
class RefResolver:
  major_key:str
  minor_key:str
# }}} class RefResolver

# {{{
@typechecked
def _validate_keys(obj:JSONDict, allowed_keys: set[str]) -> None:
  if set(obj.keys()) - allowed_keys:
    fatal(f"_validate_keys unexpected keys: {obj.keys()-allowed_keys}", obj)
# }}} _validate_keys

# N.B. allowed_keys is the set of keys allowed in the resolved object
# {{{
class RefTrackerBase:
  # {{{
  @typechecked
  def __init__(self, obj:JSONDict, key:str, allowed_keys:set[str]|None = None):
    if key not in obj:
      fatal(f"RefTracker missing key: {key}", obj)

    self.obj = cast(JSONType, obj[key])

    if allowed_keys is not None:
      _validate_keys(cast(JSONDict, self.obj), allowed_keys)

    ref_stack.append(f'{key}')
  # }}} __init__

  # {{{
  @typechecked
  def __enter__(self) -> JSONType:
    return self.obj
  # }}} __enter__

  # {{{
  @typechecked
  def __exit__(self, exc_type:Any, exc_value:Any, traceback:Any) -> None:
    ref_stack.pop()
  # }}} __exit__
# }}} class RefTracker

class RefTrackerDict(RefTrackerBase):
  # {{{
  @typechecked
  def __enter__(self) -> JSONDict:
    if not isinstance(self.obj, dict):
      fatal("Not a dict", self.obj)
    return cast(JSONDict, self.obj)
  # }}} __enter__

class RefTrackerList(RefTrackerBase):
  # {{{
  @typechecked
  def __enter__(self) -> JSONList:
    if not isinstance(self.obj, list):
      fatal("Not a list", self.obj)
    return cast(JSONList, self.obj)
  # }}} __enter__

# {{{
@typechecked
def process_schema_not(schema:JSONDict) -> None:
  process_schema(JDict(schema, "not"))
# }}} process_schema_not

# {{{
@typechecked
def process_schema_selector(schema:JSONDict, select:str) -> None:
  keys = {select, "description", "type", "example", "title", "required", "properties"}
  _validate_keys(schema, keys)

  for s in JList(schema, select):
    if set(s) != {"description"}:
      process_schema(cast(JSONDict, s))
# }}} process_schema_selector

# {{{
@typechecked
def process_schema_oneOf(schema:JSONDict) -> None:
  process_schema_selector(schema, "oneOf")
# }}} process_schema_oneOf

# {{{
@typechecked
def process_schema_allOf(schema:JSONDict) -> None:
  process_schema_selector(schema, "allOf")
# }}} process_schema_allOf

# {{{
@typechecked
def process_schema_anyOf(schema:JSONDict) -> None:
  process_schema_selector(schema, "anyOf")
# }}} process_schema_anyOf

# {{{
@typechecked
# pylint: disable=too-many-branches
def process_schema_string(schema:JSONDict) -> None:
  rename_key(schema, "minimum", "minLength", "string type")
  rename_key(schema, "maximum", "maxLength", "string type")

  # Fix dodgy formats with standard values
  if 'format' in schema:
    replace_me = {
      "^((?!(BG|GB|KN|NK|NT|TN|ZZ)|(D|F|I|Q|U|V)[A-Z]|[A-Z](D|F|I|O|Q|U|V))[A-Z]{2})[0-9]{6}[A-D]$": (None, "^((?!(BG|GB|KN|NK|NT|TN|ZZ)|(D|F|I|Q|U|V)[A-Z]|[A-Z](D|F|I|O|Q|U|V))[A-Z]{2})[0-9]{6}[A-D]$"),
      "YYYY-MM-DD_YYYY-MM-DD": (None, "^2[0-9]{3}-[0-1][0-9]-[0-3][0-9]_2[0-9]{3}-[0-1][0-9]-[0-3][0-9]$"),
      "YYYY-MM-DDThh:mm:ss.sssZ": ("date-time","^2[0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{0,3}Z$"),
      "YYYY-MM-DDThh:mm:ss.SSSZ": ("date-time","^2[0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{0,3}Z$"),
      "YYYY-YY": ("tax-year",None),
      "^2[0-9]{3}-[0-9]{2}$": ("tax-year",None),
      "YYYY-MM-DD": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "yyyy-MM-DD": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "[0-9]{4}-[0-9]{2}-[0-9]{2}$": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "full-date": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
    }
    if schema["format"] in replace_me:
      fmt = Jstr(schema, "format")
      del_key(schema, "format")
      if "pattern" in schema:
        del_key(schema, "pattern")
      if replace_me[fmt][0] is not None:
        add_key(schema, "format", replace_me[fmt][0], f"string type")
      if replace_me[fmt][1] is not None:
        add_key(schema, "pattern", replace_me[fmt][1], f"string type")

  # Convert patterns to standard formats
  if 'pattern' in schema:
    replace_me = {
      "yyyy-mm-dd": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "yyyy-MM-DD": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "YYYY-MM-DD": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      "^\\d{4}-\\d{2}-\\d{2}$": ("date","^\\d{4}-\\d{2}-\\d{2}$"),
      # Pattern limits datetime to ms
      "^2[0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]{0,3}|)Z$": ("date-time","^2[0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]{0,3}|)Z$"),
      # Pattern limits uuid to lower case.
      "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$": ("uuid","^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"),
    }
    if schema["pattern"] in replace_me:
      pattern = Jstr(schema, "pattern")
      if "format" in schema:
        del_key(schema, "format")
      del_key(schema, "pattern")
      if replace_me[pattern][0] is not None:
        add_key(schema, "format", replace_me[pattern][0], f"string type")
      if replace_me[pattern][1] is not None:
        add_key(schema, "pattern", replace_me[pattern][1], f"string type")

  # Replace dodgy id with format
  if 'id' in schema:
    replace_me = {
        "tax-year": ("tax-year",None),
        "full-date": ("date",None),
    }
    if schema["id"] in replace_me:
      rename_key(schema, "id", "format", "string type")
      fmt = Jstr(schema, "format")
      change_value(schema, "format", fmt, replace_me[fmt][0], f"string type {schema['format']}")

  if "enum" in schema:
    keys = {"enum", "type", "description", "title", "minLength", "maxLength", "nullable", "default", "example", "deprecated", "xml"}
    _validate_keys(schema, keys)
  elif "format" in schema or "pattern" in schema:
    keys = {'format', 'pattern', 'type', 'title', 'description', 'minLength', 'maxLength', 'example', 'deprecated', 'default', "nullable", }
    _validate_keys(schema, keys)
  elif "oneOf" in schema:
    process_schema_oneOf(schema)
  elif "allOf" in schema:
    process_schema_allOf(schema)
  elif "anyOf" in schema:
    process_schema_anyOf(schema)
  elif "not" in schema:
    process_schema_not(schema)
  else:
    keys = {"description", "type", "example", "minLength", "maxLength", "title", "default", "deprecated", "nullable", "xml", }
    _validate_keys(schema, keys)
# }}} process_schema_string

# {{{
@typechecked
def process_schema_boolean(schema:JSONDict) -> None:
  keys = {"type", "example", "description", "title", "enum", "nullable", "deprecated"}
  _validate_keys(schema, keys)
# }}} process_schema_boolean

# {{{
@typechecked
def process_schema_number(schema:JSONDict) -> None:
  keys = {"type", "example", "description", "title", "pattern", "multipleOf", "minimum", "maximum", "allOf", "deprecated", "format", "nullable", }
  _validate_keys(schema, keys)
# }}} process_schema_number

# {{{
@typechecked
def process_schema_integer(schema:JSONDict) -> None:
  keys = {"type", "description", "minimum", "maximum", "multipleOf", "title", "example", "allOf", "format", "exclusiveMinimum", "enum", "default", }
  _validate_keys(schema, keys)
# }}} process_schema_integer

# {{{
@typechecked
def process_schema_object(schema:JSONDict) -> None:
  keys = {"type",
      "properties",
      "required",
      "title",
      "description",
      "definitions",
      "example",
      "$id",
      "$schema",
      "additionalProperties",
      "oneOf",
      "anyOf",
      "allOf",
      "not",
      "xml",
      "nullable",
      }
  _validate_keys(schema, keys)
  if "oneOf" in schema:
    process_schema_oneOf(schema)
    return

  if "allOf" in schema:
    process_schema_allOf(schema)
    return

  if "anyOf" in schema:
    process_schema_anyOf(schema)
    return

  if "properties" not in schema:
    if "example" in schema:
      return
    if "additionalProperties" in schema and schema["additionalProperties"] is False:
      return
    if "type" in schema:
      return
    fatal("missing properties", schema)

  with RefTrackerDict(schema, "properties") as properties:
    for k in properties:
      if k == "_links":
        continue
      process_schema(JDict(properties, k))
# }}} process_schema_object

# {{{
@typechecked
def process_schema_array(schema:JSONDict) -> None:
  keys = {"type",
      "items",
      "uniqueItems",
      "description",
      "Description",
      "maxItems",
      "minItems",
      "additionalProperties",
      "title",
      "pattern",
      "example",
      "$schema",
      "$id",
      "nullable",}
  _validate_keys(schema, keys)
  with RefTrackerDict(schema, "items") as items:
    process_schema(items)
# }}} process_schema_array

# {{{
@typechecked
# pylint: disable=too-many-branches
def process_schema(schema:JSONDict) -> None:
  keys = {
    'type',
    'example',
    'examples',
    'enum',
    'description',
    'items',
    'title',
    'properties',
    'required',
    'oneOf',
    'allOf',
    'anyOf',
    'not',
    '$schema',
    'additionalProperties',
    'pattern',
    'format',
    'maximum',
    'minimum',
    'exclusiveMinimum',
    'minLength',
    'maxLength',
    'multipleOf',
    'definitions',
    '$id',
    'minItems',
    'maxItems',
    'nullable',
    'uniqueItems',
    'default',
    'id',
    'deprecated',
    '$ref',
    'xml',
    }
  _validate_keys(schema, keys)

  if "type" in schema:
    t = schema["type"]
    if t == "object":
      process_schema_object(schema)
    elif t == "array":
      process_schema_array(schema)
    elif t == "string":
      process_schema_string(schema)
    elif t == "boolean":
      process_schema_boolean(schema)
    elif t == "number":
      process_schema_number(schema)
    elif t == "integer":
      process_schema_integer(schema)
    else:
      fatal(f"Unhandled type {t}", schema)
  elif "allOf" in schema:
    process_schema_allOf(schema)
  elif "oneOf" in schema:
    process_schema_oneOf(schema)
  elif "anyOf" in schema:
    process_schema_anyOf(schema)
  elif "pattern" in schema or "format" in schema:
    process_schema_string(schema)
  elif "enum" in schema or "example" in schema:
    v = None
    if "enum" in schema:
      v = schema['enum'][0]
    elif "example" in schema:
      v = schema['example']
    if isinstance(v, dict):
      process_schema_object(schema)
    elif isinstance(v, list):
      process_schema_array(schema)
    elif isinstance(v, str):
      process_schema_string(schema)
    else:
      fatal(f"Unhandled example or enum {v}", schema)
  elif "properties" in schema:
    #add_key(schema, "type", "object")
    process_schema_object(schema)
  elif "xml" in schema:
    print(f"WARNING: ignored {json.dumps(schema, indent=2)}")
  else:
    print(f"WARNING: ignored {json.dumps(schema, indent=2)}")
    fatal("IGNORED", schema)
# }}} process_schema

# {{{
@typechecked
def process_response_headers(response:JSONDict) -> None:
  if "headers" not in response:
    return

  keys = {'Deprecation', "Link", "Sunset", 'Receipt-Signature', 'Receipt-ID', 'Receipt-Timestamp', }
  with RefTrackerDict(response, "headers", keys | {"Location", "X-CorrelationId", "Notification-Message-Id", "Notification-Box-Id", 'x-correlation-id', 'source', 'content-type', 'datetime'}) as headers:
    for k in keys:
      if k in headers:
        with RefTrackerDict(headers, k) as header:
          _validate_keys(header, {'description', 'name', 'required', 'schema', 'in', 'content'})
          # For completely unknown reasons, vat api is different to income tax api here.
          if 'content' in header:
            with RefTrackerDict(header, "content") as content:
              with RefTrackerDict(content, "text/plain") as text:
                with RefTrackerDict(text, "schema") as schema:
                  process_schema(schema)
          else:
            with RefTrackerDict(header, "schema") as schema:
              process_schema(schema)

    if "X-CorrelationId" in headers:
      with RefTrackerDict(headers, "X-CorrelationId") as header:
        _validate_keys(header, {'description', 'name', 'required', 'schema', 'in', 'type', 'content'})
        # For completely unknown reasons, vat api is different to income tax api here.
        if 'content' in header:
          with RefTrackerDict(header, "content") as content:
            with RefTrackerDict(content, "text/plain") as text:
              with RefTrackerDict(text, "schema") as schema:
                process_schema(schema)
        else:
          with RefTrackerDict(header, "schema") as schema:
            process_schema(schema)

    if "Location" in headers:
      with RefTrackerDict(headers, "Location") as header:
        _validate_keys(header, {'description', 'schema'})
        with RefTrackerDict(header, "schema") as schema:
          process_schema(schema)
# }}} process_response_headers

# {{{
@typechecked
def process_content(response:JSONDict) -> None:
  if "content" not in response or response["content"] == {}:
    return

  keys = {"application/json", 'application/json+xml', 'application/xml', 'application/vnd.hmrc.1.0+json', 'application/vnd.hmrc.1.0+xml', 'text/plain'}
  with RefTrackerDict(response, "content", keys) as content:
    for k in keys:
      if k in content:
        if k in {'application/json', 'application/json+xml'}:
          with RefTrackerDict(content, k, {'schema', 'examples', 'example', }) as app:
            with RefTrackerDict(app, "schema") as schema:
              process_schema(schema)
        elif k in {'application/xml'}:
          pass
        else:
          print(f"Warning: Skipping {k} in response")
# }}} process_content

# {{{
@typechecked
def process_response(response:JSONDict) -> None:
  _validate_keys(response, {'content', 'description', "headers"})
  process_response_headers(response)
  process_content(response)
# }}} process_response

# {{{
@typechecked
def process_security(security_list:JSONList) -> None:
  if len(security_list) != 1:
    fatal("only expected one security", security_list)

  security = JDict(security_list, 0)
  normalise_security_keys(security)

  if len(security) == 0:
    return #unrestricted endpoint

  if len(security) != 1:
    fatal("only expected one restriction type", security)

  k = list(security.keys())[0]
  vl = JList(security, k)

  if len(vl) == 0:
    v=""
  elif len(vl) == 1:
    v=Jstr(vl, 0)
  else:
    fatal("Unknown security", security)

  if (k,v) not in {
            ("Application-Restricted", ''),
            ("Application-Restricted", 'write:notifications'),
            ("Application-Restricted", 'write:self-assessment'),
            ("Application-Restricted", 'read:self-assessment'),
            ("Application-Restricted", 'read:pull-notifications'),
            ("User-Restricted", ''),
            ("User-Restricted", 'all:business-rates'),
            ("User-Restricted", 'write:import-control-system'),
            ("User-Restricted", 'write:customs-declaration'),
            ("User-Restricted", 'write:customs-declarations-information'),
            ("User-Restricted", 'common-transit-convention-traders'),
            ("User-Restricted", 'common-transit-convention-guarantee-balance'),
            ("User-Restricted", 'excise-movement-control-system'),
            ("User-Restricted", 'trader-goods-profiles-test-support'),
            ("User-Restricted", 'trader-goods-profiles'),
            ("User-Restricted", 'read:sent-invitations'),
            ("User-Restricted", 'write:sent-invitations'),
            ("User-Restricted", 'write:cancel-invitations'),
            ("User-Restricted", 'read:check-relationship'),
            ("User-Restricted", 'read:self-assessment'),
            ("User-Restricted", 'write:self-assessment'),
            ("User-Restricted", 'read:vat'),
            ("User-Restricted", 'write:vat'),
            ("User-Restricted", 'write:relationships'),
            ("User-Restricted", "read:self-assessment-assist"),
            ("User-Restricted", "write:self-assessment-assist"),
            ("User-Restricted", "write:goods-movement-system"),
            ("User-Restricted", "write:import-control-system-2"),
            ("User-Restricted", "read:individual-benefits"),
            ("User-Restricted", "read:individual-employment"),
            ("User-Restricted", "read:individual-income"),
            ("User-Restricted", "read:individual-tax"),
            ("User-Restricted", "read:marriage-allowance"),
            ("User-Restricted", "read:national-insurance"),
            ("User-Restricted", 'read:ras'),
            ("User-Restricted", 'read:lisa'),
            ("User-Restricted", 'write:lisa'),
            ("User-Restricted", 'read:isa-returns'),
            ("User-Restricted", 'write:isa-returns'),
            ("User-Restricted", 'write:interest-restriction-return'),
            ("User-Restricted", 'read:pillar2'),
            ("User-Restricted", 'write:pillar2'),
            ("User-Restricted", 'read:native-apps-api-orchestration'),
            ("User-Restricted", 'write:customs-inventory-linking-exports'),
            ("User-Restricted", 'write:customs-il-imports-movement-validation'),
            ("User-Restricted", 'write:customs-il-imports-arrival-notifications'),

            # api-example-microservice
            ("User-Restricted", 'hello'),
          }:
    fatal("Unknown access type", security)
# }}} process_security

# {{{
@typechecked
def process_parameters(request:JSONDict) -> None:
  if "parameters" not in request:
    return

  with RefTrackerList(request, "parameters") as parameters:
    for param in parameters:
      _validate_keys(cast(JSONDict,param), {'schema', 'required', 'in', 'style', 'description', 'name', 'explode', "example", "examples"})
      param_dict = cast(JSONDict, param)
      with RefTrackerDict(param_dict, 'schema', {'example', 'type', 'enum', 'pattern', 'description', "allOf", "minLength", "maxLength", "format", "default", "minimum", "maximum", }) as header:
        process_schema(header)
# }}} process_parameters

# {{{
@typechecked
def process_action(action:JSONDict) -> None:
  process_parameters(action)

  with RefTrackerList(action, 'security') as security:
    process_security(security)

  if "requestBody" in action:
    with RefTrackerDict(action, 'requestBody', {'required', 'content', 'description', }) as body:
      keys = {'application/json', 'application/x-ndjson', 'application/xml'}
      with RefTrackerDict(body, 'content', keys) as body:
        for k in keys:
          if k in body:
            if k == 'application/xml':
              print('WARNING: Ignoring application/xml')
            else:
              with RefTrackerDict(body, k, {'schema', 'examples', 'example', }) as body:
                with RefTrackerDict(body, 'schema') as schema:
                  process_schema(schema)

  with RefTrackerDict(action, 'responses', { '200', '201', '202', '204', '400', '401', '403', '404', '405', '406', '409', '410', '413', '415', '422', '429', '500', '501', '503', '504', }) as responses:
    for k in responses:
      with RefTrackerDict(responses, k) as response:
        process_response(response)
# }}} process_action

# Iterate through every action on the endpoint
# {{{
@typechecked
def process_ep(ep:JSONDict) -> None:
  for action_key in ep:
    if action_key == 'parameters':
      continue
    with RefTrackerDict(ep, action_key) as action:
      valid_keys = {'operationId',
              'parameters',
              'deprecated',
              'security',
              'tags',
              'summary',
              'responses',
              'description',
              'requestBody'}

      _validate_keys(action, valid_keys)
      if "add test only" in ApiReader.extraconfig:
        if 'summary' in action and ' [test only]' not in Jstr(action, "summary"):
          if not ApiReader.endpoint_switch("api", RefResolver.major_key, RefResolver.minor_key, True):
            action["summary"] = Jstr(action, "summary") + ' [test only]'
      process_action(action)
# }}} process_ep

# Iterate through every endpoint
# {{{
@typechecked
def process_endpoints(endpoints:JSONDict) -> None:
  for ep_key in endpoints:
    keys = {
        'delete',
        'get',
        'post',
        'put',
        'parameters',
        'patch',
        }
    with RefTrackerDict(endpoints, ep_key, keys) as ep:
      process_ep(ep)
# }}} process_endpoints

# {{{
@typechecked
def normalise_security_keys(security:JSONDict) -> None:
  keys = {
      "userRestricted",
      "user-restricted",
      "User-Restricted",
      "applicationRestricted",
      "application-restricted",
      "Application-Restricted",
      }
  _validate_keys(security, keys)
  rename_key(security, 'userRestricted', 'User-Restricted')
  rename_key(security, 'applicationRestricted', 'Application-Restricted')
  rename_key(security, 'user-restricted', 'User-Restricted')
  rename_key(security, 'application-restricted', 'User-Restricted')
# }}}

# {{{
@typechecked
def process(api:JSONDict) -> None:
  keys = { 'paths', 'info', 'tags', 'servers', 'components', 'openapi', }
  _validate_keys(api, keys)

  with RefTrackerDict(api, "components", {"securitySchemes", "examples", "parameters", "schemas", "responses", "headers"}) as components:
    for k in list(components.keys()):
      if k == "securitySchemes":
        keys = { "userRestricted",
             "applicationRestricted",
             "user-restricted",
             "application-restricted",
             "User-Restricted",
             "Application-Restricted",
            }
        with RefTrackerDict(components, "securitySchemes", keys) as securitySchemes:
          normalise_security_keys(securitySchemes)
      else:
        del components[k]
  if JDict(api, 'components') == {}:
    del api['components']
  if "add test only" in ApiReader.extraconfig:
    if 'info' in api and 'title' in JDict(api, 'info') and ' [test only]' not in Jstr(JDict(api, "info"), "title"):
      if not ApiReader.endpoint_switch("api", RefResolver.major_key, RefResolver.minor_key, True):
        JDict(api, "info")["title"] = Jstr(JDict(api, "info"), "title") + ' [test only]'
  with RefTrackerDict(api, "paths") as endpoints:
    process_endpoints(endpoints)
# }}} process

#####################################

if len(sys.argv) < 3:
  sys.exit(1)

no_deprecated = True
production_only = False

if sys.argv[1] == '--include-deprecated':
  no_deprecated = False
  del sys.argv[1]

if sys.argv[1] == '--production-only':
  production_only = True
  del sys.argv[1]

# 1   2   3    4           5
# API OUT CONF EXTRACONFIG YAML
if len(sys.argv) != 6:
  sys.exit(1)

if Path(sys.argv[2]).exists():
  with open(sys.argv[2], 'r', encoding="utf-8") as f:
    application = json.load(f)
else:
  application = {}

with open(sys.argv[3], "r", encoding="utf-8") as f:
  config = json.load(f)

if Path(sys.argv[4]).exists():
  with open(sys.argv[4], "r", encoding="utf-8") as f:
    extraconfig = json.load(f)
else:
  extraconfig = {}

ApiReader.api_key = sys.argv[1]

root = Path(sys.argv[5])
# national-insurance/resources/public/api/conf/1.1/application.yaml
RefResolver.major_key,RefResolver.minor_key = root.parts[-2].split(".")
ApiReader.prefix_end = len(root.parts)-1

confkey = ApiReader.api_key+"/conf/application.conf"
if confkey not in extraconfig:
  extraconfig[confkey] = {}

ApiReader.config = config[confkey]
ApiReader.extraconfig = extraconfig[confkey]

skipping = False

if "api" not in ApiReader.config or \
    RefResolver.major_key not in JDict(ApiReader.config, "api") or \
    RefResolver.minor_key not in JDict(JDict(ApiReader.config, "api"), RefResolver.major_key):
  print(f"Skipping NO CONFIG {root}")
  skipping = True
else:
  confapi = JDict(JDict(JDict(ApiReader.config, "api"), RefResolver.major_key), RefResolver.minor_key)

  if not Jbool(JDict(confapi, "endpoints"), "api-released-in-production") and production_only:
    print(f"Skipping non-production {root}")
    skipping = True

  if confapi["status"] == "RETIRED":
    print(f"Skipping RETIRED {root}")
    skipping = True

  if confapi["status"] == "DEPRECATED" and no_deprecated:
    print(f"Skipping DEPRECATED {root}")
    skipping = True

if ApiReader.api_key not in application:
  application[ApiReader.api_key] = {}
if RefResolver.major_key not in application[ApiReader.api_key]:
  application[ApiReader.api_key][RefResolver.major_key] = {}
if RefResolver.minor_key not in application[ApiReader.api_key][RefResolver.major_key]:
  application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key] = {}

application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key] = {}
api = application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key]

if f"{ApiReader.api_key}.{RefResolver.major_key}.{RefResolver.minor_key}" in ("individual-calculations-api.9.0", "individuals-other-income-api.3.0"):
  ApiReader.extraconfig["add test only"] = True

# Sometimes there are versions already published to github that aren't yet on the webscrape
if root.exists() and not skipping:
  # Note that this updates both api and extraconfig (where appropriate)
  ApiReader.convert(api, root)

  # This is painfully slow when typechecked.

  # {{{
  @typechecked
  def ref_resolver(api:JSONDict, obj:JSONType, path:list[str]) -> JSONType:
  #  logger.debug(f"path={path}")

    # {{{
    @typechecked
    def resolve(api:JSONDict, obj:JSONType) -> JSONType:
      if not isinstance(obj, dict) or "$ref" not in obj:
        return obj

      assert isinstance(obj["$ref"], str), "$ref is not a string!"
      target = obj["$ref"].split('#')

      assert isinstance(api, dict), "resolved api is not a JSONDict"
      resolvedobj:JSONType = deepcopy(api[target[0]])

      if len(target) == 2:
        for key in target[1].split("/")[1:]:
          resolvedobj = castJDict(resolvedobj)
          resolvedobj = resolvedobj[key]

      if not isinstance(resolvedobj, dict):
        if len(obj.keys()) != 1:
          fatal("Resolved to {resolvedobj} but parent has extra keys", obj)
        return resolvedobj

      resolvedobj = castJDict(resolvedobj)

      for k,v in obj.items():
        if k != "$ref":
          resolvedobj[k] = deepcopy(v)

      # We must not copy $id as it has to be unique which can only be true in an unresolved schema
      if "$id" in cast(JSONDict, resolvedobj):
        del cast(JSONDict, resolvedobj)["$id"]

      return resolvedobj
    # }}} resolve

    resolved = resolve(api, obj)

    if isinstance(resolved, dict):
      while "$ref" in cast(JSONDict, resolved):
        resolved = resolve(api, resolved)

      resolved = {k: ref_resolver(api, v, path + [k]) for k,v in cast(JSONDict, resolved).items() }
      if "definitions" in resolved:
        del resolved["definitions"]
    elif isinstance(resolved, list):
      resolved = [ ref_resolver(api, v, path + [f"[{idx}]"]) for idx,v in enumerate(resolved) ]
    return resolved
  # }}} ref_resolver

  api = ref_resolver(api, api[f"file:///{ApiReader.api_key}/application.yaml"], [])

  # Helper to track down unserializable objects if they happen
  # def find_unserializable(obj, path="root"):
  #   try:
  #     json.dumps(obj)
  #     return  # It's serializable — nothing to report
  #   except TypeError:
  #     if isinstance(obj, dict):
  #       for k, v in obj.items():
  #         find_unserializable(v, f"{path}.{k}")
  #     elif isinstance(obj, list):
  #       for i, item in enumerate(obj):
  #         find_unserializable(item, f"{path}[{i}]")
  #     else:
  #       print(f"  Unserializable at {path}: {type(obj).__name__} -> {repr(obj)}")
  # find_unserializable(api)

  process(api)
  application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key] = api

extraconfig = {k: v for k,v in extraconfig.items() if v != {}}

def sort_keys(obj:JSONType, done:bool=False) -> JSONType:
  if done:
    return obj
  if isinstance(obj, dict):
    return { k: sort_keys(v, k == "schema") for k,v in sorted(obj.items(), key=lambda x: x[0]) }
  if isinstance(obj, list):
    return [ sort_keys(x) for x in obj ]
  return obj

def normalize_numbers(obj:JSONType) -> JSONType:
  if isinstance(obj, float) and obj.is_integer():
    return int(obj)
  if isinstance(obj, dict):
    return {k: normalize_numbers(v) for k, v in obj.items()}
  if isinstance(obj, list):
    return [normalize_numbers(v) for v in obj]
  return obj

with open(sys.argv[4] + ".tmp", 'w', encoding="utf-8") as json_file:
  json_file.write(json.dumps(extraconfig, indent=2, sort_keys=True) + "\n")

#for apikey,api in application.items():
#  for _,major in api.items():
#    for k,minor in major.items():
#      if f"file:///{apikey}/application.yaml" in minor:
#        major[k] = ref_resolver(minor, minor[f"file:///{apikey}/application.yaml"])

with open(sys.argv[2] + ".tmp", 'w', encoding="utf-8") as json_file:
  json_file.write(json.dumps(normalize_numbers(sort_keys(application)), indent=2) + "\n")

# Atomically move to final path (overwrites if exists)
if Path(sys.argv[2] + ".tmp").exists():
  shutil.move(sys.argv[2] + ".tmp", sys.argv[2])
if Path(sys.argv[4] + ".tmp").exists():
  shutil.move(sys.argv[4] + ".tmp", sys.argv[4])

# vim: set sw=2 sts=2 ts=2 expandtab:
