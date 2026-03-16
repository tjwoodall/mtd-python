{
  "description": "Test individuals-employments-income-api request",
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
    "include": "tests/example/individuals-employments-income-api.2.0._individuals_employments-income_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individuals-employments-income-api.2.0"],
      ["COPY", ["individuals-employments-income-api.2.0", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["COPY", ["individuals-employments-income-api.2.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-employments-income-api.2.0", "", "_control", "_userId"],
      ["COPY", ["individuals-employments-income-api.2.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "individuals-employments-income-api.2.0", "", "_control", "_password"],
      ["COPY", ["individuals-employments-income-api.2.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["EDIT", "individuals-employments-income-api.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individuals-employments-income-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "employments", "0", "", "employmentId"], "00000000-0000-4000-8000-000000000000"],
      ["GOTO", "END"]
    ]
  }
}
