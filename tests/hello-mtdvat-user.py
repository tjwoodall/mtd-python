{
  "description": "call hello with user authentication (mtdvat user)",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdvat-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test mtdvat user 0 on sheet mtdvat-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/api-example-microservice.1.0._hello_user-get.example.py",
    "press": [
      ["GENSHEET", "api-example-microservice.1.0"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_username"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_userId"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_userId"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_password"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_password"], ["mtdvat-user-0", "", "json", "password"]],
      ["SUBMIT", "api-example-microservice.1.0", "sheet-hello"],
      ["VALIDATE", ["sheet-hello", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-hello", "", "json", "message"], "Hello User"],
      ["GOTO", "END"]
    ]
  }
}
