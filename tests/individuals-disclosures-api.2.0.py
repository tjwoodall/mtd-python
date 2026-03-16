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
      ["CALL", "Get test mtdit user se and property", "mtdit-user-both"],
# Stateful tests
      ["CALL", "Stateful.noNIC", "mtdit-user-both"],
      ["CALL", "Stateful", "mtdit-user-both"],

# gov-test canned responses
      ["CALL", "Create and Amend Disclosures"],
      ["CALL", "Delete Disclosures"],
      ["CALL", "Retrieve Disclosures"],
      ["CALL", "Create Marriage Allowance"],

      ["GOTO", "END"]
    ]
  }
}
