#!/usr/bin/env -S python3

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

import sys
import re
import json
import shutil
from pathlib import Path
from typing import Tuple, Any

from typeguard import typechecked

from lxml import html

# {{{
@typechecked
def find_node(root:html.HtmlComment|html.HtmlElement, tag:str, attrib:str|None=None, value:str|None=None) -> list[html.HtmlElement]:
  rval = []
  if root.tag == tag:
    if attrib is None:
      rval.append(root)
    elif attrib in root.attrib:
      if value is None or root.attrib[attrib] == value:
        rval.append(root)

  for child in root:
    rval += find_node(child, tag, attrib, value)

  return rval
# }}}

# {{{
@typechecked
def get_version(s:str) -> Tuple[str|Any, ...]:
  match = re.search(rf'^version-(\d+)\.(\d+)$', s)

  if match:
    return match.groups()
  raise RuntimeError(rf"{s} does not match pattern ^version-\d+\.\d+$")
# }}}

# {{{
@typechecked
def get_released_in_production(s:str) -> bool:
  if s == "Sandbox and Production":
    return True
  if s == "Sandbox":
    return False
  if s == "Not applicable":
    return False
  raise RuntimeError(f"{s} was unexpected for checking if it's released in production")
# }}}

# {{{
@typechecked
def get_status(s:str) -> str:
  s = s.strip()
  if s == "alpha":
    return "ALPHA"
  if s == "private alpha":
    return "PRIVATE_ALPHA"
  if s == "private beta":
    return "PRIVATE_BETA"
  if s == "beta":
    return "BETA"
  if s == "deprecated":
    return "DEPRECATED"
  if s == "stable":
    return "STABLE"
  raise RuntimeError(f"{s} was unhandled for get_status")
# }}}

if len(sys.argv) < 3:
  sys.exit(1)

with open(sys.argv[1], "r", encoding="utf-8") as fin:
  config = json.load(fin)

for f in sys.argv[2:]:
  tree = html.parse(f)

  root = tree.getroot()

  #Step 1. find the api information
  apis = find_node(root, "section", "id", "endpoints")

  for api in apis:

    #dump(api)
    trs = find_node(api, "tr", "class", "govuk-table__row")

    for tr in trs:
      #dump(tr)
      vers = find_node(tr, "th", "scope", "row")
      envs = find_node(tr, "td", "id", "environments")
      eps = find_node(tr, "td", "id", "endpoints")

      if len(vers) == 1 and len(envs) == 1 and len(eps) == 1:

        if eps[0].text.strip() == "Sign in to request access":
          continue

        major, minor = get_version(vers[0].attrib["id"])
        released_in_production = get_released_in_production(envs[0].text)

        links = find_node(vers[0], "a", "href")
        if len(links) == 1:
          status = get_status(links[0].text)
        else:
          raise RuntimeError(f"Missing link while getting status")

        if status in {"PRIVATE_ALPHA", "PRIVATE_BETA"}:
          continue

        links = find_node(eps[0], "a", "href")
        if len(links) == 1:
          path = Path(links[0].attrib["href"])
          apiname=f"{path.parts[5]}/conf/application.conf"
          #print(f"processing major={major} minor={minor} released-in-production={released_in_production} status={status} api={apiname}")

          # txm-fph-validator-api/conf/application.conf needs this
          if apiname not in config:
            config[apiname] = {}

          if "api" not in config[apiname]:
            config[apiname]["api"] = {}
            #print(f"Added 'api' to {apiname} config")
          conf = config[apiname]["api"]

          if major not in conf:
            conf[major] = {}
            #print(f"Added '{major}' to {apiname} config")
          conf = conf[major]

          if minor not in conf:
            conf[minor] = {}
            #print(f"Added '{minor}' to {apiname} config")
          conf = conf[minor]

          if "status" not in conf or conf["status"] != status:
            conf["status"] = status
            print(f"Changed 'status' to '{status}' for {apiname} {major}.{minor}")

          if "endpoints" not in conf:
            conf["endpoints"] = {}
            #print(f"Added 'endpoints' to {apiname} config")
          conf = conf["endpoints"]

          if "api-released-in-production" not in conf or conf["api-released-in-production"] != released_in_production:
            conf["api-released-in-production"] = released_in_production
            print(f"Changed 'api-released-in-production' to {released_in_production} for {apiname} {major}.{minor}")

        else:
          raise RuntimeError(f"Missing link")

with open(sys.argv[1] + ".tmp", 'w', encoding="utf-8") as json_file:
  json_file.write(json.dumps(config, indent=2, sort_keys=True) + "\n")
shutil.move(sys.argv[1] + ".tmp", sys.argv[1])

# vim: set sw=2 sts=2 ts=2 expandtab:
