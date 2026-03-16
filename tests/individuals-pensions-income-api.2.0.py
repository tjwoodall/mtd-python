{
  "description": "Test individuals-pensions-income-api request",
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
    "include": "tests/example/individuals-pensions-income-api.2.0._individuals_pensions-income_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-pensions-income-api.2.0"],
      ["COPY", ["individuals-pensions-income-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-pensions-income-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-pensions-income-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-pensions-income-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-pensions-income-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-pensions-income-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-pensions-income-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-pensions-income-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "foreignPensions", "0", "", "countryCode"], "DEU"],
      ["GOTO", "END"]
    ]
  }
}
