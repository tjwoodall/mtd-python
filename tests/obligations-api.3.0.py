{
  "description": "Test obligations-api request",
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
    "include": "tests/example/obligations-api.3.0._obligations_details_{nino}_income-and-expenditure-get.example.py",
    "press": [
      ["GENSHEET", "obligations-api.3.0"],
      ["COPY", ["obligations-api.3.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["obligations-api.3.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "obligations-api.3.0", "", "_control", "_userId"],
      ["COPY", ["obligations-api.3.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "obligations-api.3.0", "", "_control", "_password"],
      ["COPY", ["obligations-api.3.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "obligations-api.3.0", "", "_parameters", "typeOfBusiness", "self-employment"],
      ["EDIT", "obligations-api.3.0", "", "_parameters", "businessId", "XBIS12345678901"],
      ["DELETE", "obligations-api.3.0", "", "_parameters", "fromDate"],
      ["DELETE", "obligations-api.3.0", "", "_parameters", "toDate"],
      ["DELETE", "obligations-api.3.0", "", "_parameters", "status"],
      ["ADD", "obligations-api.3.0", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "obligations-api.3.0", "", "_parameters", "Gov-Test-Scenario", "DYNAMIC"],
      ["SUBMIT", "obligations-api.3.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "obligations", "0", "", "obligationDetails", "0", "", "periodStartDate"], "2026-04-06"],
      ["GOTO", "END"]
    ]
  }
}
