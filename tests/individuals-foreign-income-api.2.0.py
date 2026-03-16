{
  "description": "Test individuals-foreign-income-api request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/individuals-foreign-income-api.2.0._individuals_foreign-income_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-foreign-income-api.2.0"],
      ["COPY", ["individuals-foreign-income-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-foreign-income-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-foreign-income-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-foreign-income-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-foreign-income-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-foreign-income-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-foreign-income-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-foreign-income-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "unremittableForeignIncome", "0", "", "countryCode"], "FRA"],
      ["GOTO", "END"]
    ]
  }
}
