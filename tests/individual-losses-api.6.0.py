{
  "description": "Test individual-losses-api request",
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
    "include": "tests/example/individual-losses-api.6.0._individuals_losses_{nino}_brought-forward-losses_tax-year_{taxYearBroughtForwardFrom}-get.example.py",
    "press": [
      ["GENSHEET", "individual-losses-api.6.0"],
      ["COPY", ["individual-losses-api.6.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individual-losses-api.6.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individual-losses-api.6.0", "", "_control", "_userId"],
      ["COPY", ["individual-losses-api.6.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individual-losses-api.6.0", "", "_control", "_password"],
      ["COPY", ["individual-losses-api.6.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individual-losses-api.6.0", "", "_parameters", "taxYearBroughtForwardFrom", "2025-26"],
      ["ADD", "individual-losses-api.6.0", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "individual-losses-api.6.0", "", "_parameters", "Gov-Test-Scenario", "SELF_EMPLOYMENT"],
      ["SUBMIT", "individual-losses-api.6.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "losses", "0", "", "lossAmount"], 9420.0],
      ["GOTO", "END"]
    ]
  }
}
