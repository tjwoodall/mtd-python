{
  "description": "Test individual-losses-api 7.0",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "Create or amend": {
    "include": "tests/individual-losses-api/7.0-stateful.py",
  },

  "START": {
    "press": [
# Stateful tests
      ["GOSUB", "Create or amend", "mtdit-user-both", "list businesses.both"],
      ["GOTO", "END"]
    ]
  },
}
