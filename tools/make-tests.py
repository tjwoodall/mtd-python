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
import os
import copy
from typing import Any, cast, NoReturn

from typeguard import typechecked

from mtd.JSONTypes import JSONType, JSONDict, JSONList, castJDict

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

# {{{ pretty_json
@typechecked
def pretty_json(obj:JSONDict) -> str:
  r:str = "{\n"
  r += '  "press": [\n'
  for idx,l in enumerate(obj['setup']['press']):
    r += '    ' + json.dumps(l)
    if idx != len(obj['setup']['press'])-1:
      r += ','
    r += '\n'
  r += '  ]\n'
  r += '}\n'
  return r
# }}} pretty_json

# {{{
@typechecked
def process_action(action:JSONDict, submit:JSONDict) -> None:
  s = copy.deepcopy(submit)
  data = s.pop("data", None)
  prefix=f"{data['_api']}.{data['_major']}.{data['_minor']}"
  fn = f"tests/example/{prefix}.{data['_path'].replace('/','_')}-{data['_action']}.example.json"
  if os.path.exists(fn):
    print(f"{fn} exists, skipping")
    return

  s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_server", "Sandbox"])
  s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_id", "nino-1"])

  print(f"Writing {fn}")
  with open(fn, "w", encoding="utf-8") as f:
    f.write(pretty_json(s))
# }}} process_action

# Iterate through every action on the endpoint
# {{{
@typechecked
def process_endpoint(endpoint:JSONDict, submit:JSONDict) -> None:
  for action_key in endpoint:
    if action_key == 'parameters':
      continue
    with RefTrackerDict(endpoint, action_key) as action:
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
      s = copy.deepcopy(submit)
      s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_action", action_key])
      s['data']['_action'] = action_key
      process_action(action, s)
# }}} process_endpoint

# Iterate through every endpoint
# {{{
@typechecked
def process_minor(minor:JSONDict, submit:JSONDict) -> None:
  for ep_key in minor:
    keys = {
        'delete',
        'get',
        'post',
        'put',
        'parameters',
        'patch',
        }
    with RefTrackerDict(minor, ep_key, keys) as endpoint:
      s = copy.deepcopy(submit)
      s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_path", ep_key])
      s['data']['_path'] = ep_key
      process_endpoint(endpoint, s)
# }}} process_minor

# Get the endpoints for every minor version
# {{{
@typechecked
def process_major(major:JSONDict, submit:JSONDict) -> None:
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
      if "paths" in minor:
        with RefTrackerDict(minor, "paths") as endpoints:
          s = copy.deepcopy(submit)
          s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_minor", minor_key])
          s['data']['_minor'] = minor_key
          process_minor(endpoints, s)
# }}} process_major

# Iterate through every major version in the API
# {{{
@typechecked
def process_api(api:JSONDict, submit:JSONDict) -> None:
  for major_key in api:
    with RefTrackerDict(api, major_key) as major:
      s = copy.deepcopy(submit)
      s['setup']['press'].append(["EDIT", "MAIN", "", "json", "_major", major_key])
      s['data']['_major'] = major_key
      process_major(major, s)
# }}} process_api

# Iterate through every API
# {{{
@typechecked
def process(obj:JSONDict) -> None:
  submit:dict[str,JSONType] = { "setup": { "press": [] }, "data": {} }
  for api_key in obj:
    with RefTrackerDict(obj, api_key) as api:
      s = copy.deepcopy(submit)
      castJDict(s['setup'])['press'].append(["EDIT", "MAIN", "", "json", "_api", api_key])
      castJDict(s['data'])['_api'] = api_key
      process_api(api, s)
# }}} process

with open(sys.argv[1], "r", encoding="utf-8") as f:
  application = json.load(f)

process(application)

# vim: set sw=2 sts=2 ts=2 expandtab:
