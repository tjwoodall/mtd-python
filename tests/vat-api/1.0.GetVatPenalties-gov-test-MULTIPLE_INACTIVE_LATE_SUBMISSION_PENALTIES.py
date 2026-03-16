{
  # $1 request sheet

  "press": [
    ["EDIT", ["_$1_", "_parameters", "Gov-Test-Scenario"], "MULTIPLE_INACTIVE_LATE_SUBMISSION_PENALTIES"],

    ["SUBMIT", "_$1_", "sheet-info._$0_"],
    ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],

    ["GOTO", "END"]
  ]
}

