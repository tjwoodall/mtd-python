{
  "description": "Test individuals-other-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
  ],

  "Stateful": {
    "include": "tests/individuals-other-income-api/3.0.stateful.py",
  },

  "Create and Amend Other Income": {
    "include": "tests/individuals-other-income-api/3.0-create-gov-test.py"
  },

  "Delete Other Income": {
    "include": "tests/individuals-other-income-api/3.0-delete-gov-test.py"
  },

  "Retrieve Other Income": {
    "include": "tests/individuals-other-income-api/3.0-get-gov-test.py"
  },

  "START": {
    "press": [
# Stateful tests
      ["GOSUB", "Stateful", "2025-26"],
      ["GOSUB", "Stateful", "2026-27"],

# gov-test canned responses
      ["GOSUB", "Create and Amend Other Income"],
      ["GOSUB", "Delete Other Income"],
      ["GOSUB", "Retrieve Other Income"],

      ["GOTO", "END"]
    ]
  },
}
