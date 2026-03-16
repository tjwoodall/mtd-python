{
  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
    ["GOTO", "run"]
  ],

  "run": {
    "setup": { "include": "tests/example/individual-calculations-api.8.0._individuals_calculations_{nino}_self-assessment_{taxYear}_{calculationId}_{calculationType}-post.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["mtdit-user-0", "json", "password"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2023-24"],
      ["GOSUB", "CannedResponse", "sheet._$0_"],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2025"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_TAX_YEAR", "The provided tax year format is invalid"],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2023-24"],

      ["EDIT", "sheet._$0_", "_parameters", "nino", "ANINO"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_NINO", "The NINO format is invalid"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "calculationType", "ACalculationType"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_CALCULATION_TYPE", "The provided calculation type is not valid"],
      ["EDIT", "sheet._$0_", "_parameters", "calculationType", "final-declaration"],

      ["EDIT", "sheet._$0_", "_parameters", "calculationId", "f2fb30e5-4ab6-4a29-b3c1-c7264259ff1Z"],
      ["GOSUB", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_CALCULATION_ID", "The provided calculation ID is invalid"],
      ["EDIT", "sheet._$0_", "_parameters", "calculationId", "f2fb30e5-4ab6-4a29-b3c1-c7264259ff1c"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],

      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "The calculation ID was not found or does not correspond to the most recent calculation"],

      ["note: this requires the tax year to be set to at least 2025-26 or it gets rejected"],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2025-26"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "OUTSIDE_AMENDMENT_WINDOW", "400", "RULE_OUTSIDE_AMENDMENT_WINDOW", "You are outside the amendment window"],

      ["GOSUB", "ErrorChecker", "sheet._$0_", "FINAL_DECLARATION_IN_PROGRESS", "400", "RULE_FINAL_DECLARATION_IN_PROGRESS", "There is a calculation in progress for the tax year"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "FINAL_DECLARATION_RECEIVED", "400", "RULE_FINAL_DECLARATION_RECEIVED", "Final declaration has already been received"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "FINAL_DECLARATION_TAX_YEAR", "400", "RULE_FINAL_DECLARATION_TAX_YEAR", "Final declaration cannot be submitted until after the end of the tax year"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "INCOME_SOURCES_CHANGED", "400", "RULE_INCOME_SOURCES_CHANGED", "Income sources data has changed. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "INCOME_SOURCES_INVALID", "400", "RULE_INCOME_SOURCES_INVALID", "No valid income sources could be found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "NO_INCOME_SUBMISSIONS_EXIST", "400", "RULE_NO_INCOME_SUBMISSIONS_EXIST", "No income submissions exist for the tax year"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "RECENT_SUBMISSIONS_EXIST", "400", "RULE_RECENT_SUBMISSIONS_EXIST", "More recent submissions exist. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "RESIDENCY_CHANGED", "400", "RULE_RESIDENCY_CHANGED", "Residency has changed. Trigger a new calculation"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "SUBMISSION_FAILED", "400", "RULE_SUBMISSION_FAILED", "The submission cannot be completed due to validation failures"],

      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    "press": [
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
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
