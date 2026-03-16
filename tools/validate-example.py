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

import json
import sys
from typing import Any, cast, NoReturn
from collections.abc import Mapping, Hashable

from typeguard import typechecked
import openapi_spec_validator

from mtd.JSONTypes import JSONType, JSONDict, JSONList, JDict, Jstr, JList
from mtd.Validate import Validator

# {{{
@typechecked
def validate_examples(schema:JSONDict, body:JSONDict) -> None:
#  print(f'validating: {json.dumps({"schema": schema, "example": body}, indent=2, sort_keys=True)}')
  if 'example' in body:
    with RefTrackerBase(body, 'example') as example:
      Validator.validate(example, schema)

  if 'enum' in body:
    with RefTrackerList(body, "enum") as enum:
      for example in enum:
        Validator.validate(example, schema)

  if 'examples' in body:
    with RefTrackerDict(body, 'examples') as body_:
      for k in body_:
        with RefTrackerDict(body_, k, {'value', 'description', 'summary', }) as keyed_example:
          with RefTrackerBase(keyed_example, 'value') as example:
            Validator.validate(example, schema)
# }}} validate_examples

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
  print("-------- FATAL --------")
  print_stack()
  print("-----------------------")
  print(json.dumps(obj, indent=2, sort_keys=True))
  print("-----------------------")
  raise RuntimeError(err)
# }}} fatal

ref_stack : list[str] = []
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
  validate_examples(schema, schema)
  process_schema(JDict(schema, "not"))
# }}} process_schema_not

# {{{
@typechecked
def process_schema_selector(schema:JSONDict, select:str) -> None:
  keys = {select, "description", "type", "example", "title", "required", "properties"}
  _validate_keys(schema, keys)
  validate_examples(schema, schema)

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
def process_schema_string(schema:JSONDict) -> None:
  validate_examples(schema, schema)

  if "enum" in schema:
    keys = {"enum", "type", "description", "title", "minLength", "maxLength", "nullable", "default", "example", "deprecated", "xml"}
    _validate_keys(schema, keys)
  elif "format" in schema or "pattern" in schema:
    # TODO - find places where pattern/format are inconsistent
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
  validate_examples(schema, schema)
  keys = {"type", "example", "description", "title", "enum", "nullable", "deprecated"}
  _validate_keys(schema, keys)
# }}} process_schema_boolean

# {{{
@typechecked
def process_schema_number(schema:JSONDict) -> None:
  validate_examples(schema, schema)
  keys = {"type", "example", "description", "title", "pattern", "multipleOf", "minimum", "maximum", "allOf", "deprecated", "format", "nullable", }
  _validate_keys(schema, keys)
# }}} process_schema_number

# {{{
@typechecked
def process_schema_integer(schema:JSONDict) -> None:
  validate_examples(schema, schema)
  keys = {"type", "description", "minimum", "maximum", "multipleOf", "title", "example", "allOf", "format", "exclusiveMinimum", "enum", "default", }
  _validate_keys(schema, keys)
# }}} process_schema_integer

# {{{
@typechecked
def process_schema_object(schema:JSONDict) -> None:
  validate_examples(schema, schema)
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
  validate_examples(schema, schema)
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
def process_schema(schema:JSONDict) -> None:
  validate_examples(schema, schema)
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
                  validate_examples(schema, text)
          else:
            with RefTrackerDict(header, "schema") as schema:
              process_schema(schema)
              validate_examples(schema, header)

    if "X-CorrelationId" in headers:
      with RefTrackerDict(headers, "X-CorrelationId") as header:
        _validate_keys(header, {'description', 'name', 'required', 'schema', 'in', 'type', 'content'})
        # For completely unknown reasons, vat api is different to income tax api here.
        if 'content' in header:
          with RefTrackerDict(header, "content") as content:
            with RefTrackerDict(content, "text/plain") as text:
              with RefTrackerDict(text, "schema") as schema:
                process_schema(schema)
                validate_examples(schema, text)
        else:
          with RefTrackerDict(header, "schema") as schema:
            process_schema(schema)
            validate_examples(schema, header)

    if "Location" in headers:
      with RefTrackerDict(headers, "Location") as header:
        _validate_keys(header, {'description', 'schema'})
        with RefTrackerDict(header, "schema") as schema:
          process_schema(schema)
          validate_examples(schema, header)
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
              validate_examples(schema, app)
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
  _validate_keys(security, {'User-Restricted', 'Application-Restricted', })

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
            ("User-Restricted", 'write:customs-inventory-linking-exports'),

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
        validate_examples(header, param_dict)
# }}} process_parameters

# {{{
@typechecked
def process_action(action:JSONDict) -> None:
  process_parameters(action)

  if "requestBody" in action:
    with RefTrackerDict(action, 'requestBody', {'required', 'content', 'description', }) as body:
      keys = {'application/json', 'application/x-ndjson', 'application/xml'}
      with RefTrackerDict(body, 'content', keys) as body:
        #FIXME - we don't properly support x-ndjson - that's one json object per line - we'll send an array
        for k in keys:
          if k in body:
            if k == 'application/xml':
              print('WARNING: Ignoring application/xml')
            else:
              with RefTrackerDict(body, k, {'schema', 'examples', 'example', }) as body:
                with RefTrackerDict(body, 'schema') as schema:
                  process_schema(schema)
                  validate_examples(schema, body)

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
      print_stack(one_line=True)
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

# Get the endpoints for every minor version
# {{{
@typechecked
def process_major(major:JSONDict) -> None:
  # {{{
  @typechecked
  def remove_keys(spec:JSONType, keys:set[str]) -> JSONType:
    if isinstance(spec, dict):
      return { k: remove_keys(v, keys) for k, v in spec.items() if k not in keys }
    if isinstance(spec, list):
      return [remove_keys(item, keys) for item in spec]
    return spec
  # }}} remove_keys
  for minor_key in major:
    keys = {
        'paths',
        'info',
        'servers',
        'tags',
        'components',
        'openapi',
        }
    with RefTrackerDict(major, minor_key, keys) as minor:
      print_stack(one_line=True)
      if minor != {}:
        openapi_spec_validator.validate(cast(Mapping[Hashable, Any], remove_keys(minor, {'$schema', '$id', })))
      if "paths" in minor:
        with RefTrackerDict(minor, "paths") as endpoints:
          process_endpoints(endpoints)
# }}} process_major

# Iterate through every major version in the API
# {{{
@typechecked
def process_api(api:JSONDict) -> None:
  for major_key in api:
    with RefTrackerDict(api, major_key) as major:
      process_major(major)
# }}} process_api

# Iterate through every API
# {{{
@typechecked
def process(obj:JSONDict) -> None:
  for api_key in obj:
    with RefTrackerDict(obj, api_key) as api:
      process_api(api)
# }}} process

with open(sys.argv[1], "r", encoding="utf-8") as f:
  application = json.load(f)

process(application)

# vim: set sw=2 sts=2 ts=2 expandtab:
