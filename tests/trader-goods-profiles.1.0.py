{
  "description": "Test trader-goods-profiles request",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-sa-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test sa user 0 on sheet sa-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/trader-goods-profiles.1.0._customs_traders_goods-profiles_{eori}-put.example.py",
    "press": [
      ["GENSHEET", "trader-goods-profiles.1.0"],
      ["COPY", ["trader-goods-profiles.1.0", "", "_parameters", "eori"], ["sa-user-0", "", "json", "eoriNumber"]],
      ["COPY", ["trader-goods-profiles.1.0", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0", "", "_control", "_userId"],
      ["COPY", ["trader-goods-profiles.1.0", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0", "", "_control", "_password"],
      ["COPY", ["trader-goods-profiles.1.0", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["COPY", ["trader-goods-profiles.1.0", "", "json", "actorId"], ["sa-user-0", "", "json", "eoriNumber"]],
      ["ADD", "trader-goods-profiles.1.0", "", "json", "nirmsNumber"],
      ["ADD", "trader-goods-profiles.1.0", "", "json", "niphlNumber"],
      ["SUBMIT", "trader-goods-profiles.1.0", "sheet-info"],
      ["GOTO", "setup2", ["sheet-info", "", "_control", "_response"], "200"]
    ]
  },

  "setup2": {
    "include": "tests/example/trader-goods-profiles.1.0._customs_traders_goods-profiles_{eori}_records-get.example.py",
    "press": [
      ["GENSHEET", "trader-goods-profiles.1.0.1"],
      ["COPY", ["trader-goods-profiles.1.0.1", "", "_parameters", "eori"], ["sa-user-0", "", "json", "eoriNumber"]],
      ["COPY", ["trader-goods-profiles.1.0.1", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0.1", "", "_control", "_userId"],
      ["COPY", ["trader-goods-profiles.1.0.1", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0.1", "", "_control", "_password"],
      ["COPY", ["trader-goods-profiles.1.0.1", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["COPY", ["trader-goods-profiles.1.0.1", "", "_parameters", "lastUpdatedDate"], ["sa-user-0", "", "json", "password"], "now().strftime('%Y-%m-%dT%H:%M:%SZ')"],
      ["EDIT", "trader-goods-profiles.1.0.1", "", "_parameters", "page", 0],
      ["EDIT", "trader-goods-profiles.1.0.1", "", "_parameters", "size", 10],
      ["SUBMIT", "trader-goods-profiles.1.0.1", "sheet-info2"],
      ["GOTO", "add", ["sheet-info2", "", "json", "pagination", "totalRecords"], 0]
    ]
  },

  "add": {
    "include": "tests/example/trader-goods-profiles.1.0._customs_traders_goods-profiles_{eori}_records-post.example.py",
    "press": [
      ["GENSHEET", "trader-goods-profiles.1.0.2"],
      ["COPY", ["trader-goods-profiles.1.0.2", "", "_parameters", "eori"], ["sa-user-0", "", "json", "eoriNumber"]],
      ["COPY", ["trader-goods-profiles.1.0.2", "", "_control", "_username"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0.2", "", "_control", "_userId"],
      ["COPY", ["trader-goods-profiles.1.0.2", "", "_control", "_userId"], ["sa-user-0", "", "json", "userId"]],
      ["ADD", "trader-goods-profiles.1.0.2", "", "_control", "_password"],
      ["COPY", ["trader-goods-profiles.1.0.2", "", "_control", "_password"], ["sa-user-0", "", "json", "password"]],
      ["COPY", ["trader-goods-profiles.1.0.2", "", "json", "traderRef"], ["trader-goods-profiles.1.0.2", "", "json", "traderRef"], "hex(int(now().timestamp() * 1000000000))"],
      ["SUBMIT", "trader-goods-profiles.1.0.2", "sheet-info3"],
      ["GOTO", "get info3", ["sheet-info3", "", "_control", "_response"], "201"]
    ]
  },

  "get info3": {
    "press": [
      ["SUBMIT", "trader-goods-profiles.1.0.1", "sheet-info4"],
      ["VALIDATE", ["sheet-info4", "", "json", "pagination", "totalRecords"], 1],
      ["VALIDATE", ["sheet-info4", "", "json", "pagination", "totalPages"], 1],
      ["VALIDATE", ["sheet-info4", "", "json", "pagination", "currentPage"], 0],
      ["GOTO", "END"]
    ]
  }
}
