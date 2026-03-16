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

import decimal
import json
import numbers
import re
import datetime
from typing import Any, Generator
import jsonschema

from typeguard import typechecked

from .JSONTypes import JSONType, JSONDict, Jstr

from .LOG import logger

# {{{
class Validator:
  class ValidationError(Exception):
    pass

  class BadInstance(Exception):
    def __init__(self, message:str, errors:list[jsonschema.ValidationError]):
      super().__init__(message)
      self.errors=errors

  validator_schema = {
    "http://json-schema.org/draft-04/schema#": jsonschema.Draft4Validator,
    "http://json-schema.org/draft-07/schema#": jsonschema.Draft7Validator,
    "https://json-schema.org/draft/2019-09/schema": jsonschema.Draft201909Validator
  }

  # {{{
  @typechecked
  @staticmethod
  def _decimal_multiple_of(validator:object, multipleOf:numbers.Number, instance:numbers.Number, s:dict[str,Any]) -> Generator[jsonschema.ValidationError, None, None]:
    if isinstance(instance, (int, float, decimal.Decimal)):
      try:
        # Use Decimal for precision comparison
        if decimal.Decimal(str(instance)) % decimal.Decimal(str(multipleOf)) != 0:
          yield jsonschema.ValidationError(f"{instance} is not a multiple of {multipleOf}")
      except (decimal.InvalidOperation, TypeError):
        yield jsonschema.ValidationError(f"{instance} could not be validated with multipleOf")
    else:
      yield jsonschema.ValidationError(f"{instance} is not a number")
  # }}} decimal_multiple_of

  # {{{
#  @typechecked - don't know why but typeguard doesn't like this function in libreoffice
  @staticmethod
  def validate(instance:JSONType, schema:JSONDict) -> None:
    if '$schema' in schema:
      if schema["$schema"] not in Validator.validator_schema:
        raise Validator.ValidationError(f"Unsupported schema {schema['$schema']}. Update downloads.sh to fetch it")
      validator_cls = Validator.validator_schema[Jstr(schema, "$schema")]
    else:
      # third-party-payments-external-api only works with draft-04 due to exclusiveMinimum
      validator_cls = Validator.validator_schema["http://json-schema.org/draft-04/schema#"]

    checker = jsonschema.FormatChecker()

    # {{{
    @typechecked
    @checker.checks("int32")
    def is_valid_int32(value:Any) -> bool:
      if isinstance(value, int):
        return True
      return False
    # }}} is_valid_int32

    # {{{
    @typechecked
    @checker.checks("int64")
    def is_valid_int64(value:Any) -> bool:
      if isinstance(value, int):
        return True
      return False
    # }}} is_valid_int64

    # {{{
    @typechecked
    @checker.checks("double")
    def is_valid_double(value:Any) -> bool:
      if isinstance(value, (float, int)):
        return True
      return False
    # }}} is_valid_double

    # {{{
    @typechecked
    @checker.checks("tax-year")
    def is_valid_tax_year(value: Any) -> bool:
      if not isinstance(value, str):
        return False
      match = re.fullmatch(r"(\d{4})-(\d{2})", value)
      if not match:
        return False

      full_year = int(match.group(1))
      short_next = int(match.group(2))
      return short_next == (full_year + 1) % 100
    # }}} is_valid_tax_year

  #  # {{{
  #  @typechecked
  #  @checker.checks("full-date")
  #  def is_valid_date(value:Any) -> bool:
  #    if not isinstance(value, str):
  #      return True
  #    import re
  #
  #    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
  #    if not match:
  #      return False
  #
  #    year = int(match.group(1))
  #    month = int(match.group(2))
  #    day = int(match.group(3))
  #    try:
  #      import datetime
  #      datetime.date(year, month, day)
  #      return True
  #    except ValueError:
  #      return False
  #  # }}} is_valid_date

    # {{{
    # ExpiresOn is missing the Z at the end
    @typechecked
    @checker.checks("date-timeX")
    def is_valid_date_time(value: Any) -> bool:
      if not isinstance(value, str):
        return False
      match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.\d{3}", value)
      if not match:
        return False

      year = int(match.group(1))
      month = int(match.group(2))
      day = int(match.group(3))
      hour = int(match.group(4))
      minute = int(match.group(5))
      second = int(match.group(6))
      try:
        datetime.date(year, month, day)
        datetime.time(hour, minute, second)
        return True
      except ValueError:
        return False
    # }}} is_valid_date_time

    if 'format' in schema and schema['format'] not in checker.checkers.keys():
      raise Validator.ValidationError(f"Unknown format {schema['format']}")

    try:
      validator_cls.check_schema(schema)
    except jsonschema.exceptions.ValidationError as e:
      logger.error(f"Check schema failed {e.message}")
      raise Validator.ValidationError(f"{e.message}")
    except Exception as e:
      raise Validator.ValidationError("Validation failed") from e

    validator = validator_cls(schema, format_checker=checker)

    errors = sorted(validator.iter_errors(instance), key=lambda e: tuple(e.path))

    if not errors:
      return

    logger.error(f"Found {len(errors)} validation error(s):")
    attempt = {"schema": schema, "instance": instance}
    logger.error(f"falied validating:\n{json.dumps(attempt, indent=1)}")
    for eidx,error in enumerate(errors):
      path = ".".join([str(p) for p in error.absolute_path])
      logger.error(f"Error {eidx})")
      logger.error(f"  • Path: {path or '[root]'}")
      logger.error(f"    Message: {error.message}")
      logger.error()

      if error.context:
        logger.error(f"Sub-errors ({len(error.context)}):")
        for sidx, sub in enumerate(error.context):
          logger.error(f'eidx={eidx} sidx={sidx} error:{sub}')

    raise Validator.BadInstance(f"Invalid instance", errors)

#    for eidx,error in enumerate(errors):
#      path = ".".join([str(p) for p in error.absolute_path])
#      print(f"Error {eidx})")
#      print(f"  • Path: {path or '[root]'}")
#      print(f"    Message: {error.message}")
#      print()
#
#      if error.context:
#        print(f"Sub-errors ({len(error.context)}):")
#        for sidx, sub in enumerate(error.context):
#          print(f'eidx={eidx} sidx={sidx} error:{sub}')
#
#    attempt = { "schema": schema, "instance": instance }
#    raise Validator.BadInstance(f"Invalid instance.", attempt)

    # }}} validate

# }}} class Validator

for k,v in Validator.validator_schema.items():
  v.VALIDATORS["multipleOf"] = Validator._decimal_multiple_of # pylint: disable=protected-access


#from openapi_core.validation.request.validators import RequestValidator
#from openapi_core.validation.request.datatypes import RequestParameters
#from werkzeug.datastructures import Headers
#
## Your input
#path = "/my-endpoint"
#method = "post"
#query = {"param1": "abc"}
#headers = {"X-Custom-Header": "value"}
#body = {"id": 123, "name": "Alice"}
#
## Wrap headers properly
#headers_wrapped = Headers(headers)
#
## Prepare request parameters
#parameters = RequestParameters(
#    path={},
#    query=query,
#    header=headers,
#    cookie={}
#)
#
## Fake request (doesn't send anything)
#from openapi_core.templating.paths.finders import PathFinder
#from openapi_core.validation.request.datatypes import RequestValidationResult
#
#class CustomRequest:
#    def __init__(self, full_url_pattern, method, parameters, body, mimetype):
#        self.full_url_pattern = full_url_pattern
#        self.method = method
#        self.parameters = parameters
#        self.body = body
#        self.mimetype = mimetype
#
## Construct the request
#request = CustomRequest(
#    full_url_pattern=path,
#    method=method,
#    parameters=parameters,
#    body=body,
#    mimetype="application/json"
#)
#
## Validate the request
#validator = RequestValidator(spec)
#result: RequestValidationResult = validator.validate(request)
#
## Raise error if not valid
#result.raise_for_errors()


# vim: set sw=2 sts=2 ts=2 expandtab:
