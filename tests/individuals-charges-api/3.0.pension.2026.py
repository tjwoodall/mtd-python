{
  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
    ["GOSUB", "Create or amend", "mtdit-user-0"],
    ["GOSUB", "Retrieve", "mtdit-user-0"],
    ["GOSUB", "Delete", "mtdit-user-0"],
    ["GOTO", "END"],
  ],

  "Create or amend": {
    "setup": { "include": "tests/example/individuals-charges-api.3.0._individuals_charges_pensions_{nino}_{taxYear}-put.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "sheet._$0_", "json", "Tax years 2024-25 onwards-1"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },

  "Retrieve": {
    "setup": { "include": "tests/example/individuals-charges-api.3.0._individuals_charges_pensions_{nino}_{taxYear}-get.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  },

  "Delete": {
    "setup": { "include": "tests/example/individuals-charges-api.3.0._individuals_charges_pensions_{nino}_{taxYear}-delete.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  }
}
