{
  "description": "Test individuals-other-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
              "tests/individuals-other-income-api/2.0.2025.py",
  ],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
      ["GOSUB", "Create or amend.2025", "mtdit-user-0"],
      ["GOSUB", "Delete", "mtdit-user-0", "2025-26"],
      ["GOTO", "END"]
    ]
  },
}
