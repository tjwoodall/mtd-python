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

from typing import cast, Any

JSONPrimitive = None | bool | int | float | str
# Annoying but typeguard seems to need Any rather than JSONType here
JSONDict = dict[str, Any]
JSONList = list[Any]
JSONType = JSONPrimitive | JSONDict | JSONList

def Jbool(obj:JSONType, key:int|str) -> bool:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], bool):
      return cast(bool, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need bool")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], bool):
      return cast(bool, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need bool")
  raise RuntimeError("Need list or dict")

def Jint(obj:JSONType, key:int|str) -> int:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], int):
      return cast(int, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need int")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], int):
      return cast(int, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need int")
  raise RuntimeError("Need list or dict")

def Jfloat(obj:JSONType, key:int|str) -> float:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], (float, int)):
      return cast(float, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need float")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], (float, int)):
      return cast(float, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need float")
  raise RuntimeError("Need list or dict")

def Jstr(obj:JSONType, key:int|str) -> str:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], str):
      return cast(str, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need str")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], str):
      return cast(str, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need str")
  raise RuntimeError("Need list or dict")

def JDict(obj:JSONType, key:int|str) -> JSONDict:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], dict):
      return cast(JSONDict, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need dict")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], dict):
      return cast(JSONDict, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need dict")
  raise RuntimeError("Need list or dict")

def JList(obj:JSONType, key:int|str) -> JSONList:
  if isinstance(obj, dict) and isinstance(key, str):
    if isinstance(obj[key], list):
      return cast(JSONList, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need list")
  if isinstance(obj, list) and isinstance(key, int):
    if isinstance(obj[key], list):
      return cast(JSONList, obj[key])
    raise RuntimeError(f"Got {type(obj[key])} need list")
  raise RuntimeError("Need list or dict")

def castJbool(obj:JSONType) -> bool:
  return Jbool([obj],0)

def castJint(obj:JSONType) -> int:
  return Jint([obj],0)

def castJfloat(obj:JSONType) -> float:
  return Jfloat([obj],0)

def castJstr(obj:JSONType) -> str:
  return Jstr([obj],0)

def castJDict(obj:JSONType) -> JSONDict:
  return JDict([obj],0)

def castJList(obj:JSONType) -> JSONList:
  return JList([obj],0)

def toJbool(obj:JSONType) -> bool|None:
  try:
    return Jbool([obj],0)
  except RuntimeError:
    return None

def toJint(obj:JSONType) -> int|None:
  try:
    return Jint([obj],0)
  except RuntimeError:
    return None

def toJfloat(obj:JSONType) -> float|None:
  try:
    return Jfloat([obj],0)
  except RuntimeError:
    return None

def toJstr(obj:JSONType) -> str|None:
  try:
    return Jstr([obj],0)
  except RuntimeError:
    return None

def toJDict(obj:JSONType) -> JSONDict|None:
  try:
    return JDict([obj],0)
  except RuntimeError:
    return None

def toJList(obj:JSONType) -> JSONList|None:
  try:
    return JList([obj],0)
  except RuntimeError:
    return None

# vim: set sw=2 sts=2 ts=2 expandtab:
