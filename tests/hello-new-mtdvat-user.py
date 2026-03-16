{
  "description": "call hello with user authentication creating a new mtdvat user and doing the login handshake",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdvat-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Create a new test mtdvat user on sheet new-mtdvat-user"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/api-example-microservice.1.0._hello_user-get.example.py",
    "press": [
      ["GENSHEET", "api-example-microservice.1.0"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_username"], ["new-mtdvat-user", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_userId"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_userId"], ["new-mtdvat-user", "", "json", "userId"]],
      ["ADD", "api-example-microservice.1.0", "", "_control", "_password"],
      ["COPY", ["api-example-microservice.1.0", "", "_control", "_password"], ["new-mtdvat-user", "", "json", "password"]],
      ["SUBMIT", "api-example-microservice.1.0", "sheet-hello"],
      ["VALIDATE", ["sheet-hello", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-hello", "", "json", "message"], "Hello User"],
      ["GOTO", "END"]
    ]
  }
}
