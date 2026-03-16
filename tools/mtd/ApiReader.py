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
from collections.abc import Generator

import json
import sys
import re
import os

from pathlib import Path
from typing import Any, cast

import ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.resolver import Resolver
from ruamel.yaml.constructor import RoundTripConstructor

from typeguard import typechecked

from .JSONTypes import JSONType, JSONDict, JDict, Jbool

api_key:str = ""
prefix_end:int = 0
config:JSONDict = {}
extraconfig:JSONDict = {}

# Step 1: Remove implicit resolvers for timestamps (no autodetect)
for ch in list(Resolver.yaml_implicit_resolvers):
  Resolver.yaml_implicit_resolvers[ch] = [
    (tag, regexp)
    for tag, regexp in Resolver.yaml_implicit_resolvers[ch]
    if tag != 'tag:yaml.org,2002:timestamp'
  ]

# Step 2: Override the timestamp constructor to return strings
# {{{
@typechecked
def timestamp_as_str_constructor(loader:ruamel.yaml.constructor.RoundTripConstructor, node:ruamel.yaml.nodes.Node) -> Any:
  return loader.construct_scalar(node)
# }}} timestamp_as_str_constructor

RoundTripConstructor.add_constructor(
  'tag:yaml.org,2002:timestamp', timestamp_as_str_constructor
)

# {{{
@typechecked
def feature_switch(control:str, key:str, default:bool) -> bool:
  def feature_switch_impl(control:str, key:str, default:bool) -> bool:
    if "feature-switch" in config:
      fs = JDict(config, "feature-switch")
      if control in fs:
        ctrl = JDict(fs, control)
        if key in ctrl:
          return Jbool(ctrl, key)

    if "feature-switch" not in extraconfig:
      extraconfig["feature-switch"] = {}
    fs = JDict(extraconfig, "feature-switch")

    if control not in fs:
      fs[control] = {}
    ctrl = JDict(fs, control)

    if key not in ctrl:
      print(f"Setting not in config: returning {default} for {control}.{key}")
      ctrl[key] = default

    return default

  # Split the individual quoted feature names.
  features = re.findall(r"""['"]([^'"]+)['"]""", control)

  enabled = False
  for feature in features:
    result = feature_switch_impl(feature, key, default)
    enabled = enabled or result

  return enabled

# }}} feature_switch

# {{{
@typechecked
def endpoint_switch_defaulter(endpoint:str, major:str, minor:str, default:bool) -> bool:
  if "api" not in extraconfig:
    extraconfig["api"] = {}
  apiextraconfig = JDict(extraconfig, "api")
  if major not in apiextraconfig:
    apiextraconfig[major] = {}
  apiextraconfig = JDict(apiextraconfig, major)
  if minor not in apiextraconfig:
    apiextraconfig[minor] = {}
  apiextraconfig = JDict(apiextraconfig, minor)
  if "endpoints" not in apiextraconfig:
    apiextraconfig["endpoints"] = {}
  apiextraconfig = JDict(apiextraconfig, "endpoints")
  if f"{endpoint}-released-in-production" in apiextraconfig:
    return Jbool(apiextraconfig, f"{endpoint}-released-in-production")
  if f"api-released-in-production" in apiextraconfig:
    return Jbool(apiextraconfig, f"api-released-in-production")
  print(f"Setting not in config: returning {default} for {endpoint}-released-in-production in {api_key} {major}.{minor}")
  apiextraconfig[f"{endpoint}-released-in-production"] = default
  return default
# }}} endpoint_switch_defaulter


# {{{
@typechecked
def endpoint_switch(endpoint:str, major:str, minor:str, default:bool) -> bool:
  if "api" not in config:
    return endpoint_switch_defaulter(endpoint, major, minor, default)
  apiconfig = JDict(config, "api")
  if major not in apiconfig:
    return endpoint_switch_defaulter(endpoint, major, minor, default)
  apiconfig = JDict(apiconfig, major)
  if minor not in apiconfig:
    return endpoint_switch_defaulter(endpoint, major, minor, default)
  apiconfig = JDict(apiconfig, minor)
  if "endpoints" not in apiconfig:
    return endpoint_switch_defaulter(endpoint, major, minor, default)
  apiconfig = JDict(apiconfig, "endpoints")
  if "released-in-production" in apiconfig and endpoint in JDict(apiconfig, "released-in-production"):
    return Jbool(JDict(apiconfig, "released-in-production"), endpoint)
  if f"api-released-in-production" in apiconfig:
    return Jbool(apiconfig, f"api-released-in-production")
  return endpoint_switch_defaulter(endpoint, major, minor, default)
# }}} endpoint_switch

# {{{
@typechecked
def preprocess(file: Path) -> list[str]:

  configstack:list[bool] = [ True ]

  # To match redocly, we need to preserve knowledge of whether the file ended
  # in a trailing '\n' when importing xml files
  with open(file, 'r', encoding="utf-8") as f:
    text = f.read()
    lines:list[str|None] = list(text.splitlines())
    if text.endswith('\n'):
      lines.append("")

  for i, line in enumerate(lines):
    controls:list[str] = re.split(r"(\{\{.*?\}\})", cast(str,line))
    lines[i] = None
    hasControl = False

    for control in controls:
      if control.endswith("') }}") or control.endswith('") }}'):
        control = control[0:-3] + "}}"
      if control == '' and len(control) > 1:
        continue
      if control == "{{/if}}":
        hasControl = True
        configstack.pop()
        if not configstack:
          raise RuntimeError(f"Failed to preprocess")
      elif control == "{{/unless}}":
        hasControl = True
        # TODO we should match ifs and unlesses
        configstack.pop()
        if not configstack:
          raise RuntimeError(f"Failed to preprocess")
      elif control == "{{else}}":
        hasControl = True
        # TODO - think this should require if in the config stack
        if len(configstack) == 1:
          raise RuntimeError(f"Else without if")
        configstack[-1] = not configstack[-1]
      elif (control.startswith("{{#maybeTestOnly '") and control.endswith("'}}")) or \
          (control.startswith('{{#maybeTestOnly "') and control.endswith('"}}')):
        hasControl = True
        control = control[18:-3]
        v,e = control.split(" ")
        ma,mi = v.split(".")
        if all(configstack):
          if not endpoint_switch(e, ma, mi, True):
            if lines[i] is None:
              raise RuntimeError("Adding [test only] to None")
            lines[i] = cast(str, lines[i]) + " [test only]" # Why does mypy need this cast?

        # if endpointReleasedInProduction "" else " [test only]"
        # Takes a version and an endpoint as a string e.g.:
        # "3.0 high-income-child-benefit-charge-retrieve"
      elif control == "{{/maybeTestOnly}}":
        hasControl = True
      elif (control.startswith("{{#if (enabled '") and control.endswith("')}}")) or \
          (control.startswith('{{#if (enabled "') and control.endswith('")}}')):
        hasControl = True
        control = control[15:-3]
        configstack.append(feature_switch(control, "enabled", True))
#        print(f"Pushed {configstack[-1]} {control} on {api_key} {xmajor_key} {xminor_key}")
      elif (control.startswith("{{#unless (enabled '") and control.endswith("')}}")) or \
          (control.startswith('{{#unless (enabled "') and control.endswith('")}}')):
        hasControl = True
        control = control[19:-3]
        configstack.append(not feature_switch(control, "enabled", True))
#        print(f"Pushed {not configstack[-1]} {control} on {api_key} {xmajor_key} {xminor_key}")
      elif (control.startswith("{{#unless (releasedInProduction '") and control.endswith("')}}")) or \
          (control.startswith('{{#unless (releasedInProduction "') and control.endswith('")}}')):
        hasControl = True
        control = control[32:-3]
        configstack.append( \
            not feature_switch(control, "released-in-production", True))
#        print(f"Pushed {not configstack[-1]} {control} on {api_key} {xmajor_key} {xminor_key}")
      elif control.startswith("{{#"):
        hasControl = True
        raise RuntimeError(f"Don't know how to parse {control}")
      elif all(configstack):
#        print(f"Added {control}")
        lines[i] = cast(str, "" if lines[i] is None else lines[i] ) + control # FIXME - why this cast too for mypy?

    if hasControl and lines[i] == "":
      lines[i] = None

  return [ x for x in lines if x is not None ]
# }}} preprocess

# {{{
@typechecked
def all_keys_to_string(obj:Any) -> Any:
  if isinstance(obj, dict):
    return {str(k): all_keys_to_string(v) for k,v in obj.items()}
  if isinstance(obj, list):
    return [all_keys_to_string(item) for item in obj]
  return obj
# }}} all_keys_to_string

# {{{
@typechecked
def convert(api:JSONDict, path:Path) -> None:

  path = Path(os.path.normpath(path))

  key = f"file:///{api_key}/" + '/'.join(path.parts[prefix_end:])

  if key in api:
    return

  filestr = []
  try:
    if path.parts[-1].endswith(".json"):
      filestr = preprocess(path)
      api[key] = json.loads("\n".join(filestr))

    elif path.parts[-1].endswith(".yaml"):
      filestr = preprocess(path)
      yaml = YAML(typ='rt')
      tmp = yaml.load("\n".join(filestr))
      api[key] = all_keys_to_string(tmp)

    elif path.parts[-1].endswith(".xml"):
      filestr = preprocess(path)
      api[key] = "\n".join(filestr)

    else:
      print(f"{path} does not end in .yaml, .json or .xml. Cannot continue")
      sys.exit(1)

    # {{{
    # recurse the entire schema returning any objects who have the keys in keys
    @typechecked
    def recurse(data:"JSONType") -> Generator[JSONDict, None, None]:
      if isinstance(data, dict):
        for key in ("$ref", "externalValue"):
          if key in data:
            yield data
            break
        for value in data.values():
          yield from recurse(value)
      elif isinstance(data, list):
        for value in data:
          yield from recurse(value)
    # }}} recurse

    for ry in recurse(api[key]):
      if "externalValue" in ry:
        convert(api, path.parent / ry["externalValue"])
        p = f"file:///{api_key}/" + "/".join(Path(os.path.normpath(path.parent / ry["externalValue"])).parts[prefix_end:])
        ry["value"] = api[p]
        del ry["externalValue"]
      else:
        if ry["$ref"].startswith("#/"):
          ry["$ref"] = key + ry["$ref"]
          continue
        convert(api, path.parent / ry["$ref"].split('#',1)[0])
        p = f"file:///{api_key}/" + "/".join(Path(os.path.normpath(path.parent / ry["$ref"].split('#',1)[0])).parts[prefix_end:])
        s = "#" + ry["$ref"].split('#',1)[1] if '#' in ry["$ref"] else ""
        ry["$ref"] = p+s

  except:
    for i,line in enumerate(filestr):
      print(f"{i+1} {line}")
    print(f"Failed parsing {path}")
    raise

# vim: set sw=2 sts=2 ts=2 expandtab:
