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
import json
import secrets
import time
import hashlib
import base64
import urllib
import socket
import select
from typing import Any,cast
import requests
from typeguard import typechecked
from lxml import html

from .JSONTypes import JSONDict, JSONList

from .Config import Config
from .LOG import logger
from .AccessHelper import AccessHelper

from .PrintBuffer import _PrintBuffer

# {{{
class OAuth:
  # {{{
  @typechecked
  def __init__(self, config: Config) -> None:
    self._config = config
  # }}} __init__

  # {{{
  @typechecked
  def __send_request(self, params: JSONDict) -> JSONDict:
    oauth_headers = {
      "Accept": "application/vnd.hmrc.1.0+json",
      "Content-Type": "application/json",
    }

    sys.stdout = _PrintBuffer()
  # TODO - we should go via the bounce server if the secret is not available, direct otherwise
    oauth = requests.post('http://test-oauth.making-tax-difficult.home.woodall.me.uk/oauth/token', headers=oauth_headers, json=params, timeout=10)
#    oauth = requests.post('https://test-api.service.hmrc.gov.uk/oauth/token', headers=oauth_headers, json=params)
    logger.debug(_PrintBuffer.getText())
    _PrintBuffer.reset()
    logger.debug("=== REQUEST ===")
    logger.debug("URL:", oauth.request.url)
    logger.debug("Method:", oauth.request.method)
    logger.debug("Headers:", oauth.request.headers)
    logger.debug("Body:", oauth.request.body)

    logger.debug("=== RESPONSE ===")
    logger.debug("Status code:", oauth.status_code)
    logger.debug("Headers:", oauth.headers)
    logger.debug("Body:", oauth.text)

    if oauth.status_code != 200:
      print('status_code = ', oauth.status_code)
      print('text        = ', oauth.text)
      raise RuntimeError('oauth request failed')
    #{"access_token":"fb5a498fa032aee2afc3f08208c60599","refresh_token":"4fa9eb212272d83d2be5b0d1e95be994","expires_in":14400,"scope":"hello","token_type":"bearer"}
    return cast(JSONDict, json.loads(oauth.text))
  # }}} __send_request

  # {{{
  @typechecked
  def __request_user_token(self, oauth_data:JSONDict, user_auth:AccessHelper) -> str:
    oauth_dict = self.__send_request(oauth_data)

    token = str(oauth_dict['access_token'])
    user_auth.ts_set('token', token)
    user_auth.ts_set('refresh_token', str(oauth_dict['refresh_token']))
    self._config._flush() # pylint: disable=protected-access

    return token
  # }}} __request_user_token

  # {{{
  @typechecked
  def request_application_token(self, application_id:str, scope:list[str], control:AccessHelper) -> str:
    logger.debug(f"request_application_token application_id={application_id} scope={scope} control={control}")

    force_auth = "force_auth" in control.keys() and control.get("force_auth").as_str() == "true"

    application_auth = self._config.get_auth(application_id, application_id, scope)

    token = application_auth.ts_get('token', 14000)      #Approx 4 hours
    if token is not None and not force_auth:
      return token

    oauth_data:JSONDict = {
      "client_id":     application_id,
      "grant_type":    "client_credentials",
    }

    oauth_dict = self.__send_request(oauth_data)

    assert isinstance(oauth_dict['access_token'], str), "access_token is not a str"
    token = oauth_dict['access_token']
    application_auth.ts_set('token', token)
    self._config._flush() # pylint: disable=protected-access

    return token
  # }}} request_application_token

  # {{{
  @typechecked
  def request_user_token(self, application_id:str, scope:list[str], endpoint:AccessHelper) -> str:
    logger.debug(f"request_user_token application_id={application_id} scope={scope} endpoint={endpoint}")

    control = endpoint.get("_control")
    parameters = endpoint.get_or_default("_parameters", {})

    force_refresh = "force_refresh" in control.keys() and control.get("force_refresh").as_str() == "true"
    force_auth = "force_auth" in control.keys() and control.get("force_auth").as_str() == "true"


    user_auth = self._config.get_auth(application_id, control.get("_username").as_str(), scope)
#    if "_userId" in control.keys():
#      user_auth = self._config.get_auth(application_id, control.get("_userId").as_str(), scope)
#    elif "arn" in control.keys():
#      user_auth = self._config.get_auth(application_id, control.get("arn").as_str(), scope)
#    elif "arn" in parameters.keys():
#      # The only api that has arn as a parameter is agent-authorisation-api
#      user_auth = self._config.get_auth(application_id, parameters.get("arn").as_str(), scope)
#    elif "vrn" in parameters.keys():
#      user_auth = self._config.get_auth(application_id, parameters.get("vrn").as_str(), scope)
#    elif "utr" in parameters.keys():
#      user_auth = self._config.get_auth(application_id, parameters.get("utr").as_str(), scope)
#    else:
#      fatal("Unsupported user auth", {})

    scope = cast(list[str], user_auth.get("scope").getraw())
    token = user_auth.ts_get('token', 14000)      #Approx 4 hours

    if token is not None and not force_refresh and not force_auth:
      logger.debug("Returned cached token")
      return token

    refresh_token = user_auth.ts_get('refresh_token', 540*86400)  #Approx 18 months
    if refresh_token is not None and not force_auth:
      logger.debug("Refreshing token")

      oauth_data:JSONDict = {
        "client_id":     application_id,
        "grant_type":    "refresh_token",
        "refresh_token":  refresh_token,
      }

      token = self.__request_user_token(oauth_data, user_auth)
      return token

    nonce=secrets.token_hex(16)

    # {{{
    @typechecked
    def emulate_browser(url:str, formdata:JSONDict|None = None, session:requests.Session=requests.Session(), level:int=1) -> Any:
      if level==7:
        raise RuntimeError("Too deep")

      # {{{
      @typechecked
      def handle_form(tree:Any) -> Any:
        print("handle form")
        form = find_node(tree, "form")
        if len(form) == 1:
          # Build the payload
          payload={}
          y = find_node(form[0], "input")
          for c in y:
            if "name" not in c.attrib:
              raise RuntimeError("Missing name")
            name = c.attrib["name"]
            if name == "userId":
              payload[name] = control.get('_userId').as_str()
            elif name == "password":
              payload[name] = control.get('_password').as_str()
            elif name == "forNino":
              payload[name] = parameters.get("nino").as_str()
            elif name == "listOfSuccessEvidences":
              payload[name] = ""
            elif name == "requiredResult":
              payload[name] = "Success"
            elif "value" in c.attrib:
              payload[name] = c.attrib["value"]
            else:
              raise RuntimeError(f"Unhandled form element {html.tostring(c, encoding='utf8').decode('utf8')}")
            print(f"set {name} to {payload[name]}")

          url=f'https://test-www.tax.service.gov.uk{form[0].attrib["action"]}'
          return emulate_browser(url, formdata=payload, session=session, level=level+1)

        # We're probably done here
        x = find_node(tree, "head")
        if len(x) != 1:
          raise RuntimeError("Unexpected head")

        x = find_node(x[0], "title")
        if len(x) != 1:
          raise RuntimeError("Unexpected title")

        status=x[0].text
        if status.startswith("Success code="):
          return status[8:]

        raise RuntimeError("No Success")
      # }}} handle_form

      # {{{ find_node
      @typechecked
      def find_node(root:Any, tag:str, attrib:str|None=None, value:str|None=None) -> list[Any]:
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
      # }}} find_node

      if formdata is None:
        logger.debug(f"REQUESTING:{url}\nlevel={level}")
        time.sleep(0.5)
        sys.stdout = _PrintBuffer()
        response = session.get(url)
        logger.debug(_PrintBuffer.getText())
        _PrintBuffer.reset()
        with open(f"logs/log.{level}.html", "w", encoding="utf-8") as f:
          f.write(f"Requested get:url={url}")
          f.write(response.text)
        if response.status_code != 200:
          logger.debug(f"Failed {response.status_code}")
          return None
        tree = html.fromstring(response.text)
        a = find_node(tree, "a", "role", "button")
        if len(a) == 1:
          url=f'https://test-www.tax.service.gov.uk{a[0].attrib["href"]}'
          return emulate_browser(url, session=session, level=level+1)

        return handle_form(tree)

      logger.debug(f"REQUESTING:{url}\n{formdata}\nlevel={level}")
#      print(f"formdata={formdata}")
      sys.stdout = _PrintBuffer()
      response = session.post(url, data=formdata)
      logger.debug(_PrintBuffer.getText())
      _PrintBuffer.reset()
      with open(f"logs/log.{level}.html", "w", encoding="utf-8") as f:
        f.write(f"Requested post:url={url} data={formdata}")
        f.write(response.text)
      if response.status_code != 200:
#        print(f"Failed {response.status_code}")
        return None
      tree = html.fromstring(response.text)
      return handle_form(tree)
    # }}} emulate_browser

    # {{{
    @typechecked
    def parse_request(data:Any, nonce:str) -> Any:
      @typechecked
      def extract_params(data:Any) -> Any:
        @typechecked
        def do_split(data:Any, c:str) -> Any:
          return data.split(c.encode('utf-8'))

        @typechecked
        def extract_get(data:Any) -> Any:
          for i in do_split(data, '\n'):
            if i.decode('utf-8')[0:4].upper() == 'GET ':
              return do_split(i, ' ')[1]
          raise RuntimeError('Missing GET in request header')

        params={}
        get = extract_get(data)
        paramtxt = do_split(get, '?')[1]

        for i in do_split(paramtxt, '&'):
          k,v = i.split('='.encode('utf-8'))
          params[k.decode('utf-8')] = v.decode('utf-8')
        return params

      params=extract_params(data)

      if 'state' not in params:
        raise RuntimeError('GET request is missing nonce (state) parameter')

      if params['state'] != nonce:
        raise RuntimeError('GET request has wrong nonce (state) parameter')

      if 'error' in params:
        raise RuntimeError(params["error_description"])

      if 'code' not in params:
        raise RuntimeError('Missing code in GET request')

      return params['code']
    # }}} parse_request

    code_verifier="".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~") for _ in range(64))
    hashval = hashlib.sha256()
    hashval.update(code_verifier.encode('utf-8'))
    code_challenge = base64.urlsafe_b64encode(hashval.digest()).rstrip(b'=').decode('ascii')

    # For testing purposes we can automate the browser calls to do the OAuth stuff
    # It's always off if unless we're talking to the Sandbox
    automateBrowser = control.get("_server").as_str() == "Sandbox"

    if "automateBrowser" in control.keys():
      automateBrowser = control.get("automateBrowser").as_bool()

    if automateBrowser:
      redirect = 'urn:ietf:wg:oauth:2.0:oob'
      url=f'https://test-www.tax.service.gov.uk/oauth/authorize?response_type=code&client_id={application_id}&scope={"%20".join(scope)}&state={nonce}&redirect_uri={redirect}&code_challenge={code_challenge}&code_challenge_method=S256'
      print()
      print(f"userID   = {control.get('_userId').as_str()}")
      print(f"password = {control.get('_password').as_str()}")
#      print(f"nino     = {nino}")
#      print(f"vrn      = {vrn}")
#      print(f"utr      = {utr}")

      print(['firefox', f'{url}'])
      v = emulate_browser(url)
      print(f"Got {v} from emulate_browser")
      params = urllib.parse.parse_qs(v)
      if params is None:
        raise RuntimeError('OAuth request failed')
      if 'state' not in params or params['state'][0] != nonce:
        raise RuntimeError('OAuth request has wrong or missing nonce (state) parameter')
      code = params['code'][0]
    else:
      redirect = 'http://localhost:8080/'
      url=f'https://test-www.tax.service.gov.uk/oauth/authorize?response_type=code&client_id={application_id}&scope={"%20".join(scope)}&state={nonce}&redirect_uri={redirect}&code_challenge={code_challenge}&code_challenge_method=S256'
      addr = ('localhost', 8080)
      socks = [ ]

      try:
        s6 = socket.socket(family=socket.AF_INET6)
        s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s6.bind(addr)
        s6.listen(1)
        socks.append(s6)
      except: # pylint: disable=bare-except
        pass

      try:
        s4 = socket.socket(family=socket.AF_INET)
        s4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s4.bind(addr)
        s4.listen(1)
        socks.append(s4)
      except: # pylint: disable=bare-except
        pass

      if len(socks) == 0:
        raise RuntimeError("cannot bind port 8080")

      #Print this so we know what userId and password to login as for testing!
      print(f"userID   = {control.get('_userId').as_str()}")
      print(f"password = {control.get('_password').as_str()}")
#      print(f"nino     = {nino}")
#      print(f"vrn      = {vrn}")
#      print(f"utr      = {utr}")

      #TODO - make browser configurable by application
      print()
      print(['firefox', f'{url}'])
#      subprocess.Popen(['firefox', 'https://test-www.tax.service.gov.uk/oauth/authorize?response_type=code&client_id=7B3aGjPqnLpiiPfH6nuqNleO6PZU&scope=' + "%20".join(scope) + '&state=' + nonce + '&redirect_uri=http://localhost:8080/'])

      data=''
      while not data:
        readable,_writable,_exceptionavailable = select.select(socks,[],[])
        for s in readable:
          if s in (s4, s6):
            client, _address = s.accept()
            socks.append(client)
          else:
            data = s.recv(1024)
            try:
#              print(f"received: {data}")
              code = parse_request(data, nonce)
              s.send(b'HTTP/1.1 200\nConnection:close\nContent-type: text/html\n\n<HTML><BODY>Close this window</BODY></HTML>')
            except:
              s.send(b'HTTP/1.1 200\nConnection:close\nContent-type: text/html\n\n<HTML><BODY>Request failed</BODY></HTML>')
              raise

    oauth_data = {
      "client_id":     application_id,
      "grant_type":    "authorization_code",
      "redirect_uri":  redirect,
      "code":          code,  # pylint: disable=possibly-used-before-assignment
      "code_verifier": code_verifier,
    }

    token = self.__request_user_token(oauth_data, user_auth)
    user_auth.set('scope', cast(JSONList,scope))
    self._config._flush() # pylint: disable=protected-access

    return token
  # }}} request_user_token
# }}} class OAuth

# vim: set sw=2 sts=2 ts=2 expandtab:
