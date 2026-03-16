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
import json
import uuid
import tempfile
import shutil
from typing import cast

from typeguard import typechecked

from .JSONTypes import JSONType
from .AccessHelper import AccessHelper
from .LOG import logger

# {{{
class Config:
  PYTHON_MTD_CLIENT_ID = "GZ6gW5VT3fC6Se5k2TxvREzLMkl4"

  # {{{
  @typechecked
  def __init__(self, name: str):
    self.file_ = os.path.realpath(os.path.expanduser(name))
    path = os.path.dirname(self.file_)
    print(f"name={name} file={self.file_} path={path}")
    if not os.path.exists(path):
      os.makedirs(path)
    try:
      with open(self.file_, "r", encoding="utf-8") as f:
        self._data = AccessHelper(json.load(f))
    except FileNotFoundError:
      self._data = AccessHelper({})

    #Create some default data if it doesn't exist
    self._data.get_or_create("auth", {})
    self._data.get_or_create("default_application", Config.PYTHON_MTD_CLIENT_ID)
    self._data.get_or_create("guid", str(uuid.uuid4()))
    self._data.get_or_create("manufacturer", "Virtualization")
    self._data.get_or_create("model", "Guest")
    self._data.get_or_create("appname", "python-MTD")
    self._data.get_or_create("appversion", "0.1")

    self._flush()
  # }}} __init__

  # {{{
  @typechecked
  def _flush(self) -> None:
    final_path = os.path.expanduser(self.file_)
    dir_name = os.path.dirname(final_path)
    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tmp:
      tmp.write(json.dumps(self._data.getraw(), sort_keys=True, indent=2))
      temp_path = tmp.name  # Save path for later move

    # Atomically move to final path (overwrites if exists)
    shutil.move(temp_path, final_path)
  # }}} _flush

  # {{{
  @typechecked
  def get_default(self, conftype: str) -> str:
    conf_id = self._data.get('default_' + conftype)

    if conf_id is None:
      raise RuntimeError(f'Default {conftype} not configured')

    return conf_id.as_str()
  # }}} get_default

  # {{{
  @typechecked
  def _get_info(self, conftype: str, conf_id: str) -> AccessHelper:
    confitems = self._data.get(conftype)
    confdata = confitems.get(conf_id)
    return confdata
  # }}} _get_info

  # {{{
  @typechecked
  def get_auth(self, application_id: str, auth_id: str, scopes: list[str]) -> AccessHelper:
    logger.debug(f"get_auth application_id={application_id} auth_id={auth_id} scopes={scopes}")
    authsect = self._data.get('auth')
    if authsect is None:
      raise RuntimeError('auth section not found in persistent store')

    conf_auth = authsect.get_or_create(application_id, {})
    conf_auth = conf_auth.get_or_create(auth_id, [])  # nino for agent or taxpayer, applicationId for application

    token:AccessHelper|None = None

    request_scopes = set(scopes)
    for c in conf_auth:
      request_scopes |= set(cast(list[str], c.get("scope").getraw()))

    for c in conf_auth:
      cscopes=set(cast(list[str], c.get("scope").getraw()))
      if request_scopes <= cscopes:
        refresh_token = c.ts_get('refresh_token', 540*86400)  #Approx 18 months
        if refresh_token is not None:
          return c
        token = c
    if token is None:
      conf_auth.append({"scope": list(request_scopes)})
      token = conf_auth.get(-1)
    return token
  # }}} get auth

  # {{{
  @typechecked
  def get_or_create(self, k: str, default: JSONType) -> AccessHelper:
    return self._data.get_or_create(k, default)
  # }}} get_or_create

  # {{{
  @typechecked
  def get(self, k: str) -> AccessHelper:
    return self._data.get(k)
  # }}} get

  # {{{
  @typechecked
  def set(self, k: str, v: JSONType) -> None:
    self._data.set(k, v)
  # }}} set
# }}} class Config

# vim: set sw=2 sts=2 ts=2 expandtab:
