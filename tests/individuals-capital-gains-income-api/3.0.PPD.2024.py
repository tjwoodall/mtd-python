{
  "Create or amend PPD.2024": {
    "note": "1: user details",
    "include": "tests/example/individuals-capital-gains-income-api.3.0._individuals_disposals-income_residential-property_{nino}_{taxYear}_ppd-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],

      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2024-25"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["GOSUB", "Choose PPD Select", "sheet._$0_", "sheet._$0_"],
      ["DELETE", "sheet._$0_", "", "json", "", "multiplePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["DELETE", "sheet._$0_", "", "json", "", "singlePropertyDisposals", "0", "", "amountOfNetLoss"],
      ["EDIT", "sheet._$0_", "", "json", "", "singlePropertyDisposals", "0", "", "ppdSubmissionId", "Da2467289109"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve PPD", "validate._$0_", "_$1_", "2024-25"],
      ["VALIDATE", ["sheet-info.validate._$0_", "", "json"], ["sheet._$0_", "", "json"],
        "(d := next(iter(value.values())), d['multiplePropertyDisposals'][0].pop('source'), d['singlePropertyDisposals'][0].pop('source'), value)[-1]"
      ],

      ["GOTO", "END"]
    ]
  },
}
