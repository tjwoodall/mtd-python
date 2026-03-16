{
  "description": "Test individuals-tax-liability-adjustments-api request",
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
    "include": "tests/example/individuals-tax-liability-adjustments-api.1.0._individuals_tax-liability_adjustments_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-tax-liability-adjustments-api.1.0"],
      ["COPY", ["individuals-tax-liability-adjustments-api.1.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-tax-liability-adjustments-api.1.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-tax-liability-adjustments-api.1.0", "", "_control", "_userId"],
      ["COPY", ["individuals-tax-liability-adjustments-api.1.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-tax-liability-adjustments-api.1.0", "", "_control", "_password"],
      ["COPY", ["individuals-tax-liability-adjustments-api.1.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-tax-liability-adjustments-api.1.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-tax-liability-adjustments-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "carryBackLossesDecrease", "incomeTax"], 5000.99],
      ["GOTO", "END"]
    ]
  }
}
