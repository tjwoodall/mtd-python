{
  "_Get mtdvat user": {
    # _$1_ - control sheet
    "press": [
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "mtd-vat"],
      ["DELETE", ["_$1_", "json", "eoriNumber"]],
      ["DELETE", ["_$1_", "json", "exciseNumber"]],
      ["DELETE", ["_$1_", "json", "nino"]],
      ["DELETE", ["_$1_", "json", "taxPayerType"]],
      ["DELETE", ["_$1_", "json", "pillar2Id"]],
      ["DELETE", ["_$1_", "json", "zReference"]],
      ["GOTO", "END"]
    ],
  },

  "_Get cached mtdvat user": {
    # $1 - user sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_organisations-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get mtdvat user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ],
    "cache": "artifacts/cache/_$1_.json"
  },

  "_Get nocache mtdvat user": {
    # $1 - user sheet
    # $2 - control sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_organisations-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get mtdvat user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ]
  },

  "Get test mtdvat user": {
    # $1 - user sheet
    "press": [
      ["CALL", "_Get cached mtdvat user", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  # Create a new user
  "Create a new test mtdvat user": {
    # $1: sheet to create user on
    "press": [
      ["CALL", "_Get nocache mtdvat user", "_$1_"],
      ["GOTO", "END"],
    ]
  },
}
