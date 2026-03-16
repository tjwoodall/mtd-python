{
  "_Get mtdit user": {
    # _$1_ - control sheet
    "press": [
      ["EDIT", ["_$1_", "json", "serviceNames", "0"], "mtd-income-tax"],
      ["DELETE", ["_$1_", "json", "eoriNumber"]],
      ["DELETE", ["_$1_", "json", "nino"]],
      ["GOTO", "END"]
    ],
  },

  "_Get cached mtdit user": {
    # $1 - user sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_individuals-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get mtdit user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ],
    "cache": "artifacts/cache/_$1_.json"
  },

  "_Get nocache mtdit user": {
    # $1 - user sheet
    # $2 - control sheet
    "setup": { "include": "tests/example/api-platform-test-user.1.0._create-test-user_individuals-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["CALL", "_Get mtdit user", "sheet._$0_"],
      ["SUBMIT", "sheet._$0_", "_$1_"],
      ["GOTO", "END"]
    ]
  },

  "Get test mtdit user": {
    # $1 - user sheet
    "press": [
      ["CALL", "_Get cached mtdit user", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  # Create a new user
  "Create a new test mtdit user": {
    # $1: sheet to create user on
    "press": [
      ["CALL", "_Get nocache mtdit user", "_$1_"],
      ["GOTO", "END"],
    ]
  },

  "_Get list of businesses": {
    # Check if there's already a business defined
    # $1 - user sheet
    # $2 - list of businesses sheet
    "setup": { "include": "tests/example/business-details-api.2.0._individuals_business_details_{nino}_list-get.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet_$0_"],
      ["COPY", ["sheet_$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],
      ["COPY", ["sheet_$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet_$0_", "_control", "_userId"]],
      ["COPY", ["sheet_$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet_$0_", "_control", "_password"]],
      ["COPY", ["sheet_$0_", "_control", "_password"], ["_$1_", "json", "password"]],
      ["ADD", ["sheet_$0_", "_parameters", "Gov-Test-Scenario"]],
      ["EDIT", ["sheet_$0_", "_parameters", "Gov-Test-Scenario"], "STATEFUL"],
      ["SUBMIT", "sheet_$0_", "_$2_"],
      ["GOTO", "END"]
    ]
  },

  "Get test mtdit user property": {
    # Get a mtdit user with a property business
    # $1 - user sheet
    "Done": {
      "press": [
        ["GOTO", "END"],
      ]
    },
    "press": [
      ["CALL", "_Get cached mtdit user", "_$1_"],
      # Check if there's already a business defined
      ["CALL", "_Get list of businesses", "_$1_", "list businesses._$0_" ],
      ["IF", "Done", ["list businesses._$0_", "json", "listOfBusinesses"], 1],
      ["VALIDATE", ["list businesses._$0_", "json", "listOfBusinesses"], 0],
      ["CALL", "_Add a property business", "_$1_" ],
      ["GOTO", "END"]
    ]
  },

  "_Add a property business": {
    # Add a property business
    # $1 - user sheet
    "setup": { "include": "tests/example/mtd-sa-test-support-api.1.0._individuals_self-assessment-test-support_business_{nino}-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],

      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_userId"]],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_password"]],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["EDIT", ["sheet._$0_", "json", "typeOfBusiness"], "uk-property"],
      ["DELETE", ["sheet._$0_", "json", "tradingType"]],
      ["DELETE", ["sheet._$0_", "json", "tradingName"]],
      ["DELETE", ["sheet._$0_", "json", "firstAccountingPeriodStartDate"]],
      ["DELETE", ["sheet._$0_", "json", "firstAccountingPeriodEndDate"]],
      ["DELETE", ["sheet._$0_", "json", "latencyDetails"]],
      ["DELETE", ["sheet._$0_", "json", "quarterlyTypeChoice"]],
      ["EDIT", ["sheet._$0_", "json", "accountingType"], "ACCRUALS"],
      ["DELETE", ["sheet._$0_", "json", "commencementDate"]],
      ["DELETE", ["sheet._$0_", "json", "cessationDate"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineOne"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineTwo"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineThree"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineFour"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressPostcode"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressCountryCode"]],

      ["SUBMIT", "sheet._$0_", "test-business._$0_"],

      ["VALIDATE", ["test-business._$0_", "_control", "_response"], "201"],
      ["GOTO", "END"]
    ]
  },

  "Get test mtdit user self-employment": {
    # Get a mtdit user with a self-employment  business
    # $1 - user sheet
    "Done": {
      "press": [
        ["GOTO", "END"],
      ]
    },
    "press": [
      ["CALL", "_Get cached mtdit user", "_$1_"],
      # Check if there's already a business defined
      ["CALL", "_Get list of businesses", "_$1_", "list businesses._$0_" ],
      ["IF", "Done", ["list businesses._$0_", "json", "listOfBusinesses"], 1],
      ["VALIDATE", ["list businesses._$0_", "json", "listOfBusinesses"], 0],
      ["CALL", "_Add a self-employment business", "_$1_" ],
      ["GOTO", "END"]
    ]
  },

  "_Add a self-employment business": {
    # Add a self-employment business
    # $1 - user sheet
    "setup": { "include": "tests/example/mtd-sa-test-support-api.1.0._individuals_self-assessment-test-support_business_{nino}-post.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],

      ["COPY", ["sheet._$0_", "_control", "_username"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_userId"]],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["_$1_", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_password"]],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["_$1_", "json", "password"]],

      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["_$1_", "json", "nino"]],

      ["PRINT", "sheet._$0_"],

      ["EDIT", ["sheet._$0_", "json", "typeOfBusiness"], "self-employment"],
      ["EDIT", ["sheet._$0_", "json", "tradingType"], "SEbusinessTradingType"],
      ["EDIT", ["sheet._$0_", "json", "tradingName"], "SEbusinessTradingName"],
      ["DELETE", ["sheet._$0_", "json", "firstAccountingPeriodStartDate"]],
      ["DELETE", ["sheet._$0_", "json", "firstAccountingPeriodEndDate"]],
      ["DELETE", ["sheet._$0_", "json", "latencyDetails"]],
      ["DELETE", ["sheet._$0_", "json", "quarterlyTypeChoice"]],
      ["EDIT", ["sheet._$0_", "json", "accountingType"], "ACCRUALS"],
      ["DELETE", ["sheet._$0_", "json", "commencementDate"]],
      ["DELETE", ["sheet._$0_", "json", "cessationDate"]],
      ["EDIT", ["sheet._$0_", "json", "businessAddressLineOne"], "1 Main Street"],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineTwo"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineThree"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressLineFour"]],
      ["DELETE", ["sheet._$0_", "json", "businessAddressPostcode"]],
      ["EDIT", ["sheet._$0_", "json", "businessAddressCountryCode"], "IE"],

      ["SUBMIT", "sheet._$0_", "test-business._$0_"],

      ["VALIDATE", ["test-business._$0_", "_control", "_response"], "201"],
      ["GOTO", "END"]
    ]
  },

  "Get test mtdit user se and property": {
    # Get a mtdit user with both a self-employment and a property business
    "Done": {
      "press": [
        ["GOTO", "END"],
      ]
    },
    "press": [
      ["CALL", "_Get cached mtdit user", "_$1_"],
      ["CALL", "_Get list of businesses", "_$1_", "list businesses._$0_" ],
      # Check if there's already businesses defined
      ["IF", "Done", ["list businesses._$0_", "json", "listOfBusinesses"], 2],
      ["IF", "Get test mtdit user se and property.1", ["list businesses._$0_", "json", "listOfBusinesses"], 1],
      ["VALIDATE", ["list businesses._$0_", "json", "listOfBusinesses"], 0],
      ["CALL", "_Add a self-employment business", "_$1_" ],
      ["GOTO", "Get test mtdit user se and property.1"]
    ]
  },

  "Get test mtdit user se and property.1": {
    "press": [
      ["CALL", "_Add a property business", "_$1_" ],
      ["GOTO", "END"]
    ]
  },
}
