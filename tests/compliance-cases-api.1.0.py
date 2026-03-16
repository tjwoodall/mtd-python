{
  "description": "Test compliance-cases-api request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "START": {
    "setup": { "include": "tests/example/compliance-cases-api.1.0._misc_compliance-cases_case-post.example.py" },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],

      ["EDIT", ["sheet._$0_", "json", "case", "campaignId"], "CID-0"],
      ["EDIT", ["sheet._$0_", "json", "case", "risks", "0", "taxPeriodStart"], "2026-06-04"],
      ["EDIT", ["sheet._$0_", "json", "case", "risks", "0", "riskStartDate"], "2026-06-04"],
      ["EDIT", ["sheet._$0_", "json", "case", "risks", "0", "taxPeriodEnd"], "2027-06-05"],
      ["EDIT", ["sheet._$0_", "json", "case", "lastDateForEnquiry"], "2028-06-05"],
      ["EDIT", ["sheet._$0_", "json", "case", "projectId"], "PID-0"],
      ["EDIT", ["sheet._$0_", "json", "taxPayer", "addresses", "0", "postcode"], "SW1A 0AA"],
      ["EDIT", ["sheet._$0_", "json", "taxPayer", "referenceNumbers", "0", "referenceValue"], "REFERENCEVALUE"],

      ["SUBMIT", "sheet._$0_", "sheet-info"],

      # No idea why...
      ["VALIDATE", ["sheet-info", "_control", "_response"], "403"],
      ["VALIDATE", ["sheet-info", "json", "code"], "INVALID_SCOPE"],
      ["VALIDATE", ["sheet-info", "json", "message"], "Can not access the required resource. Ensure this token has all the required scopes."],

      ["GOTO", "END"]
    ]
  }
}
