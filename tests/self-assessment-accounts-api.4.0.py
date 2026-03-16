{
  "description": "Test self-assessment-accounts-api request",
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
    "include": "tests/example/self-assessment-accounts-api.4.0._accounts_self-assessment_{nino}_{taxYear}_collection_tax-code_coding-out_status-get.example.py",
    "press": [
      ["GENSHEET", "self-assessment-accounts-api.4.0"],
      ["COPY", ["self-assessment-accounts-api.4.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["self-assessment-accounts-api.4.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-accounts-api.4.0", "", "_control", "_userId"],
      ["COPY", ["self-assessment-accounts-api.4.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-accounts-api.4.0", "", "_control", "_password"],
      ["COPY", ["self-assessment-accounts-api.4.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "self-assessment-accounts-api.4.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "self-assessment-accounts-api.4.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "taxYear"], "2019-20"],
      ["GOTO", "END"]
    ]
  }
}
