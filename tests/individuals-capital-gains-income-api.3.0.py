{
  "description": "Test individuals-capital-gains-income-api 3.0",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "Create or amend NoPPD.2024": {
    "include": "tests/individuals-capital-gains-income-api/3.0.NoPPD.2024.py",
  },

  "Create or amend NoPPD.2025": {
    "include": "tests/individuals-capital-gains-income-api/3.0.NoPPD.2025.py",
  },

  "Create or amend NoPPD.2026": {
    "include": "tests/individuals-capital-gains-income-api/3.0.NoPPD.2026.py",
  },

  "Create or amend Other.2024": {
    "include": "tests/individuals-capital-gains-income-api/3.0.Other.2024.py",
  },

  "Create or amend Other.2025": {
    "include": "tests/individuals-capital-gains-income-api/3.0.Other.2025.py",
  },

  "Create or amend Other.2026": {
    "include": "tests/individuals-capital-gains-income-api/3.0.Other.2026.py",
  },

  "Create or amend PPD.2024": {
    "include": "tests/individuals-capital-gains-income-api/3.0.PPD.2024.py",
  },

  "Create or amend PPD.2025": {
    "include": "tests/individuals-capital-gains-income-api/3.0.PPD.2025.py"
  },

  "Create and Amend CGT Residential Property Disposals (non-PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.nonppd-create-gov-test.py"
  },

  "Delete CGT Residential Property Disposals (non-PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.nonppd-delete-gov-test.py"
  },

  "Retrieve GT Residential Property Disposals (non-PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.nonppd-get-gov-test.py"
  },

  "Create and Amend Other Capital Gains and Disposals": {
    "include": "tests/individuals-capital-gains-income-api/3.0.other-gains-create-gov-test.py"
  },

  "Delete Other Capital Gains and Disposals": {
    "include": "tests/individuals-capital-gains-income-api/3.0.other-gains-delete-gov-test.py"
  },

  "Retrieve Other Capital Gains and Disposals": {
    "include": "tests/individuals-capital-gains-income-api/3.0.other-gains-get-gov-test.py"
  },

  "Create and Amend 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.ppd-create-gov-test.py"
  },

  "Delete 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.ppd-delete-gov-test.py"
  },

  "Retrieve 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)": {
    "include": "tests/individuals-capital-gains-income-api/3.0.ppd-get-gov-test.py"
  },

  "START": {
    "press": [
# Stateful tests
      ["CALL", "Create or amend NoPPD.2026", "mtdit-user-0"],
      ["CALL", "Create or amend NoPPD.2025", "mtdit-user-0"],
      ["CALL", "Create or amend NoPPD.2024", "mtdit-user-0"],

      ["CALL", "Create or amend Other.2026", "mtdit-user-0"],
      ["CALL", "Create or amend Other.2025", "mtdit-user-0"],
      ["CALL", "Create or amend Other.2024", "mtdit-user-0"],

      # PPD cannot be submitted until the year has ended
      ["CALL", "Create or amend PPD.2025", "mtdit-user-0"],
      ["CALL", "Create or amend PPD.2024", "mtdit-user-0"],

# gov-test canned responses
      ["CALL", "Create and Amend CGT Residential Property Disposals (non-PPD)"],
      ["CALL", "Delete CGT Residential Property Disposals (non-PPD)"],
      ["CALL", "Retrieve GT Residential Property Disposals (non-PPD)"],
      ["CALL", "Create and Amend Other Capital Gains and Disposals"],
      ["CALL", "Delete Other Capital Gains and Disposals"],
      ["CALL", "Retrieve Other Capital Gains and Disposals"],
      ["CALL", "Create and Amend 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)"],
      ["CALL", "Delete 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)"],
      ["CALL", "Retrieve 'Report and Pay Capital Gains Tax on Residential Property' Overrides (PPD)"],

      ["GOTO", "END"]
    ]
  },
}
