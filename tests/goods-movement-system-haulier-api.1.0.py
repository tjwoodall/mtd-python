{
  "description": "Test goods-movement-system-haulier-api request",
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
    "include": "tests/example/goods-movement-system-haulier-api.1.0._customs_goods-movement-system_movements-get.example.py",
    "press": [
      ["GENSHEET", "goods-movement-system-haulier-api.1.0"],
      ["COPY", ["goods-movement-system-haulier-api.1.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "goods-movement-system-haulier-api.1.0", "", "_control", "_userId"],
      ["COPY", ["goods-movement-system-haulier-api.1.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "goods-movement-system-haulier-api.1.0", "", "_control", "_password"],
      ["COPY", ["goods-movement-system-haulier-api.1.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["SUBMIT", "goods-movement-system-haulier-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  }
}
