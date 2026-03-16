{
  "description": "Test vat-api request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "GetVatPenalties": {
    "include": "tests/vat-api/1.0.GetVatPenalties-gov-test.py",
  },

  "START": {
    "press": [
      ["CALL", "GetVatPenalties", "mtdvat-user-0"],
      ["GOTO", "END"]
    ]
  },
}
