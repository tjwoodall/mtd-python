{
  "description": "Test individuals-disclosures-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
  ],

  "Stateful.noNIC": {
    "include": "tests/individuals-disclosures-api/2.0-stateful-noNIC-test.py",
  },

  "Stateful": {
    "include": "tests/individuals-disclosures-api/2.0-stateful-test.py",
  },

  "Create and Amend Disclosures": {
    "include": "tests/individuals-disclosures-api/2.0-create-gov-test.py",
  },

  "Delete Disclosures": {
    "include": "tests/individuals-disclosures-api/2.0-delete-gov-test.py",
  },

  "Retrieve Disclosures": {
    "include": "tests/individuals-disclosures-api/2.0-get-gov-test.py",
  },

  "Create Marriage Allowance": {
    "include": "tests/individuals-disclosures-api/2.0-marriage-allowance-create-gov-test.py",
  },


  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user se and property on sheet mtdit-user-both"],
# Stateful tests
      ["GOSUB", "Stateful.noNIC", "mtdit-user-both"],
      ["GOSUB", "Stateful", "mtdit-user-both"],

# gov-test canned responses
      ["GOSUB", "Create and Amend Disclosures"],
      ["GOSUB", "Delete Disclosures"],
      ["GOSUB", "Retrieve Disclosures"],
      ["GOSUB", "Create Marriage Allowance"],

      ["GOTO", "END"]
    ]
  }
}
