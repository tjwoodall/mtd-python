#!/usr/bin/env -S python3

from __future__ import annotations

import re
import sys


def convert(source:str) -> str:
  # @@ is escaped @ in the source format
  source = source.replace("@@", "@")

  # Build a mapping such as:
  #
  # includeRequestAdviceEndpoint -> requestAdviceEnabled
  # includeWithdrawAdviceEndpoint -> withdrawAdviceEnabled
  variables = dict(re.findall(
    r'@(\w+)\s*=\s*@\{appConfig\.(\w+)\}',
    source
  ))

  # Remove everything before and including ---
  source = re.sub(
    r'(?s)^.*?^---\s*$',
    '',
    source,
    count=1,
    flags=re.MULTILINE
  )

  # Convert @if(condition) { to {{#if (enabled ...)}}
  def replace_if(match:re.Match[str]) -> str:
    condition = match.group(1)

    # Split "foo || bar"
    names = re.split(r'\s*\|\|\s*', condition.strip())

    try:
      properties = [variables[name] for name in names]
    except KeyError as e:
      raise ValueError(
        f"Unknown condition variable: {e.args[0]}"
      ) from e

    args = ' '.join(f"'{prop}'" for prop in properties)

    return f"{{{{#if (enabled {args})}}}}"

  source = re.sub(
    r'@if\s*\(([^)]+)\)\s*\{',
    replace_if,
    source
  )

  # The remaining closing braces from @if blocks become {{/if}}.
  source = re.sub(r'(?m)^\s*}\s*$', '{{/if}}', source)

  return '\n\n---\n' + source.strip()


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <file>")
    sys.exit(1)

  with open(sys.argv[1], encoding='utf-8') as f:
    source = f.read()

  print(convert(source))
