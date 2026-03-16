{
  "description": "Retrieve Income Tax (Self Assessment) Income and Expenditure Obligations",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
      ["GOTO", "run"]
    ]
  },

  "run": {
    "setup": { "include": "tests/example/obligations-api.3.0._obligations_details_{nino}_income-and-expenditure-get.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["mtdit-user-0", "json", "password"]],
      ["DELETE", "sheet._$0_", "_parameters", "typeOfBusiness"],
      ["DELETE", "sheet._$0_", "_parameters", "businessId"],
      ["DELETE", "sheet._$0_", "_parameters", "fromDate"],
      ["DELETE", "sheet._$0_", "_parameters", "toDate"],
      ["DELETE", "sheet._$0_", "_parameters", "status"],

      ["GOSUB", "CannedResponse", "sheet._$0_"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "DYNAMIC"],
      ["ADD", "sheet._$0_", "_parameters", "fromDate"],
      ["ADD", "sheet._$0_", "_parameters", "toDate"],

      ["GOSUB", "DYNAMIC-2024-25", "sheet._$0_"], # Non-cumulative for 2024 and before
      ["GOSUB", "DYNAMIC-2025-26", "sheet._$0_"],
      ["GOSUB", "DYNAMIC-2026-27", "sheet._$0_"],

      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Matching resource not found"],

      ["GOTO", "END"]
    ]
  },

  "DYNAMIC-2024-25": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "fromDate", "2024-04-06"],
      ["EDIT", "_$1_", "_parameters", "toDate", "2025-04-05"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["PRINT", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  },

  "DYNAMIC-2025-26": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "fromDate", "2025-04-06"],
      ["EDIT", "_$1_", "_parameters", "toDate", "2026-04-05"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["PRINT", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  },

  "DYNAMIC-2026-27": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "fromDate", "2026-04-06"],
      ["EDIT", "_$1_", "_parameters", "toDate", "2027-04-05"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["PRINT", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    "press": [
      ["Note: No DYNAMIC gov-test-scenario"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["PRINT", "sheet-info._$0_"],
      ["GOTO", "END", ["sheet-info._$0_", "_control", "_response"], "200"]
    ]
  },

  "ErrorChecker": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "Gov-Test-Scenario", "_$2_"],
      ["SUBMIT", "_$1_", "response._$0_"],
      ["VALIDATE", ["response._$0_", "_control", "_response"], "_$3_"],
      ["VALIDATE", ["response._$0_", "json", "code"], "_$4_"],
      ["VALIDATE", ["response._$0_", "json", "message"], "_$5_"],
      ["GOTO", "END"]
    ]
  }
}
