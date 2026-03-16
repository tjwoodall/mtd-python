{
  "description": "Test customs-inventory-linking-exports request",
  "schema": "artifacts/application.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-business-user.py"],

  "START": {
    "press": [
      ["GOSUB", "Get test business user 0 on sheet business-user-0"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/customs-inventory-linking-exports.2.0._customs_inventory-linking_exports-post.example.py",
    "press": [
      ["GENSHEET", "customs-inventory-linking-exports.2.0"],
      ["COPY", ["customs-inventory-linking-exports.2.0", "", "_control", "_username"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "customs-inventory-linking-exports.2.0", "", "_control", "_userId"],
      ["COPY", ["customs-inventory-linking-exports.2.0", "", "_control", "_userId"], ["business-user-0", "", "json", "userId"]],
      ["ADD", "customs-inventory-linking-exports.2.0", "", "_control", "_password"],
      ["COPY", ["customs-inventory-linking-exports.2.0", "", "_control", "_password"], ["business-user-0", "", "json", "password"]],
      ["EDIT", "customs-inventory-linking-exports.2.0", "", "xml", "<inv:inventoryLinkingQueryRequest xmlns:inv=\"http://gov.uk/customs/inventoryLinking/v1\">\n  <inv:queryUCR>\n  <inv:ucr>GB/AAAA-00000</inv:ucr>\n  <inv:ucrPartNo>123A</inv:ucrPartNo>\n  <inv:ucrType>D</inv:ucrType>\n  </inv:queryUCR>\n</inv:inventoryLinkingQueryRequest>"],
      ["SUBMIT", "customs-inventory-linking-exports.2.0", "sheet-info"],
      ["VALIDATE", ["sheet-info", "", "_control", "_response"], "403"],
      ["VALIDATE", ["sheet-info", "", "xml", "", "errorResponse", "code"], "RESOURCE_FORBIDDEN"],
      ["GOTO", "END"]
    ]
  }
}
