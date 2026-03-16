{
  # $1 request sheet

  "press": [
    ["EDIT", ["_$1_", "_parameters", "Gov-Test-Scenario"], "LATE_SUBMISSION"],

    ["SUBMIT", "_$1_", "sheet-info._$0_"],
    ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],

    ["GOTO", "END"]
  ]
}

