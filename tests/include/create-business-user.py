{
  "_Get business user": {
    # _$1_ - control sheet
    "press": [
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "import-control-system"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "paye-for-employers"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "modernisation-of-authorisations"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "self-assessment"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "disa"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "safety-and-security"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "national-insurance"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "mtd-income-tax"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "goods-vehicle-movements"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "customs-services"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "relief-at-source"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "corporation-tax"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "excise-movement-control-system"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "common-transit-convention-traders-legacy"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "submit-vat-returns"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "lisa"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "pillar-2"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "secure-electronic-transfer"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "common-transit-convention-traders"],
      ["ADD", ["_$1_", "json", "serviceNames", "0"]],
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

  "_Get cached business user": {
    # $1 - user sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_organisations-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get business user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ],
    "cache": "artifacts/cache/_$1_.json"
  },

  "_Get nocache business user": {
    # $1 - user sheet
    # $2 - control sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_organisations-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get business user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ]
  },

  "Get test business user": {
    # $1 - user sheet
    "press": [
      ["CALL", "_Get cached business user", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  # Create a new user
  "Create a new test business user": {
    # $1: sheet to create user on
    "press": [
      ["CALL", "_Get nocache business user", "_$1_"],
      ["GOTO", "END"],
    ]
  },
}
