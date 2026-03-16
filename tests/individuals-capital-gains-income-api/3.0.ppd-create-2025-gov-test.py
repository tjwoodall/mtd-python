{
  # Create 2025 PPD canned response
  # $1 response sheet

  "press": [
    # No DYNAMIC gov-test-scenario
    ["EDIT", "_$1_", "_parameters", "taxYear", "2025-26"],

    ["GOSUB", "Choose Select", "_$1_", "_$1_"],
    ["DELETE", "_$1_", "json", "multiplePropertyDisposals", "0", "amountOfNetLoss"],
    ["DELETE", "_$1_", "json", "singlePropertyDisposals", "0", "amountOfNetLoss"],
    ["EDIT", "_$1_", "json", "singlePropertyDisposals", "0", "ppdSubmissionId", "Da2467289109"],

    ["SUBMIT", "_$1_", "sheet-info._$0_"],
    ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],

    ["GOTO", "END"]
  ]
}
