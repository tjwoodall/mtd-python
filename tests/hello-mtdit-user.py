{
  "description": "call hello with user authentication (mtdit user)",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/api-example-microservice.1.0._hello_user-get.example.py",
    "press": [
      ["GENSHEET", "api-example-microservice.1.0"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_username"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_userId"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_userId"], ["mtdit-user-0", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_password"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_password"], ["mtdit-user-0", "", "json", "password"]],
      ["SUBMIT", "api-example-microservice.1.0", "sheet-hello"],
      ["VALIDATE", ["sheet-hello", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-hello", "", "json", "message"], "Hello User"],
      ["GOTO", "END"]
    ]
  }
}
