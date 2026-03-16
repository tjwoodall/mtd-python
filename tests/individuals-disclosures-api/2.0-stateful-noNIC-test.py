{
  "press": [
    ["GOSUB", "Get test mtdit user se and property on sheet mtdit-user-both"],
    ["GOSUB", "Create or amend", "mtdit-user-both"],
    ["GOSUB", "Retrieve", "_$0_", "mtdit-user-both"],
    ["GOSUB", "AddAvoidance", "_$0_", "mtdit-user-both"],
    ["GOSUB", "Delete", "mtdit-user-both"],
    ["GOTO", "END"],
  ],

  "Create or amend": {
    # 1: user details",
    "setup": { "include": "tests/example/individuals-disclosures-api.2.0._individuals_disclosures_{nino}_{taxYear}-put.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "sheet._$0_", "json", "taxAvoidance", "0", "taxYear", "2026-27"],
      ["DELETE", "sheet._$0_", "json", "class2Nics"],

      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve", "validate._$0_", "_$1_"],
      ["VALIDATE", ["sheet-info.validate._$0_", "json"], ["sheet._$0_", "json"],
        "(value['json'].pop('submittedOn'),value)[-1]"
      ],
      ["GOTO", "END"]
    ]
  },

  "Retrieve": {
    "note": "1: uuid for sheet/sheet-info, 2: user details",
    "setup": { "include": "tests/example/individuals-disclosures-api.2.0._individuals_disclosures_{nino}_{taxYear}-get.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$1_"],
      ["COPY", ["sheet._$1_", "_control", "_username"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet._$1_", "_control", "_userId"],
      ["COPY", ["sheet._$1_", "_control", "_userId"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet._$1_", "_control", "_password"],
      ["COPY", ["sheet._$1_", "_control", "_password"], ["_$2_", "json", "password"]],

      ["COPY", ["sheet._$1_", "_parameters", "nino"], ["_$2_", "json", "nino"]],
      ["EDIT", "sheet._$1_", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$1_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$1_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$1_", "sheet-info._$1_"],
      ["VALIDATE", ["sheet-info._$1_", "_control", "_response"], "200"],
      ["GOTO", "END"]
    ]
  },

  "Delete": {
    "note": "1: user details",
    "setup": { "include": "tests/example/individuals-disclosures-api.2.0._individuals_disclosures_{nino}_{taxYear}-delete.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["SUBMIT", "sheet._$0_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "204"],
      ["GOTO", "END"]
    ]
  },

  "AddAvoidance": {
    "setup": { "include": "tests/example/individuals-disclosures-api.2.0._individuals_disclosures_{nino}_{taxYear}-put.example.py", },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet.1._$0_"],
      ["COPY", ["sheet.1._$0_", "_control", "_username"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet.1._$0_", "_control", "_userId"],
      ["COPY", ["sheet.1._$0_", "_control", "_userId"], ["_$2_", "json", "userId"]],
      ["ADD", "sheet.1._$0_", "_control", "_password"],
      ["COPY", ["sheet.1._$0_", "_control", "_password"], ["_$2_", "json", "password"]],

      ["COPY", ["sheet.1._$0_", "_parameters", "nino"], ["_$2_", "json", "nino"]],

      ["EDIT", "sheet.1._$0_", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet.1._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet.1._$0_", "_parameters", "Gov-Test-Scenario", "STATEFUL"],

      ["COPY", ["sheet.1._$0_", "json", "taxAvoidance"], ["sheet-info._$1_", "json", "taxAvoidance"]],
      ["COPY", ["sheet.1._$0_", "json", "class2Nics"], ["sheet-info._$1_", "json", "class2Nics"]],

      ["ADD", "sheet.1._$0_", "json", "taxAvoidance", "1"],

      ["EDIT", "sheet.1._$0_", "json", "taxAvoidance", "1", "srn", "12345678"],
      ["EDIT", "sheet.1._$0_", "json", "taxAvoidance", "1", "taxYear", "2025-26"],

      ["SUBMIT", "sheet.1._$0_", "sheet-info.1._$0_"],
      ["VALIDATE", ["sheet-info.1._$0_", "_control", "_response"], "204"],

      ["GOSUB", "Retrieve", "validate._$0_", "_$2_"],
      ["VALIDATE", ["sheet-info.validate._$0_", "json"], ["sheet.1._$0_", "json"],
        "(value['json'].pop('submittedOn'),value)[-1]"
      ],
      ["VALIDATE", ["sheet-info.validate._$0_", "json"], ["sheet-info._$1_", "json"],
        "(value['json'].update(submittedOn=expected['json']['submittedOn']),value['json']['taxAvoidance'].pop(1),value)[-1]"
      ],
      ["GOTO", "END"]
    ]
  }
}
