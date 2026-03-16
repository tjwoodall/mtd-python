{
  "include": ["tests/include/create-mtdit-user.py", ],

  "press": [
    ["GOSUB", "Get test mtdit user se and property on sheet mtdit-user-both"],
    ["GOSUB", "_Get list of businesses", "mtdit-user-both", "list businesses._$0_" ],

    ["GOSUB", "Create", "mtdit-user-both", "2026-27", "list businesses._$0_"],
    ["GOSUB", "Delete", "mtdit-user-both", "2026-27", "list businesses._$0_"],
    ["GOTO", "END"]
  ],

  "Create": {
    # Create a loss (and confirm that we can read it back)
    # $1 user details
    # $2 tax-year
    # $3 business details

    "setup": { "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-put.example.py" },
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
      ["COPY", ["sheet._$0_", "_parameters", "businessId"], ["_$3_", "json", "listOfBusinesses", "0", "businessId"]],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["DELETE", "sheet._$0_", "json", "claims", "carryBack", "terminalLosses"],
      ["EDIT", "sheet._$0_", "json", "claims", "preferenceOrder", "applyFirst", "carry-back"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve", "validate._$0_", "_$1_", "_$2_", "_$3_"],
      ["PRINT", "_$1_"],
      ["VALIDATE", ["validate._$0_", "json"], ["sheet._$0_", "json"],
        "(d := next(iter(value.values())), d.pop('submittedOn'), value)[-1]"
      ],

      ["GOTO", "END"]
    ]
  },

  "Retrieve": {
    # Retrieve a loss
    # $1 response sheet
    # $2 user details
    # $3 tax-year
    # $4 business details

    "setup": { "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-get.example.py" },
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
      ["COPY", ["sheet._$0_", "_parameters", "businessId"], ["_$4_", "json", "listOfBusinesses", "0", "businessId"]],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["VALIDATE", ["_$1_", "_control", "_response"], "200"],

      ["GOTO", "END"]
    ]
  },

  "Delete": {
    # Delete a loss
    # $1 user details
    # $2 tax-year
    # $3 business details

    "setup": { "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-delete.example.py" },
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
      ["COPY", ["sheet._$0_", "_parameters", "businessId"], ["_$3_", "json", "listOfBusinesses", "0", "businessId"]],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },
}
