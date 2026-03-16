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
    # Retrieve a PPD gain
    # $1 user details

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}_ppd-get.example.py" },
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
      ["GOSUB", "CannedResponse", "sheet._$0_", "2025-26", "hmrc-held"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2025-26", "user"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2025-26", "latest"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2024-25", "hmrc-held"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2024-25", "user"],
      ["GOSUB", "CannedResponse", "sheet._$0_", "2024-25", "latest"],

# Check the various Got-Test-Scenario
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Matching resource not found"],
      ["GOSUB", "ErrorChecker", "sheet._$0_", "REQUEST_CANNOT_BE_FULFILLED", "422", "RULE_REQUEST_CANNOT_BE_FULFILLED", "Custom (will vary in production depending on the actual error)"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    # Retrieve PPD canned response
    # $1 response sheet
    # $2 tax-year
    # $3 data source

    "press": [
      # No DYNAMIC gov-test-scenario
      ["EDIT", "_$1_", "_parameters", "taxYear", "_$2_"],
      ["EDIT", "_$1_", "_parameters", "source", "_$3_"],

      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],

      ["GOSUB", "Choose Select", "_$1_", "sheet-info._$0_"],

      ["GOTO", "END"]
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
