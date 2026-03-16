{
  "description": "Test self-assessment-liability-api request (private api)",
  "schema": "artifacts/application.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-sa-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test sa user 0 on sheet sa-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/self-assessment-liability-api.1.0._individuals_self-assessment_breakdown_{utr}-get.example.py",
    "press": [
      ["GENSHEET", "self-assessment-liability-api.1.0"],
      ["COPY", ["self-assessment-liability-api.1.0", "", "_parameters", "utr"], ["sa-user-0", "", "json", "saUtr"]],
      ["COPY", ["self-assessment-liability-api.1.0", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-liability-api.1.0", "", "_control", "_userId"],
      ["COPY", ["self-assessment-liability-api.1.0", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "self-assessment-liability-api.1.0", "", "_control", "_password"],
      ["COPY", ["self-assessment-liability-api.1.0", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["SUBMIT", "self-assessment-liability-api.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "403"],
      ["VALIDATE", ["sheet-info", "", "json", "code"], "RESOURCE_FORBIDDEN"],
      ["GOTO", "END"]
    ]
  }
}
