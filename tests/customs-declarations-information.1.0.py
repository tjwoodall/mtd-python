{
  "description": "Test customs-declarations-information request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-sa-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test sa user 0 on sheet sa-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/customs-declarations-information.1.0._customs_declarations-information_ducr_{ducr}_status-get.example.py",
    "press": [
      ["GENSHEET", "customs-declarations-information.1.0"],
      ["COPY", ["customs-declarations-information.1.0", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "customs-declarations-information.1.0", "", "_control", "_userId"],
      ["COPY", ["customs-declarations-information.1.0", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "customs-declarations-information.1.0", "", "_control", "_password"],
      ["COPY", ["customs-declarations-information.1.0", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["SUBMIT", "customs-declarations-information.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "404"],
      ["VALIDATE", ["sheet-info", "", "xml", "", "errorResponse", "code"], "CDS60001"],
      ["GOTO", "END"]
    ]
  }
}
