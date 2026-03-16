{
  "Create or amend.2026": {
    "note": "1: user details",
    "include": "tests/example/individuals-other-income-api.3.0._individuals_other-income_{nino}_{taxYear}-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],

      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["GOSUB", "Choose Select", "sheet._$0_", "sheet._$0_"],
      ["DELETE", "sheet._$0_", "", "json", "", "postCessationReceipts"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve", "validate._$0_", "_$1_", "2026-27"],
      ["VALIDATE", ["sheet-info.validate._$0_", "", "json"], ["sheet._$0_", "", "json"],
        "(d := next(iter(value.values())), d.pop('submittedOn'), k := next(iter(expected)), value.update({k: value.pop(next(iter(value)))}), value)[-1]"
      ],
      ["GOTO", "END"]
    ]
  },

  "Retrieve": {
    "note": "1: uuid for sheet/sheet-info, 2: user details, 3: tax-year",
    "include": "tests/example/individuals-other-income-api.3.0._individuals_other-income_{nino}_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "sheet._$1_"],
      ["COPY", ["sheet._$1_", "", "_control", "_username"], ["_$2_", "", "json", "userId"]],
      ["ADD", "sheet._$1_", "", "_control", "_userId"],
      ["COPY", ["sheet._$1_", "", "_control", "_userId"], ["_$2_", "", "json", "userId"]],
      ["ADD", "sheet._$1_", "", "_control", "_password"],
      ["COPY", ["sheet._$1_", "", "_control", "_password"], ["_$2_", "", "json", "password"]],

      ["COPY", ["sheet._$1_", "", "_parameters", "nino"], ["_$2_", "", "json", "nino"]],
      ["EDIT", "sheet._$1_", "", "_parameters", "taxYear", "_$3_"],
      ["ADD", "sheet._$1_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$1_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$1_", "sheet-info._$1_"],
      ["VALIDATE", ["sheet-info._$1_", "", "_control", "_response"], "200"],
      ["GOSUB", "Choose Retrieve Select", "sheet._$1_", "sheet-info._$1_"],
      ["GOTO", "END"]
    ]
  },

  "Delete": {
    "note": "1: user details, 2: tax-year",
    "include": "tests/example/individuals-other-income-api.3.0._individuals_other-income_{nino}_{taxYear}-delete.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],
      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "_$2_"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },

  "Choose Retrieve Select": {
    # $1 - sheet to be checked for tax year
    # $2 - sheet to be updated based on tax year
    "press": [
      ["GOTO", "_Retrieve Select 2026", ["_$1_", "", "_parameters", "taxYear"], "2027-28"],
      ["GOTO", "_Retrieve Select 2026", ["_$1_", "", "_parameters", "taxYear"], "2026-27"],
      ["GOTO", "_Retrieve Select 2025", ["_$1_", "", "_parameters", "taxYear"], "2025-26"],
      ["GOTO", "_Retrieve Select 2025", ["_$1_", "", "_parameters", "taxYear"], "2024-25"],
      ["GOTO", "_Retrieve Select 2025", ["_$1_", "", "_parameters", "taxYear"], "2023-24"],
      ["GOTO", "_Retrieve Select 2022", ["_$1_", "", "_parameters", "taxYear"], "2022-23"],
    ]
  },

  "_Retrieve Select 2026": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2026-27 onwards-2"],
      ["GOTO", "END"]
    ]
  },

  "_Retrieve Select 2025": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2023-24 to TY 2025-26-1"],
      ["GOTO", "END"]
    ]
  },

  "_Retrieve Select 2022": {
    "press": [
      ["EDIT", "_$2_", "", "json", "Before TY 2023-24-0"],
      ["GOTO", "END"]
    ]
  },

  "Choose Select": {
    # $1 - sheet to be checked for tax year
    # $2 - sheet to be updated based on tax year
    "press": [
      ["GOTO", "_Select 2026", ["_$1_", "", "_parameters", "taxYear"], "2027-28"],
      ["GOTO", "_Select 2026", ["_$1_", "", "_parameters", "taxYear"], "2026-27"],
      ["GOTO", "_Select 2025", ["_$1_", "", "_parameters", "taxYear"], "2025-26"],
    ]
  },

  "_Select 2026": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2026-27 onwards-1"],
      ["GOTO", "END"]
    ]
  },

  "_Select 2025": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2025-26-0"],
      ["GOTO", "END"]
    ]
  },
}
