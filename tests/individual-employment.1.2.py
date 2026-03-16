{
  "description": "Test individual-employment request",
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
    "include": "tests/example/paye-des-stub.2.0._individual-paye-test-support_sa_{utr}_employments_annual-summary_{taxYear}-post.example.py",
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
    "include": "tests/example/individual-employment.1.2._individual-employment_sa_{utr}_annual-summary_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "individual-employment.1.2"],
      ["COPY", ["individual-employment.1.2", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["COPY", ["individual-employment.1.2", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "individual-employment.1.2", "", "_control", "_userId"],
      ["COPY", ["individual-employment.1.2", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "individual-employment.1.2", "", "_control", "_password"],
      ["COPY", ["individual-employment.1.2", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["EDIT", "individual-employment.1.2", "", "_parameters", "taxYear", "2026-27"],
      ["SUBMIT", "individual-employment.1.2", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "employments", "0", "", "employerPayeReference"], "123/AB456"],
      ["GOTO", "END"]
    ]
  }
}
