{
  "description": "Test self-employment-business-api request",
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
    "include": "tests/example/self-employment-business-api.5.0._individuals_business_self-employment_{nino}_{businessId}_cumulative_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "self-employment-business-api.5.0"],
      ["COPY", ["self-employment-business-api.5.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["self-employment-business-api.5.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-employment-business-api.5.0", "", "_control", "_userId"],
      ["COPY", ["self-employment-business-api.5.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-employment-business-api.5.0", "", "_control", "_password"],
      ["COPY", ["self-employment-business-api.5.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "self-employment-business-api.5.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "self-employment-business-api.5.0", "", "_parameters", "businessId", "XAIS12345678910"],
      ["SUBMIT", "self-employment-business-api.5.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "periodDates", "periodStartDate"], "2025-04-06"],
      ["GOTO", "END"]
    ]
  }
}
