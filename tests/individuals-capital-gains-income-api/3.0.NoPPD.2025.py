{
  "include": ["tests/include/create-mtdit-user.py",
              "tests/individuals-capital-gains-income-api/3.0.nonppd-select.py",
  ],

  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],

    ["GOSUB", "Create", "mtdit-user-0", "2025-26"],
    ["GOSUB", "Delete", "mtdit-user-0", "2025-26"],
    ["GOTO", "END"]
  ],

  "Create": {
    # Create a NoPPD gain (and confirm that we can read it back)
    # $1 user details
    # $2 tax-year

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-put.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "_$2_"],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["GOSUB", "Choose Select", "sheet._$0_", "sheet._$0_"],
      ["DELETE", "sheet._$0_", "json", "disposals", "0", "amountOfNetLoss"],
      ["EDIT", "sheet._$0_", "json", "disposals", "0", "disposalDate", "2025-04-10"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve", "validate._$0_", "_$1_", "_$2_"],
      ["VALIDATE", ["validate._$0_", "json"], ["sheet._$0_", "json"],
        "(d := next(iter(value.values())), d.update(d.pop('customerAddedDisposals')), d.pop('submittedOn'), value)[-1]"
      ],

      ["GOTO", "END"]
    ]
  },

  "Retrieve": {
    # Retrieve NoPPD gains
    # $1 response sheet
    # $2 user details
    # $3 tax-year

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-get.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$2_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$2_", "json", "nino"]],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "_$3_"],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["VALIDATE", ["_$1_", "_control", "_response"], "200"],
      ["GOSUB", "Choose Select", "sheet._$0_", "_$1_"],

      ["GOTO", "END"]
    ]
  },

  "Delete": {
    # Delete a NoPPD gain
    # $1 user details
    # $2 tax-year

    "setup": { "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-delete.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "_$2_"],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },
}
