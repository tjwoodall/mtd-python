{
  "description": "Test individual-losses-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user se and property on sheet mtdit-user-both"],
      ["GOSUB", "_Get list of businesses", "mtdit-user-both", "list businesses.both" ],
      ["GOSUB", "Create or amend.2026", "mtdit-user-both", "list businesses.both"],
      ["GOSUB", "Retrieve.2026", "mtdit-user-both", "list businesses.both"],
      ["GOSUB", "Delete.2026", "mtdit-user-both", "list businesses.both"],
      ["GOTO", "END"]
    ]
  },

  "Create or amend.2026": {
    "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-put.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "businessId"], ["_$2_", "", "json", "listOfBusinesses", "0", "", "businessId"]],

      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["DELETE", "sheet._$0_", "", "json", "claims", "carryBack", "terminalLosses"],
      ["EDIT", "sheet._$0_", "", "json", "claims", "preferenceOrder", "applyFirst", "carry-back"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },

  "Retrieve.2026": {
    "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-get.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "businessId"], ["_$2_", "", "json", "listOfBusinesses", "0", "", "businessId"]],

      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],
      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "", "json", "claims", "carryBack", "earlyYearLosses"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "Delete.2026": {
    "include": "tests/example/individual-losses-api.7.0._individuals_losses_{nino}_businesses_{businessId}_loss-claims_{taxYear}-delete.example.py",
    "press": [
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "", "_control", "_username"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "", "_control", "_userId"], ["_$1_", "", "json", "userId"]],
      ["ADD", "sheet._$0_", "", "_control", "_password"],
      ["COPY", ["sheet._$0_", "", "_control", "_password"], ["_$1_", "", "json", "password"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "nino"], ["_$1_", "", "json", "nino"]],

      ["COPY", ["sheet._$0_", "", "_parameters", "businessId"], ["_$2_", "", "json", "listOfBusinesses", "0", "", "businessId"]],

      ["EDIT", "sheet._$0_", "", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  }
}
