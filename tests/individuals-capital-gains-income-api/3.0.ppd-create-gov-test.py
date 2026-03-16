{
  "include": ["tests/include/create-mtdit-user.py",
              "tests/individuals-capital-gains-income-api/3.0.ppd-select.py",
  ],

  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],

    ["GOSUB", "run", "mtdit-user-0"],
    ["GOTO", "END"]
  ],

  "run": {
    # Create a PPD gain
    # $1 user details

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}_ppd-put.example.py" },
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
      ["GOSUB", "CannedResponse.2025", "sheet._$0_"],
      ["GOSUB", "CannedResponse.2024", "sheet._$0_"],

# Check the various Got-Test-Scenario
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "PPD_SUBMISSION_ID_NOT_FOUND", "404", "PPD_SUBMISSION_ID_NOT_FOUND", "Matching resource not found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "INCORRECT_DISPOSAL_TYPE", "400", "RULE_INCORRECT_DISPOSAL_TYPE", "A provided ppdSubmissionId is being used for the incorrect disposal type"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "OUTSIDE_AMENDMENT_WINDOW", "400", "RULE_OUTSIDE_AMENDMENT_WINDOW", "You are outside the amendment window"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "REQUEST_CANNOT_BE_FULFILLED", "422", "RULE_REQUEST_CANNOT_BE_FULFILLED", "Custom (will vary in production depending on the actual error)"],

      ["GOTO", "END"]
    ]
  },

  "CannedResponse.2025": { "include": "tests/individuals-capital-gains-income-api/3.0.ppd-create-2025-gov-test.py" },
  "CannedResponse.2024": { "include": "tests/individuals-capital-gains-income-api/3.0.ppd-create-2024-gov-test.py" },

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
