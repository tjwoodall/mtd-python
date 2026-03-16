{
  "_Get sa user": {
    # _$1_ - control sheet
    "press": [
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "self-assessment"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "national-insurance"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "mtd-income-tax"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "customs-services"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "goods-vehicle-movements"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "import-control-system"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "mtd-vat"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "common-transit-convention-traders"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "common-transit-convention-traders-legacy"],
      ["DELETE", ["_$1_", "json", "eoriNumber"]],
      ["DELETE", ["_$1_", "json", "nino"]],
      ["GOTO", "END"]
    ],
  },

  "_Get cached sa user": {
    # $1 - user sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_individuals-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get sa user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ],
    "cache": "artifacts/cache/_$1_.json"
  },

  "_Get nocache sa user": {
    # $1 - user sheet
    # $2 - control sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_individuals-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get sa user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ]
  },

  "Get test sa user": {
    # $1 - user sheet
    "press": [
      ["CALL", "_Get cached sa user", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  # Create a new user
  "Create a new test sa user": {
    # $1: sheet to create user on
    "press": [
      ["CALL", "_Get nocache sa user", "_$1_"],
      ["GOTO", "END"],
    ]
  },
}
