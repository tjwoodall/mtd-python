{
  "include": ["tests/include/create-mtdit-user.py", ],

  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],

    ["GOSUB", "run", "mtdit-user-0"],
    ["GOTO", "END"]
  ],

  "run": {
    # Delete a NonPPD gain
    # $1 user details

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-delete.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

# Get the canned responses
      ["GOSUB", "CannedResponse", "sheet._$0_", "2026-27"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2025-26"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2024-25"],

# Check the various Got-Test-Scenario
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Matching resource not found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "OUTSIDE_AMENDMENT_WINDOW", "400", "RULE_OUTSIDE_AMENDMENT_WINDOW", "You are outside the amendment window"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    # Retrieve NonPPD canned response
    # $1 response sheet
    # $2 tax-year

    "press": [
      # No DYNAMIC gov-test-scenario
      ["EDIT", "_$1_", "_parameters", "taxYear", "_$2_"],

      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["GOTO", "END", ["sheet-info._$0_", "_control", "_response"], "204"]
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
  },
}
