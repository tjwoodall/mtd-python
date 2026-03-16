{
  "description": "Test individuals-capital-gains-income-api request",
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
    "include": "tests/example/individuals-capital-gains-income-api.2.0._individuals_disposals-income_other-gains_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-capital-gains-income-api.2.0"],
      ["COPY", ["individuals-capital-gains-income-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-capital-gains-income-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-capital-gains-income-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-capital-gains-income-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-capital-gains-income-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-capital-gains-income-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-capital-gains-income-api.2.0", "", "_parameters", "taxYear", "2024-25"],
      ["SUBMIT", "individuals-capital-gains-income-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "disposals", "0", "", "disposalDate"], "2021-05-07"],
      ["GOTO", "END"]
    ]
  }
}
