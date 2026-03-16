{
  "description": "Test marriage-allowance request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-sa-user.py", "tests/include/create-business-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test sa user 0 on sheet sa-user-0"],
      ["GOTO", "Get test-user2"]
    ]
  },

  "Get test-user2": {
    "press": [
      ["GOSUB", "Get test sa user 1 on sheet sa-user-1"],
      ["GOTO", "Get test-user3"]
    ]
  },

  "Get test-user3": {
    "press": [
      ["GOSUB", "Get test business user 0 on sheet business-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/marriage-allowance-des-stub.1.0._marriage-allowance-test-support_sa_{utr}_status_{taxYear}-post.example.py",
    "press": [
      ["GENSHEET", "setup-marriage-allowance.1.0.1"],
      ["COPY", ["setup-marriage-allowance.1.0.1", "", "_parameters", "utr"], ["sa-user-1", "", "json", "saUtr"]],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "json", "status", "Recipient"],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "json", "deceased", False],
      ["SUBMIT", "setup-marriage-allowance.1.0.1", "create-marriage-allowance.1"],
      ["GOTO", "set info2", ["create-marriage-allowance.1", "", "_control", "_response"], "201"]
    ]
  },

  "set info2": {
    "press": [
      ["COPY", ["setup-marriage-allowance.1.0.1", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "json", "status", "Transferor"],
      ["EDIT", "setup-marriage-allowance.1.0.1", "", "json", "deceased", False],
      ["SUBMIT", "setup-marriage-allowance.1.0.1", "create-marriage-allowance.2"],
      ["GOTO", "setup3", ["create-marriage-allowance.2", "", "_control", "_response"], "201"]
    ]
  },

  "setup3": {
    "include": "tests/example/marriage-allowance-des-stub.1.0._marriage-allowance-test-support_nino_{nino}_eligibility_{taxYear}-post.example.py",
    "press": [
      ["GENSHEET", "setup-marriage-allowance.1.0.3"],
      ["COPY", ["setup-marriage-allowance.1.0.3", "", "_parameters", "nino"], ["sa-user-1", "", "json", "nino"]],
      ["EDIT", "setup-marriage-allowance.1.0.3", "", "_parameters", "taxYear", "2026-27"],
      ["EDIT", "setup-marriage-allowance.1.0.3", "", "json", "eligible", True],
      ["SUBMIT", "setup-marriage-allowance.1.0.3", "create-marriage-allowance.3"],
      ["GOTO", "setup4", ["create-marriage-allowance.3", "", "_control", "_response"], "201"]
    ]
  },

  "setup4": {
    "include": "tests/example/marriage-allowance.2.0._marriage-allowance_sa_{utr}_eligibility-post.example.py",
    "press": [
      ["GENSHEET", "marriage-allowance.2.0"],
      ["COPY", ["marriage-allowance.2.0", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["COPY", ["marriage-allowance.2.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "marriage-allowance.2.0", "", "_control", "_userId"],
      ["COPY", ["marriage-allowance.2.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "marriage-allowance.2.0", "", "_control", "_password"],
      ["COPY", ["marriage-allowance.2.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["COPY", ["marriage-allowance.2.0", "", "json", "nino"], ["sa-user-1", "", "json", "nino"]],
      ["COPY", ["marriage-allowance.2.0", "", "json", "firstname"], ["sa-user-1", "", "json", "individualDetails", "firstName"]],
      ["COPY", ["marriage-allowance.2.0", "", "json", "surname"], ["sa-user-1", "", "json", "individualDetails", "lastName"]],
      ["COPY", ["marriage-allowance.2.0", "", "json", "dateOfBirth"], ["sa-user-1", "", "json", "individualDetails", "dateOfBirth"]],
      ["EDIT", "marriage-allowance.2.0", "", "json", "taxYear", "2026-27"],
      ["SUBMIT", "marriage-allowance.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "404"],
      ["VALIDATE", ["sheet-info", "", "json", "code"], "MATCHING_RESOURCE_NOT_FOUND"],
      ["GOTO", "END"]
    ]
  }
}
