{
  "description": "Test ras-api request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py", "tests/include/create-business-user.py"],

  "START": {
    "press": [
      ["CALL", "Get test mtdit user", "mtdit-user-0"],
      ["GOTO", "Get test-user2"]
    ]
  },

  "Get test-user2": {
    "press": [
      ["CALL", "Get test business user", "business-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "setup": { "include": "tests/example/ras-api.2.0._individuals_relief-at-source_residency-status-post.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "ras-api.2.0"],
      ["COPY", ["ras-api.2.0", "_control", "_username"], ["business-user-0", "json", "userId"]],
      ["ADD", ["ras-api.2.0", "_control", "_userId"]],
      ["COPY", ["ras-api.2.0", "_control", "_userId"], ["business-user-0", "json", "userId"]],
      ["ADD", ["ras-api.2.0", "_control", "_password"]],
      ["COPY", ["ras-api.2.0", "_control", "_password"], ["business-user-0", "json", "password"]],
      ["EDIT", ["ras-api.2.0", "json", "nino"], "CC123456C"],
      ["EDIT", ["ras-api.2.0", "json", "firstName"], "Joe"],
      ["EDIT", ["ras-api.2.0", "json", "lastName"], "Bloggs"],
      ["EDIT", ["ras-api.2.0", "json", "dateOfBirth"], "1982-02-17"],
      ["SUBMIT", "ras-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "json", "currentYearResidencyStatus"], "scotResident"],
      ["GOTO", "END"]
    ]
  }
}
