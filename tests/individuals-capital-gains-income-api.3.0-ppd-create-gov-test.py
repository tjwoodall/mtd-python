{
  "description": "Create and Amend 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)",
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
    "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}_ppd-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["mtdit-user-0", "", "json", "nino"]],

      ["GOSUB", "CannedResponse.2025", "sheet._$0_"],
      ["GOSUB", "CannedResponse.2024", "sheet._$0_"],

      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["xGOSUB", "ErrorChecker", "sheet._$0_", "INVALID_DISPOSAL_DATE", "400", "RULE_DISPOSAL_DATE", "The disposalDate must be within the specified tax year"],
      ["xGOSUB", "ErrorChecker", "sheet._$0_", "INVALID_ACQUISITION_DATE", "400", "RULE_ACQUISITION_DATE", "The acquisitionDate must not be later than disposalDate"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "OUTSIDE_AMENDMENT_WINDOW", "400", "RULE_OUTSIDE_AMENDMENT_WINDOW", "You are outside the amendment window"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "REQUEST_CANNOT_BE_FULFILLED", "422", "RULE_REQUEST_CANNOT_BE_FULFILLED", "Custom (will vary in production depending on the actual error)"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse.2025": {
    "press": [
      ["EDIT", "_$1_", "", "_parameters", "taxYear", "2025-26"],
      ["EDIT", "_$1_", "", "json", "TY 2025-26 onwards-1"],
      ["DELETE", "_$1_", "", "json", "", "multiplePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["DELETE", "_$1_", "", "json", "", "singlePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["EDIT", "_$1_", "", "json", "", "singlePropertyDisposals", "0", "", "ppdSubmissionId", "Da2467289109"],

      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["GOTO", "END", ["sheet-info._$0_", "", "_control", "_response"], "204"]
    ]
  },

  "CannedResponse.2024": {
    "press": [
      ["EDIT", "_$1_", "", "_parameters", "taxYear", "2024-25"],
      ["EDIT", "_$1_", "", "json", "TY 2024-25 or before-0"],
      ["DELETE", "_$1_", "", "json", "", "multiplePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["DELETE", "_$1_", "", "json", "", "singlePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["EDIT", "_$1_", "", "json", "", "singlePropertyDisposals", "0", "", "ppdSubmissionId", "Da2467289109"],

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
