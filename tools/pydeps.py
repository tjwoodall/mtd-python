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

def local_imports(path: str, imports: set[str]) -> list[str]:
  path = os.path.abspath(path)

  if path in imports:
    return []

  imports.add(path)

  with open(path, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read(), path)

  # Work out the Python package containing this file.
  directory = os.path.dirname(path)
  package_parts = []

  while os.path.isfile(os.path.join(directory, "__init__.py")):
    package_parts.insert(0, os.path.basename(directory))
    directory = os.path.dirname(directory)

  package = ".".join(package_parts)

  modules: set[str] = set()

  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for n in node.names:
        modules.add(n.name)

    elif isinstance(node, ast.ImportFrom):
      if node.module:
        module = node.module
        if node.level:
          module = importlib.util.resolve_name(
            "." * node.level + module,
            package,
          )
        modules.add(module)

      elif node.level:
        # `from . import Foo` / `from .. import Foo`
        base = importlib.util.resolve_name(
          "." * node.level,
          package,
        )
        for n in node.names:
          modules.add(f"{base}.{n.name}")

  local: set[str] = set()

  for mod in modules:
    # Skip UNO imports — they are not real Python modules
    if mod.startswith("com.sun.star"):
      continue

    try:
      spec = importlib.util.find_spec(mod)
    except (ImportError, ModuleNotFoundError, AttributeError):
      continue

    if (
      spec
      and spec.origin
      and spec.origin.endswith(".py")
    ):
      origin = os.path.abspath(spec.origin)

      if origin.startswith(os.getcwd() + os.sep) and origin not in imports:
        local.add(origin)

  for mod in sorted(local):
    local_imports(mod, imports)

  return sorted(imports)

print("\n".join(local_imports(sys.argv[1], set())))

# vim: set sw=2 sts=2 ts=2 expandtab:
