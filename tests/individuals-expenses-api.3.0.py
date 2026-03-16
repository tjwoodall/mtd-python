{
  "description": "Test individuals-expenses-api request",
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
    "include": "tests/example/individuals-expenses-api.3.0._individuals_expenses_employments_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-expenses-api.3.0"],
      ["COPY", ["individuals-expenses-api.3.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-expenses-api.3.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-expenses-api.3.0", "", "_control", "_userId"],
      ["COPY", ["individuals-expenses-api.3.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-expenses-api.3.0", "", "_control", "_password"],
      ["COPY", ["individuals-expenses-api.3.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-expenses-api.3.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-expenses-api.3.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "expenses", "businessTravelCosts"], 326.71],
      ["GOTO", "END"]
    ]
  }
}
