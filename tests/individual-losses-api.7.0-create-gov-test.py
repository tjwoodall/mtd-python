{
  "description": "Create or Amend Losses and Claims",
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
    "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],
      ["EDIT", "sheet._$0_", "", "_parameters", "businessId", "XAIS12345678910"],
      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],
      ["DELETE", "sheet._$0_", "", "json", "claims", "carryBack", "terminalLosses"],

      ["GOSUB", "CannedResponse", "sheet._$0_"],

      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Matching resource not found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "CARRY_BACK_CLAIM", "400", "RULE_CARRY_BACK_CLAIM", "Carry back claim type is not valid for property income sources"],
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
      ["VALIDATE", ["response._$0_", "", "_control", "_response"], "_$3_"],
      ["VALIDATE", ["response._$0_", "", "json", "code"], "_$4_"],
      ["VALIDATE", ["response._$0_", "", "json", "message"], "_$5_"],
      ["GOTO", "END"]
    ]
  }
}
