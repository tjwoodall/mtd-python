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
from copy import deepcopy
from pathlib import Path

from typeguard import typechecked

from mtd.JSONTypes import JSONType, JSONDict, JDict, Jstr
from mtd import ApiReader

# {{{
@typechecked
def fatal(err:str, obj:JSONType) -> None:
  sys.stdout.flush()
  print("-------- FATAL --------", file=sys.stderr)
  print("-----------------------", file=sys.stderr)
  print(json.dumps(obj, indent=2), file=sys.stderr)
  print("-----------------------", file=sys.stderr)
  raise RuntimeError(err)
# }}} fatal

ref_stack:list[str] = []
# {{{
class RefResolver:
  major_key:str
  minor_key:str
# }}} class RefResolver
# {{{
@typechecked
def check_formats(obj:JSONDict, path:list[str]) -> bool:
#    print(f"check_formats on {obj}")
  if not isinstance(obj, dict):
    print("Not a dict while checking formats")
    return False

  fixed = deepcopy(obj)

  # Fix dodgy formats with standard values
  if 'format' in fixed:
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
    if fixed["format"] in replace_me:
      fmt = Jstr(fixed, "format")
      del fixed["format"]
      if "pattern" in fixed:
        del fixed["pattern"]
      if replace_me[fmt][0] is not None:
        fixed["format"] = replace_me[fmt][0]
      if replace_me[fmt][1] is not None:
        fixed["pattern"] = replace_me[fmt][1]

  # Convert patterns to standard formats
  if 'pattern' in fixed:
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
    if fixed["pattern"] in replace_me:
      pattern = Jstr(fixed, "pattern")
      if "format" in fixed:
        del fixed["format"]
      del fixed["pattern"]
      if replace_me[pattern][0] is not None:
        fixed['format'] = replace_me[pattern][0]
      if replace_me[pattern][1] is not None:
        fixed['pattern'] = replace_me[pattern][1]

  # Replace dodgy id with format
  if 'id' in fixed and isinstance(fixed['id'], str):
    replace_me = {
        "tax-year": ("tax-year",None),
        "full-date": ("date", "^\\d{4}-\\d{2}-\\d{2}$"),
    }
    if fixed["id"] in replace_me:
      fmt = Jstr(fixed, "id")
      del fixed['id']
      fixed['format'] = replace_me[fmt][0]

  if 'type' in fixed and fixed['type'] != "string" and 'example' in fixed and isinstance(fixed['example'], str):
    fixed['example'] = "NOT A STRING"
  elif 'type' in fixed and fixed['type'] == "string" or 'example' in fixed and isinstance(fixed['example'], str):
    if 'minimum' in fixed:
      fixed['minLength'] = fixed['minimum']
      del fixed['minimum']
    if 'maximum' in fixed:
      fixed['maxLength'] = fixed['maximum']
      del fixed['maximum']

  if fixed != obj:
    print(f"{path}: replace {json.dumps(obj, indent=2)} with {json.dumps(fixed, indent=2)}")
    return False

  return True

# }}} check_formats


#####################################

# tools/find-bad-formats.py $(1) artifacts/$(1).config.json artifacts/$(1).$(2).extraconfig.json $(1)/resources/public/api/conf/$2/application.yaml

# 1   2    3         4
# API CONF EXTRACONF YAML
if len(sys.argv) != 5:
  sys.exit(0)

with open(sys.argv[2], "r", encoding="utf-8") as f:
  config = json.load(f)

if Path(sys.argv[3]).exists():
  with open(sys.argv[3], "r", encoding="utf-8") as f:
    extraconfig = json.load(f)
else:
  extraconfig = {}

application:JSONDict = {}

ApiReader.api_key = sys.argv[1]

root = Path(sys.argv[4])

if not root.exists():
  print(f"{root} does not exist")
  sys.exit(0)

# national-insurance/resources/public/api/conf/1.1/application.yaml
RefResolver.major_key,RefResolver.minor_key = root.parts[-2].split(".")
ApiReader.prefix_end = len(root.parts)-1

confkey = ApiReader.api_key+"/conf/application.conf"
if confkey not in extraconfig:
  extraconfig[confkey] = {}

ApiReader.config = config[confkey]
ApiReader.extraconfig = extraconfig[confkey]

if "api" not in ApiReader.config or \
    RefResolver.major_key not in JDict(ApiReader.config, "api") or \
    RefResolver.minor_key not in JDict(JDict(ApiReader.config, "api"), RefResolver.major_key):
  print(f"Skipping NO CONFIG {root}")
  sys.exit(0)

if ApiReader.api_key not in application:
  application[ApiReader.api_key] = {}
if RefResolver.major_key not in application[ApiReader.api_key]:
  application[ApiReader.api_key][RefResolver.major_key] = {}
if RefResolver.minor_key not in application[ApiReader.api_key][RefResolver.major_key]:
  application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key] = {}

application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key] = {}
api = application[ApiReader.api_key][RefResolver.major_key][RefResolver.minor_key]

# Note that this updates extraconfig (where appropriate)
ApiReader.convert(api, root)

# {{{
@typechecked
def format_checker(obj:JSONType, path:list[str]) -> bool:

#  print(f"format_checker at {path}")
  rv = True
  if isinstance(obj, dict):
    if not check_formats(obj, path):
      rv = False

    for k,v in obj.items():
      if not format_checker(v, path + [k]):
        rv = False
  elif isinstance(obj, list):
    for v in obj:
      if not format_checker(v, path + ["index into array"]):
        rv = False

  return rv
# }}} format_checker

rv = 0
for k,v in api.items():
  # file:///business-details-api/schemas/retrieveBusinessDetails/response.json
  # file:///business-details-api/resources/public/api/conf/major.minor/schemas/retrieveBusinessDetails/response.json
  p = k.split("/")
  p = p[3:4] + [ "resources", "public", "api", "conf", f"{RefResolver.major_key}.{RefResolver.minor_key}" ] + p[4:]
  if not format_checker(v, ["/".join(p)]):
    rv = 1

sys.exit(rv)

# vim: set sw=2 sts=2 ts=2 expandtab:
