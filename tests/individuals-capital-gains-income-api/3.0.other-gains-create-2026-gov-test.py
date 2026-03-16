{
  # Create 2026 Other canned response
  # $1 response sheet

  "press": [
    # No DYNAMIC gov-test-scenario
    ["EDIT", ["_$1_", "_parameters", "taxYear"], "2026-27"],

    ["CALL", "Choose Select", "_$1_", "_$1_"],
    ["DELETE", ["_$1_", "json", "_value", "cryptoassets", "0", "amountOfNetLoss"]],
    ["DELETE", ["_$1_", "json", "_value", "otherGains", "0", "amountOfNetLoss"]],
    ["EDIT", ["_$1_", "json", "_value", "cryptoassets", "0", "disposalDate"], "2026-05-05"],
    ["EDIT", ["_$1_", "json", "_value", "otherGains", "0", "disposalDate"], "2026-05-05"],
    ["EDIT", ["_$1_", "json", "_value", "unlistedShares", "0", "disposalDate"], "2026-05-05"],

    ["SUBMIT", "_$1_", "sheet-info._$0_"],
    ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],

    ["GOTO", "END"]
  ]
}
