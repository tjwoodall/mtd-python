{
  "include": ["tests/include/create-mtdit-user.py", "tests/include/create-agent.py"],

  "press": [
    ["GOSUB", "Get test mtdit user 0 on sheet mtdit-user-0"],
    ["GOSUB", "Get test agent 0 on sheet agent-0"],
    ["GOSUB", "Create Request"],
    ["GOSUB", "Agent Request for user"],
    ["GOTO", "END"]
  ],

  "Create Request": {
    "setup": { "include": "tests/example/agent-authorisation-api.1.0._agents_{arn}_invitations-post.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "arn"], ["agent-0", "json", "agentServicesAccountNumber"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["agent-0", "json", "password"]],
      ["EDIT", "sheet._$0_", "json", "Agent Invitation Request for MTD-IT-0"],
      ["COPY", ["sheet._$0_", "json", "clientId"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "json", "knownFact"], ["mtdit-user-0", "json", "individualDetails", "address", "postcode"]],
      ["SUBMIT", "sheet._$0_", "agent-auth-req"],
      ["GOTO", "END", ["agent-auth-req", "json", "code"], "ALREADY_AUTHORISED"],
      ["GOSUB", "Accept Request", ["agent-auth-req", "_control", "_response"], "204"],
      ["GOTO", "END", ["agent-auth-req", "_control", "_response"], "204"],
      ["GOSUB", "Cancel Request", ["agent-auth-req", "json", "code"], "DUPLICATE_AUTHORISATION_REQUEST"],
      ["GOTO", "Create Request"],
    ]
  },

  "Accept Request": {
    "setup": { "include": "tests/example/agent-authorisation-test-support-api.1.0._agent-authorisation-test-support_invitations_{invitationId}-put.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "invitationId"], ["agent-auth-req", "_parameters", "Location"], "value.split('/')[-1]"],
      ["SUBMIT", "sheet._$0_", "agent-auth-response"],
      ["GOTO", "END", ["agent-auth-response", "_control", "_response"], "204"]
    ]
  },

  "Cancel Request": {
    "setup": { "include": "tests/example/agent-authorisation-api.1.0._agents_{arn}_invitations_{invitationId}-delete.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "sheet-tax-calc", "_parameters", "arn"], ["agent-0", "sheet-tax-calc", "json", "agentServicesAccountNumber"]],
      ["ADD", "sheet._$0_", "_parameters", "nino"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["agent-0", "json", "password"]],
      ["COPY", ["sheet._$0_", "_parameters", "invitationId"], ["agent-auth-req", "_parameters", "Location", "value.split('/')[-1]"]],
      ["SUBMIT", "sheet._$0_", "cancel-response"],
      ["GOTO", "END"]
    ]
  },

  "Agent Request for user": {
    "setup": { "include": "tests/example/individual-calculations-api.8.0._individuals_calculations_{nino}_self-assessment_{taxYear}_{calculationId}-get.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["ADD", "sheet._$0_", "_control", "arn"],
      ["COPY", ["sheet._$0_", "_control", "arn"], ["agent-0", "json", "agentServicesAccountNumber"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["agent-0", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["agent-0", "json", "password"]],
      ["EDIT", "sheet._$0_", "_parameters", "taxYear", "2026-27"],
      ["ADD", "sheet._$0_", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "sheet._$0_", "_parameters", "Gov-Test-Scenario", "DYNAMIC"],
      ["SUBMIT", "sheet._$0_", "sheet-tax-calc"],
      ["VALIDATE", ["sheet-tax-calc", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-tax-calc", "json"], "TY 2026-27 onwards-3"],
      ["VALIDATE", ["sheet-tax-calc", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-tax-calc", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-tax-calc", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-tax-calc", "json", "calculation", "endOfYearEstimate", "totalAllowancesAndDeductions"], 5311],
      ["VALIDATE", ["sheet-tax-calc", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },
}
