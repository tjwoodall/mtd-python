{
  "description": "Create and Amend Disclosures",
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
    "include": "tests/example/individuals-disclosures-api.2.0._individuals_disclosures_{nino}_{taxYear}-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],

      ["GOSUB", "CannedResponse", "sheet._$0_"],

      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "VOLUNTARY_CLASS2_CANNOT_BE_CHANGED", "400", "RULE_VOLUNTARY_CLASS2_CANNOT_BE_CHANGED", "Voluntary Class 2 NICs cannot be changed after 31st Jan following the year of submission"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Self-employment income source not found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "OUTSIDE_AMENDMENT_WINDOW", "400", "RULE_OUTSIDE_AMENDMENT_WINDOW", "You are outside the amendment window"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    "press": [
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["GOTO", "END", ["sheet-info._$0_", "", "_control", "_response"], "204"]
    ]
  },

  "ErrorChecker": {
    "press": [
      ["EDIT", "_$1_", "", "_parameters", "Gov-Test-Scenario", "_$2_"],
      ["SUBMIT", "_$1_", "response._$0_"],
      ["PRINT", "_$1_"],
      ["VALIDATE", ["response._$0_", "", "_control", "_response"], "_$3_"],
      ["VALIDATE", ["response._$0_", "", "json", "code"], "_$4_"],
      ["VALIDATE", ["response._$0_", "", "json", "message"], "_$5_"],
      ["GOTO", "END"]
    ]
  }
}
