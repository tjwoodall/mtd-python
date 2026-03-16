{
  "description": "Test self-assessment-biss-api request",
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
    "include": "tests/example/self-assessment-biss-api.3.0._individuals_self-assessment_income-summary_{nino}_{typeOfBusiness}_{taxYear}_{businessId}-get.example.py",
    "press": [
      ["GENSHEET", "self-assessment-biss-api.3.0"],
      ["COPY", ["self-assessment-biss-api.3.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["self-assessment-biss-api.3.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-biss-api.3.0", "", "_control", "_userId"],
      ["COPY", ["self-assessment-biss-api.3.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-biss-api.3.0", "", "_control", "_password"],
      ["COPY", ["self-assessment-biss-api.3.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "self-assessment-biss-api.3.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "self-assessment-biss-api.3.0", "", "_parameters", "typeOfBusiness", "self-employment"],
      ["EDIT", "self-assessment-biss-api.3.0", "", "_parameters", "businessId", "XAIS12345678910"],
      ["SUBMIT", "self-assessment-biss-api.3.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "total", "expenses"], 125.49],
      ["GOTO", "END"]
    ]
  }
}
