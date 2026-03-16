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

import os
import sys
import importlib
from typing import Any

import uno

# apt-get install python3-uno libreoffice-script-provider-python

# Get the user path via UNO
ctx = uno.getComponentContext()
ps = ctx.getByName("/singletons/com.sun.star.util.thePathSettings")
user_config_url = ps.getPropertyValue("UserConfig")  # returns a file:// URL
user_config_dir = uno.fileUrlToSystemPath(user_config_url)

# Construct the Python scripts path
libreoffice_dir = os.path.join(os.path.dirname(user_config_dir), "Scripts", "python", "libreoffice")

if libreoffice_dir not in sys.path:
  sys.path.append(libreoffice_dir)

import libreoffice # pylint: disable=wrong-import-position

XSCRIPTCONTEXT: Any

def reload_package(pkg:str) -> None:
  names = sorted(
    (
      n for n in sys.modules
      if n == pkg or n.startswith(pkg + ".")
    ),
    key=lambda n: n.count("."),
    reverse=True,
  )

  for n in names:
    importlib.reload(sys.modules[n])

def reload() -> Any:
  global libreoffice  # pylint: disable=global-statement

  reload_package("mtd")
  libreoffice = importlib.reload(libreoffice)
  libreoffice.XSCRIPTCONTEXT = XSCRIPTCONTEXT  # pylint: disable=undefined-variable

  return libreoffice

# This is the outbound sheet callback.
# {{{ sheet_changed_callback
def sheet_changed_callback(event:Any) -> None:
  reload().sheet_changed_callback(event)
# }}} sheet_changed_callback

# {{{ cmd_test_click
def cmd_test_click(event:Any) -> None:
  reload().cmd_test_click_impl(event, None)
# }}} cmd_test_click

# This is the MAINSheet changed callback.
# {{{ on_sheet_change
def on_sheet_change(event:Any) -> None:
  reload().on_sheet_change(event)
# }}} on_sheet_change

g_exportedScripts = (on_sheet_change,cmd_test_click,sheet_changed_callback,)

# vim: set sw=2 sts=2 ts=2 expandtab:
