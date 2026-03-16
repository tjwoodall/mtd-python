{
  "description": "Test national-insurance request",
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
    "include": "tests/example/national-insurance-des-stub.1.0._national-insurance-test-support_sa_{utr}_annual-summary_{taxYear}-post.example.py",
    "press": [
      ["GENSHEET", "setup-national-insurance.1.0"],
      ["COPY", ["setup-national-insurance.1.0", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["EDIT", "setup-national-insurance.1.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "setup-national-insurance.1.0", "", "json", "scenario", "HAPPY_PATH_1"],
      ["SUBMIT", "setup-national-insurance.1.0", "create-national-insurance"],
      ["GOTO", "setup 2", ["create-national-insurance", "", "_control", "_response"], "201"]
    ]
  },

  "setup 2": {
    "include": "tests/example/national-insurance.1.1._national-insurance_sa_{utr}_annual-summary_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "national-insurance.1.1"],
      ["COPY", ["national-insurance.1.1", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["COPY", ["national-insurance.1.1", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "national-insurance.1.1", "", "_control", "_userId"],
      ["COPY", ["national-insurance.1.1", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "national-insurance.1.1", "", "_control", "_password"],
      ["COPY", ["national-insurance.1.1", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["EDIT", "national-insurance.1.1", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "national-insurance.1.1", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "class2", "totalDue"], 20.0],
      ["GOTO", "END"]
    ]
  }
}
