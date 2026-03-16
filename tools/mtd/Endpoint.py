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
import datetime
import urllib
import platform
import os
import hashlib
import time
import sys
from typing import Any, cast

import netifaces
import requests
import xmltodict

from typeguard import typechecked

from .JSONTypes import JSONDict, JSONList, JSONType, Jstr, castJList, castJstr

from .Config import Config
from .AccessHelper import AccessHelper
from .OAuth import OAuth
from .LOG import logger
from .PrintBuffer import _PrintBuffer
from .Validate import Validator

# {{{
class Endpoint:
  BASE_URI = 'https://test-api.service.hmrc.gov.uk'

  # {{{
  @typechecked
  def __init__(self, config: Config):
    self._config = config
  # }}} __init__

  # {{{
  @typechecked
  def make_get_request(self, API: JSONDict, endpoint: AccessHelper, application_id: str|None, extra_scopes: list[str]) -> JSONDict:
    token:str|None = None
    assert isinstance(endpoint, AccessHelper), "endpoint is not an AccessHelper"

    if application_id is None:
      application_id = self._config.get_default("application")

    control = endpoint.get("_control")

    if "_api" not in control.keys():
      raise RuntimeError(f"_api missing from {control} {endpoint}")
    api = control.get("_api").as_str()
    if api not in API:
      raise RuntimeError(f"{api} is not recognised. Valid values are {API.keys()}")
    ep = cast(JSONDict, API[api])

    if "_major" not in control.keys():
      major = str(max(int(k) for k in ep.keys()))
    else:
      major = control.get("_major").as_str()
    if major not in ep:
      raise RuntimeError(f"{major} is not a valid major version for {api}. Valid values are {ep.keys()}")
    ep = cast(JSONDict, ep[major])

    if "_minor" not in control.keys():
      minor = str(max(int(k) for k in ep.keys()))
    else:
      minor = control.get("_minor").as_str()
    if minor not in ep:
      raise RuntimeError(f"{minor} is not a valid minor version for {api}-{major}.{minor}. Valid values are {ep.keys()}")
    ep = cast(JSONDict, ep[minor])

    if "_path" not in control.keys():
      raise RuntimeError(f"_path missing from {control}")
    path = control.get("_path").as_str()

    if path not in cast(JSONDict, ep["paths"]):
      raise RuntimeError(f"{path} is not a valid path for {api}-{major}.{minor}. Valid values are {ep.keys()}")

    server = ""
    for s in cast(JSONDict, ep["servers"]):
      d = Jstr(s, 'description') if 'description' in s else 'Sandbox' if "test-api" in Jstr(s, 'url') else "Production"
      if d == control.get("_server").as_str():
        server = Jstr(s, 'url')

    if server == "":
      raise RuntimeError(f"{control.get('_server').as_str()} is not a valid server for {api}-{major}.{minor}")


    # might need some other data from this EP
    ep = cast(JSONDict, cast(JSONDict, ep["paths"])[path])

    if "_action" not in control.keys():
      raise RuntimeError(f"action missing from {control}")
    action = control.get("_action").as_str()
    if action not in ep:
      raise RuntimeError(f"{action} is not a valid action for {api}-{major}.{minor}. Valid values are {ep.keys()}")

    common_parameters = cast(JSONList, ep['parameters'] if 'parameters' in ep else [])
    ep = cast(JSONDict, ep[action])

    reply:JSONDict = {
      "_control": {
        "_api": api,
        "_major": major,
        "_minor": minor,
        "_path": path,
        "_action": action,
        "_server": server,
      },
      "_parameters": {}
    }

    logger.debug("requested endpoint:\n", endpoint)
    logger.debug("resolved endpoint:\n", json.dumps(ep, indent=2))

    headers = {}

    # TODO - we should alert if the parameters doesn't include the Authorization header when we build application.json
    security = cast(JSONList, ep["security"])
    if len(security) != 1:
      raise RuntimeError("Don't know how to handle multiple security types")
    secinfo = cast(JSONDict, security[0])
    if "Application-Restricted" in secinfo:
      logger.info(f"Getting Application-Restricted token for {cast(list[str], secinfo['Application-Restricted']) + extra_scopes}")
      token = OAuth(self._config).request_application_token(application_id, cast(list[str], secinfo["Application-Restricted"])+extra_scopes, endpoint.get("_control"))
      # FIXME - this shouldn't be required if it was correctly included in the API
      headers['Authorization'] = "Bearer " + token
    elif "User-Restricted" in secinfo:
      logger.info(f"Getting User-Restricted token for {cast(list[str], secinfo['User-Restricted']) + extra_scopes}")
      token = OAuth(self._config).request_user_token(application_id, cast(list[str], secinfo["User-Restricted"]) + extra_scopes, endpoint)
      # FIXME - this shouldn't be required if it was correctly included in the API
      headers['Authorization'] = "Bearer " + token
    elif secinfo == {}:
      token = None
    else:
      raise RuntimeError(f"Unhandled security {secinfo}")

# Populate the Gov-* headers
# get ip addresses from interfaces.
    ips = set()
    macs = set()
    iptime = datetime.datetime.now(datetime.timezone.utc)

    @typechecked
    def percent_encode(instr: str) -> str:
      return urllib.parse.quote(instr, '')

    for iface in netifaces.interfaces():
      if iface == "lo":
        continue

      addrs = netifaces.ifaddresses(iface)
      link = addrs.get(netifaces.AF_LINK)
      if link:
        m = link[0].get('addr')
        if m:
          macs.add(percent_encode(m))

      # IPv4
      ipv4_addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
      for addr in ipv4_addrs:
        ips.add(str(addr['addr']))

      # IPv6
      ipv6_addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET6, [])
      for addr in ipv6_addrs:
        ips.add(percent_encode(str(addr['addr'])))
# end get addresses from interfaces.

    # This is the best I can do. /sys/class/dmi doesn't exist on VMs for example, it's not typically possible to identify manufacturer and model in the VM.
    @typechecked
    def read_sys(item: str) -> str:
      if item == "manufacturer":
        file = '/sys/class/dmi/id/sys_vendor'
      elif item == "model":
        file = '/sys/class/dmi/id/product_name'
      else:
        raise RuntimeError("What's going on?")

      try:
        with open(file, 'r', encoding="utf-8") as f:
          return f.read().strip()
      except FileNotFoundError:
        return self._config.get(item).as_str()

    # Something like this for windows - completely untested!
    # import wmi
    # def read_sys_windows(item: str):
    #   c = wmi.WMI()
    #   for system in c.Win32_ComputerSystem():
    #     if item == 'manufacturer':
    #       return system.Manufacturer
    #     elif item == 'model':
    #       return system.Model
    #     else:
    #       raise RuntimeError("What's going on?")

    headers["Gov-Client-Connection-Method"] = "OTHER_DIRECT"
    headers["Gov-Client-Device-ID"] = self._config.get("guid").as_str()
    headers["Gov-Client-Local-IPs"] = ','.join(ips)
    headers["Gov-Client-Local-IPs-Timestamp"] = iptime.strftime('%Y-%m-%dT%H:%M:%S.') + f'{iptime.microsecond // 1000:03d}Z'
    headers["Gov-Client-MAC-Addresses"] = ','.join(macs)
    headers["Gov-Client-Multi-Factor"] = "" # Not applicable
    headers["Gov-Client-Timezone"] = "UTC+00:00"
    headers["Gov-Client-User-Agent"] = f"os-family={percent_encode(platform.system())}&os-version={percent_encode(platform.version())}%20{percent_encode(platform.release())}&device-manufacturer={percent_encode(read_sys('manufacturer'))}&device-model={percent_encode(read_sys('model'))}"
    headers["Gov-Client-User-IDs"] = f"os={percent_encode(str(os.getuid()))}"
    hashval = hashlib.sha256()
    hashval.update("GPL3".encode('utf-8'))  # TODO GPL3 or BSD2?
    appname = self._config.get('appname').as_str()
    assert isinstance(appname, str), "appname is not str"
    appversion = self._config.get('appversion').as_str()
    assert isinstance(appname, str), "appversion is not str"
    headers["Gov-Vendor-License-IDs"] = f"{percent_encode(appname)}={percent_encode(hashval.hexdigest())}"
    headers["Gov-Vendor-Product-Name"] = f"{percent_encode(appname)}"
    headers["Gov-Vendor-Version"] = f"{percent_encode(appname)}={percent_encode(appversion)}"
# END populating Gov- headers

    qparams:dict[str,Any] = {}

    # TODO - missing required check for headers too
    _headers = endpoint.get('_parameters')
    aparams = cast(list[JSONDict], ep['parameters'] if 'parameters' in ep else [])
    for v in aparams + common_parameters:
      if v["in"] == "header":
        # TODO - these have the value in the schema, why not get it from there instead of hard coding it?
        # Or even supply them so they can be overridden if necessary?
#        if v["name"] == "Accept":
#          headers['Accept'] = f"application/vnd.hmrc.{major}.{minor}+json"
#        elif v["name"] == "Content-Type":
#          headers['Content-Type'] = "application/json"
        if v["name"] == 'Authorization':
          if token is None:   #This indicates a documentation error or an error parsing it as we need an authorization header without it being user or application restricted.
            raise RuntimeError(f"Incorrect access state or bad token for Authorization header in endpoint '{endpoint}'")
          headers['Authorization'] = "Bearer " + token
        elif v["name"] in _headers.keys():
          # FIXME - don't overwrite the Gov- special headers (Don't think they're listed in the API anyway so we're ok)
          if v["schema"]["type"] == "boolean":
            headers[cast(str, v["name"])] = str(_headers.get(cast(str, v["name"])).as_bool())
          else:
            headers[cast(str, v["name"])] = _headers.get(cast(str, v["name"])).as_str()
        elif "required" in v and v["required"] and v["name"] != "Gov-*" and v["name"] != "Content-Length":
          # "Gov-*" header is required in the txm-fph-validator-api /test/fraud-prevention-headers/validate endpoint
          raise RuntimeError(f"Missing required header {v['name']}")
      elif v["in"] == "path":
        if f'{{{v["name"]}}}' in path and v["name"] in _headers.keys():
          path = path.replace(f'{{{v["name"]}}}', _headers.get(cast(str, v["name"])).as_str())
      elif v["in"] == "query":
        if v["name"] in _headers.keys():
          qparams[cast(str, v["name"])] = _headers.get(cast(str, v["name"])).value()
        elif "required" in v and v["required"]:
          raise RuntimeError(f"Missing required parameter {v['name']}")
      else:
        raise RuntimeError(f"Can't handle {v['in']} as a parameter yet")

    if '{' in path:
      raise RuntimeError(f"Mismatched '{{' or missing key in path '{path}'")

    time.sleep(0.5) #Avoid throttle
    logger.info("headers=\n", json.dumps(headers, indent=2))
    logger.info("params=\n", json.dumps(qparams, indent=2))
    if control.get("_action").as_str() in {"put", "post", "patch"}:
      if "_data" not in endpoint.keys():
        raise RuntimeError(f"Missing required post/put data")
      logger.info(f"data=\n{json.dumps(endpoint.get('_data').getraw(), indent=2)}")
      if "_disableValidation" not in control.keys() or control.get("_disableValidation").as_bool() is False:
        if "requestBody" in ep:
          x = cast(JSONDict, ep["requestBody"])
          x = cast(JSONDict, x["content"])
          if 'application/json' in x:
            x = cast(JSONDict, x["application/json"])
            x = cast(JSONDict, x["schema"])
            Validator.validate(endpoint.get('_data').get('json').getraw(), x)
        elif endpoint.get("_data").getraw() is not None:
          raise RuntimeError(f"Unexpected post/put data")
    else:
      if "_data" in endpoint.keys() and endpoint.get("_data").getraw() is not None:
        raise RuntimeError(f"Unexpected post/put data")

    sys.stdout = _PrintBuffer()
    output = control.get("_output").as_str()

    def getData() -> JSONType:
      if endpoint.get("_data").getraw() is None:
        return None
      if output == "ndjson":
        return "\n".join(json.dumps(item) for item in castJList(endpoint.get("_data").get(output).getraw())) + '\n'
      return endpoint.get("_data").get(output).getraw()

    if control.get("_action").as_str() == "get":
      result = requests.get(server + path, headers=headers, params=qparams, timeout=60)
    elif control.get("_action").as_str() == "post":
      if isinstance(getData(), str):
        result = requests.post(server + path, headers=headers, params=qparams, data=castJstr(getData()), timeout=60)
      else:
        result = requests.post(server + path, headers=headers, params=qparams, json=getData(), timeout=60)
    elif control.get("_action").as_str() == "patch":
      result = requests.patch(server + path, headers=headers, params=qparams, json=getData(), timeout=60)
    elif control.get("_action").as_str() == "delete":
      result = requests.delete(server + path, headers=headers, params=qparams, timeout=60)
    elif control.get("_action").as_str() == "put":
      result = requests.put(server + path, headers=headers, params=qparams, json=getData(), timeout=60)
    else:
      _PrintBuffer.reset()
      raise RuntimeError(f"Unhandled action {control.get('_action')}")
    logger.debug(_PrintBuffer.getText())
    _PrintBuffer.reset()

    logger.debug("=== REQUEST ===")
    logger.debug("URL:", result.request.url)
    logger.debug("Method:", result.request.method)
    logger.debug("Headers:", result.request.headers)
    logger.debug("Body:", result.request.body)

    logger.debug("=== RESPONSE ===")
    logger.debug("Status code:", result.status_code)
    logger.debug("Headers:", result.headers)
    logger.debug("Body:", result.text)

    reply['_control']['_response'] = str(result.status_code)
    reply['_parameters'].update(dict(result.headers))
    try:
      reply['_data']  = json.loads(result.text)
      reply['_control']['_output'] = "json"
    except: # pylint: disable=bare-except
      try:
        reply['_data'] = xmltodict.parse(result.text)
        reply['_control']['_output'] = "xml"
      except:
        reply['_data'] = None
        reply['_control']['_output'] = "None"
    reply['_text']  = result.text

    class Done(Exception):
      pass

    # Validate the response
    reply['_validation'] = "OK"
    try:
      if "responses" not in ep:
        raise Done("Missing responses in endpoint")
      responses = cast(JSONDict, ep["responses"])
      if reply['_control']['_response'] not in responses:
        raise Done(f"Missing {reply['_control']['_response']} in responses")
      responses = cast(JSONDict, responses[reply['_control']['_response']])
      if "content" not in responses:
        if reply['_data'] is not None:
          raise Done(f"Missing content in schema - this should not happen")
        return reply
      responses = cast(JSONDict, responses["content"])
      if "application/json" not in responses:
        if responses == {} and reply['_data'] is None:
          raise Done("OK")
        raise Done(f"Missing application/json in schema - this should not happen")
      responses = cast(JSONDict, responses["application/json"])
      if "schema" not in responses:
        raise Done(f"Missing 'schema' in schema - this should not happen")
      responses = cast(JSONDict, responses["schema"])
#      Validator.validate(reply['_data'], responses)
    except Validator.BadInstance as e:
      for eidx,error in enumerate(e.errors):
        path = ".".join([str(p) for p in error.absolute_path])
        logger.info(f"Validation Error {eidx})")
        logger.info(f"  • Path: {path or '[root]'}")
        logger.info(f"    Message: {error.message}")
        logger.info()

        if error.context:
          logger.info(f"Sub-errors ({len(error.context)}):")
          for sidx, sub in enumerate(error.context):
            logger.info(f'eidx={eidx} sidx={sidx} error:{sub}')
      reply['_validation'] = "validation failed"
    except Done as e:
      reply['_validation'] = str(e)

    logger.info("response=\n", json.dumps(reply, indent=2))

    return reply
  # }}} make_get_request

# }}} class Endpoint

# vim: set sw=2 sts=2 ts=2 expandtab:
