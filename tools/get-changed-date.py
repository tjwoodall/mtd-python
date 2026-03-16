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

from typeguard import typechecked

from lxml import html

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

tree = html.parse(sys.argv[1])

root = tree.getroot()

lastUpdated = find_node(root, "td", "id", "lastUpdated")

print(lastUpdated[0].text_content().strip())

# vim: set sw=2 sts=2 ts=2 expandtab:
