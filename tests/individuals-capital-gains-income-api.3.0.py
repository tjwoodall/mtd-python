{
  "description": "Test individuals-capital-gains-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
              "tests/individuals-capital-gains-income-api/3.0.NoPPD.2024.py",
              "tests/individuals-capital-gains-income-api/3.0.NoPPD.2025.py",
              "tests/individuals-capital-gains-income-api/3.0.NoPPD.2026.py",
              "tests/individuals-capital-gains-income-api/3.0.Other.2024.py",
              "tests/individuals-capital-gains-income-api/3.0.Other.2025.py",
              "tests/individuals-capital-gains-income-api/3.0.Other.2026.py",
              "tests/individuals-capital-gains-income-api/3.0.PPD.2024.py",
              "tests/individuals-capital-gains-income-api/3.0.PPD.2025.py"
  ],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
      ["GOSUB", "Create or amend NoPPD.2026", "mtdit-user-0"],
      ["GOSUB", "Delete NoPPD", "mtdit-user-0", "2026-27"],
      ["GOSUB", "Create or amend NoPPD.2025", "mtdit-user-0"],
      ["GOSUB", "Delete NoPPD", "mtdit-user-0", "2025-26"],
      ["GOSUB", "Create or amend NoPPD.2024", "mtdit-user-0"],
      ["GOSUB", "Delete NoPPD", "mtdit-user-0", "2024-25"],

      ["GOSUB", "Create or amend Other.2026", "mtdit-user-0"],
      ["GOSUB", "Delete Other", "mtdit-user-0", "2026-27"],
      ["GOSUB", "Create or amend Other.2025", "mtdit-user-0"],
      ["GOSUB", "Delete Other", "mtdit-user-0", "2025-26"],
      ["GOSUB", "Create or amend Other.2024", "mtdit-user-0"],
      ["GOSUB", "Delete Other", "mtdit-user-0", "2024-25"],

      # PPD cannot be submitted until the year has ended
      ["GOSUB", "Create or amend PPD.2025", "mtdit-user-0"],
      ["GOSUB", "Delete PPD", "mtdit-user-0", "2025-26"],
      ["GOSUB", "Create or amend PPD.2024", "mtdit-user-0"],
      ["GOSUB", "Delete PPD", "mtdit-user-0", "2024-25"],
      ["GOTO", "END"]
    ]
  }
}
