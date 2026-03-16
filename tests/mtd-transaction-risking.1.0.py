{
  "description": "Test mtd-transaction-risking request",
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
    "include": "tests/example/mtd-transaction-risking.1.0._misc_transaction-risking_assist_{vrn}-post.example.py",
    "press": [
      ["GENSHEET", "mtd-transaction-risking.1.0"],
      ["COPY", ["mtd-transaction-risking.1.0", "", "_parameters", "vrn"], ["mtdvat-user-0", "", "json", "vrn"]],
      ["COPY", ["mtd-transaction-risking.1.0", "", "_control", "_username"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "mtd-transaction-risking.1.0", "", "_control", "_userId"],
      ["COPY", ["mtd-transaction-risking.1.0", "", "_control", "_userId"], ["mtdvat-user-0", "", "json", "userId"]],
      ["ADD", "mtd-transaction-risking.1.0", "", "_control", "_password"],
      ["COPY", ["mtd-transaction-risking.1.0", "", "_control", "_password"], ["mtdvat-user-0", "", "json", "password"]],
      ["SUBMIT", "mtd-transaction-risking.1.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "403"],
      ["VALIDATE", ["sheet-info", "", "json", "code"], "RESOURCE_FORBIDDEN"],
      ["GOTO", "END"]
    ]
  }
}
