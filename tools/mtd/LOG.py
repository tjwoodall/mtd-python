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

import os
import logging
import datetime
import http.client
from typing import Any

from typeguard import typechecked

# {{{
class LOG:
  # {{{
  @typechecked
  def __init__(self, fname: str):
    fname = os.path.realpath(fname)
    self.logger = logging.getLogger(fname)
    self.info(fname)
  # }}} __init__

  # {{{
  @typechecked
  def error(self, *p: Any) -> None:
    self.logger.error("".join(str(x) for x in p))
  # }}} error

  # {{{
  @typechecked
  def info(self, *p: Any) -> None:
    self.logger.info("".join(str(x) for x in p))
  # }}} info

  # {{{
  @typechecked
  def debug(self, *p: Any) -> None:
    self.logger.debug("".join(str(x) for x in p))
  # }}} debug
# }}} class LOG

logging.basicConfig(filename=f'logs/mtd-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S.%f")}.log', level=logging.DEBUG)
http.client.HTTPConnection.debuglevel = 1
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("urllib3").propagate = True
logger = LOG(__file__)

# vim: set sw=2 sts=2 ts=2 expandtab:
