{
  "description": "Test individuals-disclosures-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
              "tests/individuals-disclosures-api/individuals-disclosures-api.2.0-stateful-noNIC-test.py",
              "tests/individuals-disclosures-api/individuals-disclosures-api.2.0-stateful-test.py",
              "tests/individuals-disclosures-api/individuals-disclosures-api.2.0-stateful-add-tax-avoidance.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user se and property on sheet mtdit-user-both"],

      ["GOSUB", "Create or amend", "mtdit-user-both"],
      ["GOSUB", "AddAvoidance", "mtdit-user-both"],
      ["GOSUB", "Delete", "mtdit-user-both"],

      ["GOSUB", "Create or amend no NIC", "mtdit-user-both"],
      ["GOSUB", "AddAvoidance", "mtdit-user-both"],
      ["GOSUB", "Delete", "mtdit-user-both"],
      ["GOTO", "END"]
    ]
  }
}
