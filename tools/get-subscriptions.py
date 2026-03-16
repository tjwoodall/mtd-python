#!/usr/bin/env -S python3 -O

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

# Depends python3-pyotp

from __future__ import annotations

import sys
import json
import time
from typing import Any
import pyotp
import requests
from typeguard import typechecked
from lxml import html

from mtd.LOG import logger
from mtd.PrintBuffer import _PrintBuffer
from mtd.JSONTypes import JSONDict
from mtd import ErrorHandler

@typechecked
def request_url(url:str, session:requests.Session=requests.Session(), level:int=1) -> requests.Response:
  logger.debug(f"REQUESTING:{url}\nlevel={level}")
  time.sleep(0.5)
  sys.stdout = _PrintBuffer()
  response = session.get(url)
  logger.debug(_PrintBuffer.getText())
  _PrintBuffer.reset()
  with open(f"logs/log.{level}.html", "w", encoding="utf-8") as f:
    f.write(f"Requested get:url={url}")
    f.write(response.text)
  return response

@typechecked
def post_url(url:str, formdata:JSONDict, session:requests.Session=requests.Session(), level:int=1) -> requests.Response:
  logger.debug(f"REQUESTING:{url}\n{formdata}\nlevel={level}")
#  print(f"formdata={formdata}")
  sys.stdout = _PrintBuffer()
  response = session.post(url, data=formdata)
  logger.debug(_PrintBuffer.getText())
  _PrintBuffer.reset()
  with open(f"logs/log.{level}.html", "w", encoding="utf-8") as f:
    f.write(f"Requested post:url={url} data={formdata}")
    f.write(response.text)
  return response

# {{{ find_node
@typechecked
def find_node(root:Any, tag:str, attrib:str|None=None, value:str|None=None) -> list[Any]:
  rval = []
  if root.tag == tag:
    if attrib is None:
      rval.append(root)
    elif attrib in root.attrib:
      if value is None or root.attrib[attrib].startswith(value):
        rval.append(root)

  for child in root:
    rval += find_node(child, tag, attrib, value)

  return rval
# }}} find_node


def handle_login_form(session:requests.Session, response:requests.Response, params:JSONDict) -> requests.Response:
  print("handle login form")
  if response.status_code != 200:
    ErrorHandler.fatal("response status was not 200", {})
  tree = html.fromstring(response.text)
  form = find_node(tree, "form")
  if len(form) != 1:
    ErrorHandler.fatal(f"Form not found", {})

  # Build the payload
  payload={}
  y = find_node(form[0], "input")
  for c in y:
    if "name" not in c.attrib:
      raise RuntimeError("Missing name")
    name = c.attrib["name"]
    if name in ("emailaddress", "password"):
      payload[name] = params[name]
    elif "value" in c.attrib:
      payload[name] = c.attrib["value"]
    else:
      raise RuntimeError(f"Unhandled form element {html.tostring(c, encoding='utf8').decode('utf8')}")
    print(f"set {name} to {payload[name]}")

  url=f'https://developer.service.hmrc.gov.uk/{form[0].attrib["action"]}'
  return post_url(url, formdata=payload, session=session, level=2)

def handle_mfa_selection_form(session:requests.Session, response:requests.Response, params:JSONDict) -> requests.Response:
  print("handle mfa selection form")
  if response.status_code != 200:
    ErrorHandler.fatal("response status was not 200", {})
  tree = html.fromstring(response.text)
  form = find_node(tree, "form")
  if len(form) != 1:
    ErrorHandler.fatal(f"Form not found", {})

  # Build the payload
  payload={}
  y = find_node(form[0], "input")
  for c in y:
    if "name" not in c.attrib:
      raise RuntimeError("Missing name")
    name = c.attrib["name"]
    if name == "mfaId":
      if c.attrib["id"] == "auth-app-mfa":
        payload[name] = c.attrib["value"]
      else:
        continue
    elif "value" in c.attrib:
      payload[name] = c.attrib["value"]
    else:
      raise RuntimeError(f"Unhandled form element {html.tostring(c, encoding='utf8').decode('utf8')}")
    print(f"set {name} to {payload[name]}")

  url=f'https://developer.service.hmrc.gov.uk/{form[0].attrib["action"]}'
  return post_url(url, formdata=payload, session=session, level=3)

def handle_mfa_submission_form(session:requests.Session, response:requests.Response, params:JSONDict) -> requests.Response:
  print("handle mfa selection form")
  if response.status_code != 200:
    ErrorHandler.fatal("response status was not 200", {})
  tree = html.fromstring(response.text)
  form = find_node(tree, "form")
  if len(form) != 1:
    ErrorHandler.fatal(f"Form not found", {})

  # Build the payload
  payload={}
  y = find_node(form[0], "input")
  totp = pyotp.TOTP(params["totp_secret"])

  for c in y:
    if "name" not in c.attrib:
      raise RuntimeError("Missing name")
    name = c.attrib["name"]
    if name == "accessCode":
      payload[name] = totp.now()
    elif "value" in c.attrib:
      payload[name] = c.attrib["value"]
    else:
      raise RuntimeError(f"Unhandled form element {html.tostring(c, encoding='utf8').decode('utf8')}")
    print(f"set {name} to {payload[name]}")

  url=f'https://developer.service.hmrc.gov.uk/{form[0].attrib["action"]}'
  return post_url(url, formdata=payload, session=session, level=4)

def process_subscriptions(response:requests.Response) -> JSONDict:
#  with open("subscriptions.html", "r", encoding="utf-8") as f:
#    tree = html.fromstring(f.read())
  tree = html.fromstring(response.text)

  result:JSONDict = {}
  subs = find_node(tree, "div", "class", "govuk-accordion__section")
  for s in subs:
    subs2 = find_node(s, "div", "class", "govuk-grid-row")
    for s2 in subs2:
      print()
      print(s.attrib["id"])
      lnk = find_node(s2, "a")
      for l in lnk:
        print(l.attrib["href"])
        p =  l.attrib["href"].split("/")
        name = p[-2]
        version = p[-1]
        if name not in result:
          result[name] = { }
        result[name][version] = { "subscribed": "N/A" }
      iput = find_node(s2, "input", "name", "subscribed")
      for i in iput:
        if "checked" in i.attrib:
          print(f"Subscribed = {i.attrib['value']}")
          result[name][version]["subscribed"] = i.attrib['value']

  ErrorHandler.jd(result)

  return result


def main() -> int:
#  process_subscriptions(requests.Response())
#  sys.exit(0)

  with open(".hmrc.json", "r", encoding="utf-8") as f:
    params:JSONDict = json.load(f)
  session = requests.Session()
  response = request_url("https://developer.service.hmrc.gov.uk/developer/applications/61cf08dc-d679-4cb2-845b-97375ec6bae7/manage", session=session)
  response = handle_login_form(session, response, params)
  response = handle_mfa_selection_form(session, response, params)
  response = handle_mfa_submission_form(session, response, params)
  response = request_url("https://developer.service.hmrc.gov.uk/developer/applications/61cf08dc-d679-4cb2-845b-97375ec6bae7/subscriptions", session=session, level=5)
  process_subscriptions(response)

  return 0

if __name__ == "__main__":
  sys.exit(main())
