{
  "description": "Test individuals-capital-gains-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
  ],

  "Submit a Self Assessment Final Declaration": {
    "include": "tests/individual-calculations-api/8.0-final-declaration-gov-test.py"
  },

  "List Self Assessment Tax Calculations": {
    "include": "tests/individual-calculations-api/8.0-list-gov-test.py"
  },

  "Retrieve a Self Assessment Tax Calculation": {
    "include": "tests/individual-calculations-api/8.0-retrieve-gov-test.py"
  },

  "Trigger a Self Assessment Tax Calculation": {
    "include": "tests/individual-calculations-api/8.0-trigger-gov-test.py"
  },

  "START": {
    "press": [
      ["GOSUB", "Submit a Self Assessment Final Declaration"],
      ["GOSUB", "List Self Assessment Tax Calculations"],
      ["GOSUB", "Retrieve a Self Assessment Tax Calculation"],
      ["GOSUB", "Trigger a Self Assessment Tax Calculation"],

      ["GOTO", "END"]
    ]
  },
}
