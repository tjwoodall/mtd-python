#!/usr/bin/env -S python3 -O

# typechecked is painfully slow! Remove -O to enable

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
import sys
from typing import Any, cast, NoReturn

from typeguard import typechecked

from mtd.JSONTypes import JSONType, JSONDict, JSONList

# {{{
@typechecked
def print_stack(indent:str = "", one_line:bool=False, last_file:bool=False) -> None:
  if last_file:
    for r in ref_stack[::-1]:
      p = r.split('#',1)[0]
      if p.endswith(".yaml") or p.endswith(".json"):
        print(f"{indent}{r}")
        return
  if one_line:
    print(indent + ' / '.join(ref_stack))
    return
  for r in ref_stack:
    print(f"{indent}{r}")
    indent += "  "
# }}} print_stack

# {{{
@typechecked
def fatal(err:str, obj:JSONType) -> NoReturn:
  sys.stdout.flush()
  print("-------- FATAL --------")
  print_stack()
  print("-----------------------")
  print(json.dumps(obj, indent=2, sort_keys=True))
  print("-----------------------")
  raise RuntimeError(err)
# }}} fatal

ref_stack : list[str] = []
# {{{
@typechecked
def _validate_keys(obj:JSONDict, allowed_keys: set[str]) -> None:
  if set(obj.keys()) - allowed_keys:
    fatal(f"_validate_keys unexpected keys: {obj.keys()-allowed_keys}", obj)
# }}} _validate_keys

# N.B. allowed_keys is the set of keys allowed in the resolved object
# {{{
class RefTrackerBase:
  # {{{
  @typechecked
  def __init__(self, obj:JSONDict, key:str, allowed_keys:set[str]|None = None):
    if key not in obj:
      fatal(f"RefTracker missing key: {key}", obj)

    self.obj = cast(JSONType, obj[key])

    if allowed_keys is not None:
      _validate_keys(cast(JSONDict, self.obj), allowed_keys)

    ref_stack.append(f'{key}')
  # }}} __init__

  # {{{
  @typechecked
  def __enter__(self) -> JSONType:
    return self.obj
  # }}} __enter__

  # {{{
  @typechecked
  def __exit__(self, exc_type:Any, exc_value:Any, traceback:Any) -> None:
    ref_stack.pop()
  # }}} __exit__
# }}} class RefTrackerBase

class RefTrackerDict(RefTrackerBase):
  # {{{
  @typechecked
  def __enter__(self) -> JSONDict:
    if not isinstance(self.obj, dict):
      fatal("Not a dict", self.obj)
    return cast(JSONDict, self.obj)
  # }}} __enter__

class RefTrackerList(RefTrackerBase):
  # {{{
  @typechecked
  def __enter__(self) -> JSONList:
    if not isinstance(self.obj, list):
      fatal("Not a list", self.obj)
    return cast(JSONList, self.obj)
  # }}} __enter__

# see https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#errors
default_responses = """
{
  "401": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "MISSING_CREDENTIALS",
                "INVALID_CREDENTIALS",
                "UNAUTHORIZED",
                "INCORRECT_ACCESS_TOKEN_TYPE"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "MISSING_CREDENTIALS",
            "message": "Authentication information is not provided"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "403": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "HTTPS_REQUIRED",
                "RESOURCE_FORBIDDEN",
                "INVALID_SCOPE",
                "FORBIDDEN"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "RESOURCE_FORBIDDEN",
            "message": "The application is not subscribed to the API which it is attempting to invoke"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "404": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "MATCHING_RESOURCE_NOT_FOUND"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "MATCHING_RESOURCE_NOT_FOUND",
            "message": "No endpoint for the request path"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "405": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "METHOD_NOT_ALLOWED"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "METHOD_NOT_ALLOWED",
            "message": "Request method must be one of GET, PUT, POST, PATCH, DELETE or OPTIONS"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "406": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "ACCEPT_HEADER_INVALID"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "ACCEPT_HEADER_INVALID",
            "message": "Missint or invalid Accept header"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "429": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "MESSAGE_THROTTLED_OUT"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "MESSAGE_THROTTLED_OUT",
            "message": "The application has reached its maximum rate limit"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "500": {
    "content": {
      "application/json": {
        "schema": {
          "oneOf": [
            {
              "properties": {
                "code": {
                  "type": "string",
                  "description": "Error Code",
                  "enum": [
                    "INTERNAL_SERVER_ERROR"
                  ]
                },
                "message": {
                  "type": "string"
                }
              },
              "type": "object",
              "example": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error"
              }
            },
            {
              "type": "string",
              "example": "Failed to process request"
            }
          ]
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "501": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "NOT_IMPLEMENTED"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "NOT_IMPLEMENTED",
            "message": "API not implemented or deployed"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "503": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "SERVER_ERROR",
                "SCHEDULED_MAINTENANCE"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "SCHEDULED_MAINTENANCE",
            "message": "Scheduled maintenance"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "504": {
    "content": {
      "application/json": {
        "schema": {
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code",
              "enum": [
                "GATEWAY_TIMEOUT"
              ]
            },
            "message": {
              "type": "string"
            }
          },
          "type": "object",
          "example": {
            "code": "GATEWAY_TIMEOUT",
            "message": "Request timed out"
          }
        }
      }
    },
    "description": "UNAUTHORISED Response"
  }
}
"""

default_xml_responses = """
{
  "401": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "403": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "404": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "405": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "406": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "429": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "500": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "501": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "503": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  },
  "504": {
    "content": {
      "application/xml": {
        "schema": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "Error Code"
            },
            "message": {
              "type": "string"
            }
          },
          "xml": {
            "name": "errorResponse"
          }
        },
        "example": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<errorResponse>\\n  <code>CDS60001</code>\\n  <message>Declaration not found</message>\\n</errorResponse>"
      }
    },
    "description": "UNAUTHORISED Response"
  }
}
"""


default_responses_json = json.loads(default_responses)
default_responses_xml = json.loads(default_xml_responses)

# {{{
@typechecked
def process_action(action:JSONDict) -> None:

  with RefTrackerDict(action, 'responses', { '200', '201', '202', '204', '400', '401', '403', '404', '405', '406', '409', '410', '413', '415', '422', '429', '500', '501', '503', '504', }) as responses:
    isXML = False
    for k,v in responses.items():
      if 'content' in v and 'application/xml' in v['content']:
        isXML = True
    for k,v in default_responses_json.items():
      if k not in responses:
        responses[k] = v
        if isXML:
          responses[k]['content']['application/xml'] = default_responses_xml[k]['content']['application/xml']
# }}} process_action

# Iterate through every action on the endpoint
# {{{
@typechecked
def process_ep(ep:JSONDict) -> None:
  for action_key in ep:
    if action_key == 'parameters':
      continue
    with RefTrackerDict(ep, action_key) as action:
      print_stack(one_line=True)
      valid_keys = {'operationId',
              'parameters',
              'deprecated',
              'security',
              'tags',
              'summary',
              'responses',
              'description',
              'requestBody'}

      _validate_keys(action, valid_keys)
      process_action(action)
# }}} process_ep

# Iterate through every endpoint
# {{{
@typechecked
def process_endpoints(endpoints:JSONDict) -> None:
  for ep_key in endpoints:
    keys = {
        'delete',
        'get',
        'post',
        'put',
        'parameters',
        'patch',
        }
    with RefTrackerDict(endpoints, ep_key, keys) as ep:
      process_ep(ep)
# }}} process_endpoints

# Get the endpoints for every minor version
# {{{
@typechecked
def process_major(major:JSONDict) -> None:
  for minor_key in major:
    keys = {
        'paths',
        'info',
        'servers',
        'tags',
        'components',
        'openapi',
        }
    with RefTrackerDict(major, minor_key, keys) as minor:
      print_stack(one_line=True)
      if "paths" in minor:
        with RefTrackerDict(minor, "paths") as endpoints:
          process_endpoints(endpoints)
# }}} process_major

# Iterate through every major version in the API
# {{{
@typechecked
def process_api(api:JSONDict) -> None:
  for major_key in api:
    with RefTrackerDict(api, major_key) as major:
      process_major(major)
# }}} process_api

# Iterate through every API
# {{{
@typechecked
def process(obj:JSONDict) -> None:
  for api_key in obj:
    with RefTrackerDict(obj, api_key) as api:
      process_api(api)
# }}} process

with open(sys.argv[1], "r", encoding="utf-8") as f:
  application = json.load(f)

process(application)

with open(sys.argv[1], "w", encoding="utf-8") as f:
  json.dump(application, f, indent=2)

# vim: set sw=2 sts=2 ts=2 expandtab:
