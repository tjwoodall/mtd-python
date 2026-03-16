{
  "description": "Test other-deductions-api request",
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
    "include": "tests/example/other-deductions-api.2.0._individuals_deductions_other_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "other-deductions-api.2.0"],
      ["COPY", ["other-deductions-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["other-deductions-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "other-deductions-api.2.0", "", "_control", "_userId"],
      ["COPY", ["other-deductions-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "other-deductions-api.2.0", "", "_control", "_password"],
      ["COPY", ["other-deductions-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "other-deductions-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "other-deductions-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "seafarers", "0", "", "amountDeducted"], 2543.32],
      ["GOTO", "END"]
    ]
  }
}
