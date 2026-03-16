{
  "Create or amend NoPPD.2026": {
    "note": "1: user details",
    "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-put.example.py",
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

      ["GOSUB", "Choose NoPPD Select", "sheet._$0_", "sheet._$0_"],
      ["DELETE", "sheet._$0_", "", "json", "", "disposals", "0", "", "amountOfNetLoss"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve NoPPD", "validate._$0_", "_$1_", "2026-27"],
      ["VALIDATE", ["sheet-info.validate._$0_", "", "json"], ["sheet._$0_", "", "json"],
        "(d := next(iter(value.values())), d.update(d.pop('customerAddedDisposals')), d.pop('submittedOn'), value)[-1]"
      ],
      ["GOTO", "END"]
    ]
  },

  "Retrieve NoPPD": {
    "note": "1: uuid for sheet/sheet-info, 2: user details, 3: tax-year",
    "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-get.example.py",
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
      ["GOSUB", "Choose NoPPD Select", "sheet._$1_", "sheet-info._$1_"],
      ["GOTO", "END"]
    ]
  },

  "Delete NoPPD": {
    "note": "1: user details, 2: tax-year",
    "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}-delete.example.py",
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

  "Choose NoPPD Select": {
    # $1 - sheet to be checked for tax year
    # $2 - sheet to be updated based on tax year
    "press": [
      ["GOTO", "_Select NoPPD 2026", ["_$1_", "", "_parameters", "taxYear"], "2027-28"],
      ["GOTO", "_Select NoPPD 2026", ["_$1_", "", "_parameters", "taxYear"], "2026-27"],
      ["GOTO", "_Select NoPPD 2025", ["_$1_", "", "_parameters", "taxYear"], "2025-26"],
      ["GOTO", "_Select NoPPD 2024", ["_$1_", "", "_parameters", "taxYear"], "2024-25"],
      ["GOTO", "_Select NoPPD 2024", ["_$1_", "", "_parameters", "taxYear"], "2023-24"],
      ["GOTO", "_Select NoPPD 2024", ["_$1_", "", "_parameters", "taxYear"], "2022-23"],
    ]
  },

  "_Select NoPPD 2026": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2026-27 onwards [Test Only]-2"],
      ["GOTO", "END"]
    ]
  },

  "_Select NoPPD 2025": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2025-26 -1"],
      ["GOTO", "END"]
    ]
  },

  "_Select NoPPD 2024": {
    "press": [
      ["EDIT", "_$2_", "", "json", "TY 2024-25 or before-0"],
      ["GOTO", "END"]
    ]
  },
}
