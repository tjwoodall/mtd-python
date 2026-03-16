{
  "description": "Test individuals-state-benefits-api request",
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
    "include": "tests/example/individuals-state-benefits-api.2.0._individuals_state-benefits_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-state-benefits-api.2.0"],
      ["COPY", ["individuals-state-benefits-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-state-benefits-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-state-benefits-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-state-benefits-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-state-benefits-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-state-benefits-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-state-benefits-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-state-benefits-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "stateBenefits", "0", "", "amount"], 34345.55],
      ["GOTO", "END"]
    ]
  }
}
