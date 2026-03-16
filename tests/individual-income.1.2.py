{
  "description": "Test individual-income request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-sa-user.py"],

  "START": {
    "press": [
      ["CALL", "Get test sa user", "sa-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "setup": { "include": "tests/example/paye-des-stub.2.0._individual-paye-test-support_sa_{utr}_income_annual-summary_{taxYear}-post.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "setup-benefits.2.0"],
      ["COPY", ["setup-benefits.2.0", "_parameters", "utr"], ["sa-user-0", "json", "saUtr"]],
      ["EDIT", ["setup-benefits.2.0", "_parameters", "taxYear"], "2026-27"],
      ["EDIT", ["setup-benefits.2.0", "json", "scenario"], "HAPPY_PATH_2"],
      ["SUBMIT", "setup-benefits.2.0", "create-benefit"],
      ["VALIDATE", ["create-benefit", "_control", "_response"], "201"],
      ["GOTO", "setup 2"]
    ]
  },

  "setup 2": {
    "setup": { "include": "tests/example/individual-income.1.2._individual-income_sa_{utr}_annual-summary_{taxYear}-get.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "individual-income.1.2"],
      ["COPY", ["individual-income.1.2", "_parameters", "utr"], ["sa-user-0", "json", "saUtr"]],
      ["COPY", ["individual-income.1.2", "_control", "_username"], ["sa-user-0", "json", "userId"]],
      ["ADD", ["individual-income.1.2", "_control", "_userId"]],
      ["COPY", ["individual-income.1.2", "_control", "_userId"], ["sa-user-0", "json", "userId"]],
      ["ADD", ["individual-income.1.2", "_control", "_password"]],
      ["COPY", ["individual-income.1.2", "_control", "_password"], ["sa-user-0", "json", "password"]],
      ["EDIT", ["individual-income.1.2", "_parameters", "taxYear"], "2026-27"],
      ["SUBMIT", "individual-income.1.2", "sheet-info"],
      ["VALIDATE", ["sheet-info", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "json", "employments", "0", "employerPayeReference"], "123/AB456"],
      ["GOTO", "END"]
    ]
  }
}
