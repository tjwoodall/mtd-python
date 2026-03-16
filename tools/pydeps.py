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

import ast
import importlib.util
import os
import sys

def local_imports(path:str, imports:set[str]) -> list[str]:
  imports.add(os.path.abspath(path))

  with open(path, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read(), path)

  newimports:set[str] = set()
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for n in node.names:
        if n.name not in imports:
          newimports.add(n.name)
    elif isinstance(node, ast.ImportFrom):
      if node.module:
        if node.module not in imports:
          newimports.add(node.module)

  local:set[str] = set()
  for mod in newimports:
    # Skip UNO imports — they are not real Python modules
    if mod.startswith("com.sun.star"):
      continue
    spec = importlib.util.find_spec(mod)
    if spec and spec.origin and spec.origin.endswith(".py") and spec.origin not in imports:
      if os.path.abspath(spec.origin).startswith(os.getcwd()):
        local.add(spec.origin)

  imports.update(local)
  for mod in local:
    imports.update(local_imports(mod, imports))

  return sorted(imports)

print("\n".join(local_imports(sys.argv[1], set())))

# vim: set sw=2 sts=2 ts=2 expandtab:
