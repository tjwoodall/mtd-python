{
  "description": "Test individual-benefits request",
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
    "include": "tests/example/paye-des-stub.2.0._individual-paye-test-support_sa_{utr}_benefits_annual-summary_{taxYear}-post.example.py",
    "press": [
      ["GENSHEET", "setup-benefits.2.0"],
      ["COPY", ["setup-benefits.2.0", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["EDIT", "setup-benefits.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "setup-benefits.2.0", "", "json", "scenario", "HAPPY_PATH_1"],
      ["SUBMIT", "setup-benefits.2.0", "create-benefit"],
      ["GOTO", "setup 2", ["create-benefit", "", "_control", "_response"], "201"]
    ]
  },

  "setup 2": {
    "include": "tests/example/individual-benefits.2.0._individual-benefits_sa_{utr}_annual-summary_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individual-benefits.2.0"],
      ["COPY", ["individual-benefits.2.0", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["COPY", ["individual-benefits.2.0", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "individual-benefits.2.0", "", "_control", "_userId"],
      ["COPY", ["individual-benefits.2.0", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "individual-benefits.2.0", "", "_control", "_password"],
      ["COPY", ["individual-benefits.2.0", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["EDIT", "individual-benefits.2.0", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individual-benefits.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "employments", "0", "", "companyCarsAndVansBenefit"], 44.0],
      ["GOTO", "END"]
    ]
  }
}
