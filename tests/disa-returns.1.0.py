{
  "description": "Test disa-returns request",
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
    "xinclude": "tests/example/disa-returns.1.0._monthly_{zReference}_{taxYear}_{month}-post.example.py",
    "include": "tests/example/disa-returns.1.0._monthly_{zReference}-post.example.py",
    "press": [
      ["GENSHEET", "disa-returns.1.0"],
      ["COPY", ["disa-returns.1.0", "", "_parameters", "zReference"], ["business-user-0", "", "json", "zReference"]],
      ["EDIT", "disa-returns.1.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "disa-returns.1.0", "", "_parameters", "month", "APR"],
      ["COPY", ["disa-returns.1.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "disa-returns.1.0", "", "_control", "_userId"],
      ["COPY", ["disa-returns.1.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "disa-returns.1.0", "", "_control", "_password"],
      ["COPY", ["disa-returns.1.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["ADD", "disa-returns.1.0", "", "ndjson", "0"],
      ["ADD", "disa-returns.1.0", "", "ndjson", "1"],
      ["ADD", "disa-returns.1.0", "", "ndjson", "2"],
      ["ADD", "disa-returns.1.0", "", "ndjson", "3"],
      ["EDIT", "disa-returns.1.0", "", "ndjson", "0", "", "Lifetime ISA - Subscription-0"],
      ["EDIT", "disa-returns.1.0", "", "ndjson", "1", "", "Lifetime ISA - Closure-1"],
      ["EDIT", "disa-returns.1.0", "", "ndjson", "2", "", "Standard ISA - Subscription-2"],
      ["EDIT", "disa-returns.1.0", "", "ndjson", "3", "", "Standard ISA - Closure-3"],
      ["SUBMIT", "disa-returns.1.0", "sheet-info"],
      ["xVALIDATE", ["sheet-info", "", "_control", "_response"], "403"],
      ["xVALIDATE", ["sheet-info", "", "json", "code"], "RESOURCE_FORBIDDEN"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "404"],
      ["VALIDATE", ["sheet-info", "", "json", "code"], "MATCHING_RESOURCE_NOT_FOUND"],
      ["GOTO", "END"]
    ]
  }
}
