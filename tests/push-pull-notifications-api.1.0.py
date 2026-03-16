{
  "description": "Test push-pull-notifications-api request",
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
    "setup": { "include": "tests/example/push-pull-notifications-api.1.0._misc_push-pull-notification_box_{boxId}_notifications-get.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "push-pull-notifications-api.1.0"],
      ["DELETE", ["push-pull-notifications-api.1.0", "_parameters", "status"]],
      ["DELETE", ["push-pull-notifications-api.1.0", "_parameters", "fromDate"]],
      ["DELETE", ["push-pull-notifications-api.1.0", "_parameters", "toDate"]],
      ["DELETE", ["push-pull-notifications-api.1.0", "_parameters", "count"]],
      ["SUBMIT", "push-pull-notifications-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "_control", "_response"], "403"],
      ["VALIDATE", ["sheet-info", "json", "code"], "INVALID_SCOPE"],
      ["GOTO", "END"]
    ]
  }
}
