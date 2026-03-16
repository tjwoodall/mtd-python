{
  "description": "Test vat-api request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdvat-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdvat user 0 on sheet mtdvat-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/vat-api.1.0._organisations_vat_{vrn}_information-get.example.py",
    "press": [
      ["GENSHEET", "vat-api.1.0"],
      ["COPY", ["vat-api.1.0", "", "_parameters", "vrn"], ["mtdvat-user-0", "", "json", "vrn"]],
      ["COPY", ["vat-api.1.0", "", "_control", "_username"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "vat-api.1.0", "", "_control", "_userId"],
      ["COPY", ["vat-api.1.0", "", "_control", "_userId"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "vat-api.1.0", "", "_control", "_password"],
      ["COPY", ["vat-api.1.0", "", "_control", "_password"], ["mtdvat-user-0", "", "json", "password"]],
      ["SUBMIT", "vat-api.1.0", "sheet-vat"],
      ["VALIDATE", ["sheet-vat", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-vat", "", "json", "customerDetails", "effectiveRegistrationDate"], "2018-03-04"],
      ["GOTO", "END"]
    ]
  }
}
