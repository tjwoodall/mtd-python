{
  "description": "Test lisa-api request",
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
    "include": "tests/example/lisa-api.2.0._lifetime-isa_manager_{lisaManagerReferenceNumber}-get.example.py",
    "press": [
      ["GENSHEET", "lisa-api.2.0"],
      ["COPY", ["lisa-api.2.0", "", "_parameters", "lisaManagerReferenceNumber"], ["business-user-0", "", "json", "lisaManagerReferenceNumber"]],
      ["COPY", ["lisa-api.2.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "lisa-api.2.0", "", "_control", "_userId"],
      ["COPY", ["lisa-api.2.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "lisa-api.2.0", "", "_control", "_password"],
      ["COPY", ["lisa-api.2.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["SUBMIT", "lisa-api.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "lisaManagerReferenceNumber"], ["business-user-0", "", "json", "lisaManagerReferenceNumber"]],
      ["GOTO", "END"]
    ]
  }
}
