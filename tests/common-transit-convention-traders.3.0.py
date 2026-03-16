{
  "description": "Test common-transit-convention-traders request",
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
    "include": "tests/example/common-transit-convention-traders.3.0._customs_transits_movements_arrivals-get.example.py",
    "press": [
      ["GENSHEET", "common-transit-convention-traders.3.0"],
      ["COPY", ["common-transit-convention-traders.3.0", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "common-transit-convention-traders.3.0", "", "_control", "_userId"],
      ["COPY", ["common-transit-convention-traders.3.0", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "common-transit-convention-traders.3.0", "", "_control", "_password"],
      ["COPY", ["common-transit-convention-traders.3.0", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "updatedSince"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "movementEORI"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "movementReferenceNumber"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "localReferenceNumber"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "page"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "count"],
      ["DELETE", "common-transit-convention-traders.3.0", "", "_parameters", "receivedUntil"],
      ["SUBMIT", "common-transit-convention-traders.3.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json", "totalCount"], 0.0],
      ["GOTO", "END"]
    ]
  }
}
