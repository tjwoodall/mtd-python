{
  "Choose Select": {
    # $1 - sheet to be checked for tax year
    # $2 - sheet to be updated based on tax year
    "press": [
      ["IF", "_Select 2026", ["_$1_", "_parameters", "taxYear"], "2027-28"],
      ["IF", "_Select 2026", ["_$1_", "_parameters", "taxYear"], "2026-27"],
      ["IF", "_Select 2025", ["_$1_", "_parameters", "taxYear"], "2025-26"],
      ["IF", "_Select 2024", ["_$1_", "_parameters", "taxYear"], "2024-25"],
      ["IF", "_Select 2024", ["_$1_", "_parameters", "taxYear"], "2023-24"],
      ["VALIDATE", ["_$1_", "_parameters", "taxYear"], "2022-23"],
      ["GOTO", "_Select 2024"],
    ]
  },

  "_Select 2026": {
    "press": [
      ["EDIT", ["_$2_", "json"], "TY 2026-27 onwards [Test Only]-2"],
      ["GOTO", "END"]
    ]
  },

  "_Select 2025": {
    "press": [
      ["EDIT", ["_$2_", "json"], "TY 2025-26-1"],
      ["GOTO", "END"]
    ]
  },

  "_Select 2024": {
    "press": [
      ["EDIT", ["_$2_", "json"], "TY 2024-25 or before-0"],
      ["GOTO", "END"]
    ]
  },
}
