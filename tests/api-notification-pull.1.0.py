{
  "description": "Test api-notification-pull request",
  "schema": "artifacts/application.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-business-user.py"],

  "START": {
    "press": [
      ["CALL", "Get test business user", "business-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "setup": { "include": "tests/example/api-notification-pull.1.0._notifications_unpulled-get.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "api-notification-pull.1.0"],
      ["SUBMIT", "api-notification-pull.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info", "xml", "resource", "@href"], "/notifications/unpulled/"],
      ["GOTO", "END"]
    ]
  }
}
