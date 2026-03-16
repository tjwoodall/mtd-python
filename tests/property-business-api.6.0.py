{
  "description": "Test individuals-disclosures-api request",
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
    "include": "tests/example/property-business-api.6.0._individuals_business_property_uk_{nino}_{businessId}_cumulative_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-disclosures-api.2.0"],
      ["COPY", ["individuals-disclosures-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-disclosures-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-disclosures-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-disclosures-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-disclosures-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-disclosures-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-disclosures-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "individuals-disclosures-api.2.0", "", "_parameters", "businessId", "XAIS12345678910"],
      ["ADD", "individuals-disclosures-api.2.0", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "individuals-disclosures-api.2.0", "", "_parameters", "Gov-Test-Scenario", "UK_PROPERTY_CONSOLIDATED"],
      ["SUBMIT", "individuals-disclosures-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "ukProperty", "expenses", "consolidatedExpenses"], 998.18],
      ["GOTO", "END"]
    ]
  }
}
