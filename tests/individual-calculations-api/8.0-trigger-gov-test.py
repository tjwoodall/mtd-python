{
  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
    ["GOTO", "run"]
  ],

  "run": {
    "setup": { "include": "tests/example/individual-calculations-api.8.0._individuals_calculations_{nino}_self-assessment_{taxYear}_trigger_{calculationType}-post.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["mtdit-user-0", "json", "password"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2025-26"],
      ["GOSUB", "CannedResponse", "sheet._$0_"],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2025"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_TAX_YEAR", "The provided tax year format is invalid"],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2023-24"],

      ["EDIT", "sheet._$0_", "_parameters", "nino", "ANINO"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_NINO", "The NINO format is invalid"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "calculationType", "ACalculationType"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_CALCULATION_TYPE", "The provided calculation type is not valid"],
      ["EDIT", "sheet._$0_", "_parameters", "calculationType", "intent-to-finalise"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],

      ["GOSUB", "ErrorChecker", "sheet._$0_", "NO_INCOME_SUBMISSIONS_EXIST", "400", "RULE_NO_INCOME_SUBMISSIONS_EXIST", "No income submissions exist for the tax year"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "FINAL_DECLARATION_RECEIVED", "400", "RULE_FINAL_DECLARATION_RECEIVED", "Final declaration has already been received"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "INCOME_SOURCES_CHANGED", "400", "RULE_INCOME_SOURCES_CHANGED", "Income sources data has changed. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "RECENT_SUBMISSIONS_EXIST", "400", "RULE_RECENT_SUBMISSIONS_EXIST", "More recent submissions exist. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "RESIDENCY_CHANGED", "400", "RULE_RESIDENCY_CHANGED", "Residency has changed. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "CALCULATION_IN_PROGRESS", "400", "RULE_CALCULATION_IN_PROGRESS", "A calculation is in progress. Please wait before triggering a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "BUSINESS_VALIDATION_FAILURE", "400", "RULE_BUSINESS_VALIDATION_FAILURE", "Business validation rule failures"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "TAX_YEAR_NOT_ENDED", "400", "RULE_TAX_YEAR_NOT_ENDED", "The specified tax year has not yet ended"],

      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "_$1_", "_parameters", "calculationType", "intent-to-finalise"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "202"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculationId"], "c75dbb53-6237-49e2-b05a-60ef221f0260"],
      ["GOTO", "END"]
    ]
  },

  "ErrorChecker": {
    "press": [
      ["EDIT", "_$1_", "_parameters", "Gov-Test-Scenario", "_$2_"],
      ["GOTO", "ErrorChecker2"]
    ]
  },

  "ErrorChecker2": {
    "press": [
      ["SUBMIT", "_$1_", "response._$0_"],
      ["VALIDATE", ["response._$0_", "_control", "_response"], "_$3_"],
      ["VALIDATE", ["response._$0_", "json", "code"], "_$4_"],
      ["VALIDATE", ["response._$0_", "json", "message"], "_$5_"],
      ["GOTO", "END"]
    ]
  }
}
