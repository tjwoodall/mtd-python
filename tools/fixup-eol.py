#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

def git(*args: str, check: bool = True) -> str:
  result = subprocess.run(
    ["git", *args],
    check=check,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  )
  return result.stdout.decode("utf-8", errors="surrogateescape")


def git_blob(rev: str, path: str) -> bytes:
  result = subprocess.run(
    ["git", "show", f"{rev}:{path}"],
    check=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
  )
  if result.returncode != 0:
    # Probably added/deleted/renamed; ignore.
    return b""
  return result.stdout


def is_binary(data: bytes) -> bool:
  return b"\0" in data


def main() -> int:
  changed = False

  files = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--diff-filter=M", "HEAD").splitlines()

  for path in files:
    before = git_blob("HEAD^", path)
    after = git_blob("HEAD", path)

    if not before or not after:
      # Skip added/deleted files.
      continue

    if is_binary(before) or is_binary(after):
      continue

    parent_has_nl = before.endswith(b"\n")
    current_has_nl = after.endswith(b"\n")

    if not parent_has_nl and current_has_nl:
      print(f"Removing trailing newline from {path}")

      p = Path(path)
      data = p.read_bytes()

      if data.endswith(b"\n"):
        p.write_bytes(data[:-1])

        subprocess.run(["git", "add", "--", path], check=True)
        changed = True

  if changed:
    subprocess.run(
      ["git", "commit", "--amend", "--no-edit"],
      check=True,
    )

  return 0

if __name__ == "__main__":
  sys.exit(main())
