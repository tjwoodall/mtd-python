{
  "description": "Test excise-movement-control-system-api request",
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
    "include": "tests/example/excise-movement-control-system-api.1.0._customs_excise_movements-get.example.py",
    "press": [
      ["GENSHEET", "excise-movement-control-system-api.1.0"],
      ["COPY", ["excise-movement-control-system-api.1.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "excise-movement-control-system-api.1.0", "", "_control", "_userId"],
      ["COPY", ["excise-movement-control-system-api.1.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "excise-movement-control-system-api.1.0", "", "_control", "_password"],
      ["COPY", ["excise-movement-control-system-api.1.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["DELETE", "excise-movement-control-system-api.1.0", "", "_parameters", "ern"],
      ["DELETE", "excise-movement-control-system-api.1.0", "", "_parameters", "arc"],
      ["DELETE", "excise-movement-control-system-api.1.0", "", "_parameters", "lrn"],
      ["DELETE", "excise-movement-control-system-api.1.0", "", "_parameters", "updatedSince"],
      ["DELETE", "excise-movement-control-system-api.1.0", "", "_parameters", "traderType"],
      ["SUBMIT", "excise-movement-control-system-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "", "json"], 0],
      ["GOTO", "END"]
    ]
  }
}
