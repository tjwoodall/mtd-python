{
  "_Get agent": {
    # _$1_ - control sheet
    "press": [
      ["GOTO", "END"]
    ],
  },

  "_Get cached agent": {
    # $1 - user sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_agents-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get agent", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ],
    "cache": "artifacts/cache/_$1_.json"
  },

  "_Get nocache agent": {
    # $1 - user sheet
    # $2 - control sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_agents-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get agent", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ]
  },

  "Get test agent": {
    # $1 - user sheet
    "press": [
      ["CALL", "_Get cached agent", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  # Create a new user
  "Create a new test agent": {
    # $1: sheet to create user on
    "press": [
      ["CALL", "_Get nocache agent", "_$1_"],
      ["GOTO", "END"],
    ]
  },
}
