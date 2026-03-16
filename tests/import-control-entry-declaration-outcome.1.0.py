{
  "description": "Test import-control-entry-declaration-outcome request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-business-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test business user 0 on sheet business-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/import-control-entry-declaration-outcome.1.0._customs_imports_outcomes-get.example.py",
    "press": [
      ["GENSHEET", "import-control-entry-declaration-outcome.1.0"],
      ["COPY", ["import-control-entry-declaration-outcome.1.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "import-control-entry-declaration-outcome.1.0", "", "_control", "_userId"],
      ["COPY", ["import-control-entry-declaration-outcome.1.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "import-control-entry-declaration-outcome.1.0", "", "_control", "_password"],
      ["COPY", ["import-control-entry-declaration-outcome.1.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["SUBMIT", "import-control-entry-declaration-outcome.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  }
}
