{
  # $1 request sheet

  "press": [
    ["SUBMIT", "_$1_", "sheet-info._$0_"],
    ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],

    ["GOTO", "END"]
  ]
}

