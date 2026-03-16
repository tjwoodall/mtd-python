{
  "description": "Retrieve VAT penalties",
  "include": ["tests/include/create-mtdvat-user.py",
  ],

  "press": [
    ["CALL", "Get test mtdvat user", "mtdvat-user-0"],

    ["CALL", "run", "mtdvat-user-0"],
    ["GOTO", "END"]
  ],

  "run": {
    # Retrieve VAT penalties
    # $1 user details

    "setup": { "include": "tests/example/vat-api.1.0._organisations_vat_{vrn}_penalties-get.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_userId"]],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_password"]],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "vrn"], ["_$1_", "json", "vrn"]],

# Get the canned response
      ["CALL", "CannedResponse-DEFAULT", "sheet._$0_"],

# Check the various Got-Test-Scenario
      ["ADD", ["sheet._$0_", "_parameters", "Gov-Test-Scenario"]],
      ["CALL", "CannedResponse-NO_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-LATE_SUBMISSION", "sheet._$0_"],
      ["CALL", "CannedResponse-LATE_PAYMENT", "sheet._$0_"],
      ["CALL", "CannedResponse-MULTIPLE_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-MULTIPLE_LATE_PAYMENT_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-MULTIPLE_LATE_SUBMISSION_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-MULTIPLE_INACTIVE_LATE_SUBMISSION_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-THRESHOLD_LATE_SUBMISSION_PENALTIES", "sheet._$0_"],
      ["CALL", "CannedResponse-CHARGE_LATE_SUBMISSION_PENALTIES", "sheet._$0_"],
      ["DELETE", ["sheet._$0_", "_parameters", "Gov-Test-Scenario"]],

      ["GOTO", "END"]
    ]
  },

  "CannedResponse-DEFAULT":                                     { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-DEFAULT.py" },
  "CannedResponse-NO_PENALTIES":                                { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-NO_PENALTIES.py" },
  "CannedResponse-LATE_SUBMISSION":                             { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-LATE_SUBMISSION.py" },
  "CannedResponse-LATE_PAYMENT":                                { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-LATE_PAYMENT.py" },
  "CannedResponse-MULTIPLE_PENALTIES":                          { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-MULTIPLE_PENALTIES.py" },
  "CannedResponse-MULTIPLE_LATE_PAYMENT_PENALTIES":             { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-MULTIPLE_LATE_PAYMENT_PENALTIES.py" },
  "CannedResponse-MULTIPLE_LATE_SUBMISSION_PENALTIES":          { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-MULTIPLE_LATE_SUBMISSION_PENALTIES.py" },
  "CannedResponse-MULTIPLE_INACTIVE_LATE_SUBMISSION_PENALTIES": { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-MULTIPLE_INACTIVE_LATE_SUBMISSION_PENALTIES.py" },
  "CannedResponse-THRESHOLD_LATE_SUBMISSION_PENALTIES":         { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-THRESHOLD_LATE_SUBMISSION_PENALTIES.py" },
  "CannedResponse-CHARGE_LATE_SUBMISSION_PENALTIES":            { "include": "tests/vat-api/1.0.GetVatPenalties-gov-test-CHARGE_LATE_SUBMISSION_PENALTIES.py" },
}
