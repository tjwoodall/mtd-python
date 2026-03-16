{
  "description": "Test self-assessment-bsas-api request",
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
    "include": "tests/example/self-assessment-bsas-api.7.0._individuals_self-assessment_adjustable-summary_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "self-assessment-bsas-api.7.0"],
      ["COPY", ["self-assessment-bsas-api.7.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["self-assessment-bsas-api.7.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-bsas-api.7.0", "", "_control", "_userId"],
      ["COPY", ["self-assessment-bsas-api.7.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-bsas-api.7.0", "", "_control", "_password"],
      ["COPY", ["self-assessment-bsas-api.7.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "self-assessment-bsas-api.7.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "self-assessment-bsas-api.7.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "", "businessSources", "0", "", "typeOfBusiness"], "self-employment"],
      ["GOTO", "END"]
    ]
  }
}
