{
  "description": "Test self-assessment-assist request",
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
    "include": "tests/example/self-assessment-assist.1.0._individuals_self-assessment_assist_reports_{nino}_{taxYear}_{calculationId}-post.example.py",
    "press": [
      ["GENSHEET", "self-assessment-assist.1.0"],
      ["COPY", ["self-assessment-assist.1.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["self-assessment-assist.1.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-assist.1.0", "", "_control", "_userId"],
      ["COPY", ["self-assessment-assist.1.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-assist.1.0", "", "_control", "_password"],
      ["COPY", ["self-assessment-assist.1.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "self-assessment-assist.1.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "self-assessment-assist.1.0", "", "_parameters", "calculationId", "f2fb30e5-4ab6-4a29-b3c1-c7264259ff1c"],
      ["SUBMIT", "self-assessment-assist.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "taxYear"], "2026-27"],
      ["GOTO", "END"]
    ]
  }
}
