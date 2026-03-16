{
  "description": "Test individuals-partner-income-api request",
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
    "include": "tests/example/individuals-partner-income-api.1.0._individuals_partner-income_{nino}_{taxYear}_partnership-get.example.py",
    "press": [
      ["GENSHEET", "individuals-partner-income-api.1.0"],
      ["COPY", ["individuals-partner-income-api.1.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-partner-income-api.1.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-partner-income-api.1.0", "", "_control", "_userId"],
      ["COPY", ["individuals-partner-income-api.1.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-partner-income-api.1.0", "", "_control", "_password"],
      ["COPY", ["individuals-partner-income-api.1.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-partner-income-api.1.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-partner-income-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "partnerIncomeSubmissions", "0", "", "partnershipUtr"], "4564564564"],
      ["GOTO", "END"]
    ]
  }
}
