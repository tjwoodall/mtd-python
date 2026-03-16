{
  "description": "Test individuals-charges-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py",
  ],

  "HICB.2026": {
    "include": "tests/individuals-charges-api/3.0.HICB.2026.py",
  },

  "pension.2023": {
    "include": "tests/individuals-charges-api/3.0.pension.2023.py",
  },

  "pension.2026": {
    "include": "tests/individuals-charges-api/3.0.pension.2026.py",
  },

  "winter-fuel-payment.2026": {
    "include": "tests/individuals-charges-api/3.0.winter-fuel-payment.2026.py"
  },

  "Create or Amend High Income Child Benefit Charge Submission": {
    "include": "tests/individuals-charges-api/3.0-HICB-create-gov-test.py"
  },

  "Delete High Income Child Benefit Charge Submission": {
    "include": "tests/individuals-charges-api/3.0-HICB-delete-gov-test.py"
  },

  "Retrieve High Income Child Benefit Charge Submission": {
    "include": "tests/individuals-charges-api/3.0-HICB-get-gov-test.py"
  },

  "Create and Amend Pension Charges": {
    "include": "tests/individuals-charges-api/3.0-pension-create-gov-test.py"
  },

  "Delete Pension Charges": {
    "include": "tests/individuals-charges-api/3.0-pension-delete-gov-test.py"
  },

  "Retrieve Pension Charges": {
    "include": "tests/individuals-charges-api/3.0-pension-get-gov-test.py"
  },

  "Create or Amend Winter Fuel Payment": {
    "include": "tests/individuals-charges-api/3.0-winter-fuel-create-gov-test.py"
  },

  "Delete Winter Fuel Payment": {
    "include": "tests/individuals-charges-api/3.0-winter-fuel-delete-gov-test.py"
  },

  "Retrieve Winter Fuel Payment": {
    "include": "tests/individuals-charges-api/3.0-winter-fuel-get-gov-test.py"
  },

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],

# Stateful tests
      ["GOSUB", "HICB.2026"],
      ["GOSUB", "pension.2026"],
      ["GOSUB", "pension.2023"],
      ["GOSUB", "winter-fuel-payment.2026"],

# gov-test canned responses
      ["GOSUB", "Create or Amend High Income Child Benefit Charge Submission"],
      ["GOSUB", "Delete High Income Child Benefit Charge Submission"],
      ["GOSUB", "Retrieve High Income Child Benefit Charge Submission"],
      ["GOSUB", "Create and Amend Pension Charges"],
      ["GOSUB", "Delete Pension Charges"],
      ["GOSUB", "Retrieve Pension Charges"],
      ["GOSUB", "Create or Amend Winter Fuel Payment"],
      ["GOSUB", "Delete Winter Fuel Payment"],
      ["GOSUB", "Retrieve Winter Fuel Payment"],

      ["GOTO", "END"]
    ]
  }
}
