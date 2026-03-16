{
  "description": "This creates a new agent, a new mtdit user, gets agent authorisation and then the agent requests a tax calculation for the user",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdit-user.py", "tests/include/create-agent.py"],

  "START": {
    "press": [
      ["GOSUB", "Create a new test mtdit user on sheet new-mtdit-user"],
      ["GOTO", "Get test-agent"]
    ]
  },

  "Get test-agent": {
    "press": [
      ["GOSUB", "Create a new test agent on sheet new-agent"],
      ["GOTO", "setup"]
    ]
  },

  "setup": {
    "include": "tests/example/agent-authorisation-api.1.0._agents_{arn}_invitations-post.example.py",
    "press": [
      ["GENSHEET", "agent-authorisation-api.1.0"],
      ["COPY", ["agent-authorisation-api.1.0", "", "_parameters", "arn"], ["new-agent", "", "json", "agentServicesAccountNumber"]],
      ["COPY", ["agent-authorisation-api.1.0", "", "_control", "_username"], ["new-agent", "", "json", "userId"]],
      ["ADD", "agent-authorisation-api.1.0", "", "_control", "_userId"],
      ["COPY", ["agent-authorisation-api.1.0", "", "_control", "_userId"], ["new-agent", "", "json", "userId"]],
      ["ADD", "agent-authorisation-api.1.0", "", "_control", "_password"],
      ["COPY", ["agent-authorisation-api.1.0", "", "_control", "_password"], ["new-agent", "", "json", "password"]],
      ["COPY", ["agent-authorisation-api.1.0", "", "json", "", "clientId"], ["new-mtdit-user", "", "json", "nino"]],
      ["COPY", ["agent-authorisation-api.1.0", "", "json", "", "knownFact"], ["new-mtdit-user", "", "json", "individualDetails", "address", "postcode"]],
      ["SUBMIT", "agent-authorisation-api.1.0", "agent-auth-req"],
      ["GOTO", "accept request", ["agent-auth-req", "", "_control", "_response"], "204"]
    ]
  },

  "accept request": {
    "include": "tests/example/agent-authorisation-test-support-api.1.0._agent-authorisation-test-support_invitations_{invitationId}-put.example.py",
    "press": [
      ["GENSHEET", "agent-authorisation-test-support-api.1.0"],
      ["COPY", ["agent-authorisation-test-support-api.1.0", "", "_parameters", "invitationId"], ["agent-auth-req", "", "_parameters", "Location"], "value.split('/')[-1]"],
      ["SUBMIT", "agent-authorisation-test-support-api.1.0", "agent-auth-response"],
      ["GOTO", "tax-calc", ["agent-auth-response", "", "_control", "_response"], "204"]
    ]
  },

  "tax-calc": {
    "include": "tests/example/individual-calculations-api.8.0._individuals_calculations_{nino}_self-assessment_{taxYear}_{calculationId}-get.example.py",
    "press": [
      ["GENSHEET", "individual-calculations-api.8.0"],
      ["COPY", ["individual-calculations-api.8.0", "", "_parameters", "nino"], ["new-mtdit-user", "", "json", "nino"]],
      ["ADD", "individual-calculations-api.8.0", "", "_control", "arn"],
      ["COPY", ["individual-calculations-api.8.0", "", "_control", "arn"], ["new-agent", "", "json", "agentServicesAccountNumber"]],
      ["COPY", ["individual-calculations-api.8.0", "", "_control", "_username"], ["new-agent", "", "json", "userId"]],
      ["ADD", "individual-calculations-api.8.0", "", "_control", "_userId"],
      ["COPY", ["individual-calculations-api.8.0", "", "_control", "_userId"], ["new-agent", "", "json", "userId"]],
      ["ADD", "individual-calculations-api.8.0", "", "_control", "_password"],
      ["COPY", ["individual-calculations-api.8.0", "", "_control", "_password"], ["new-agent", "", "json", "password"]],
      ["EDIT", "individual-calculations-api.8.0", "", "_parameters", "taxYear", "2026-27"],
      ["ADD", "individual-calculations-api.8.0", "", "_parameters", "Gov-Test-Scenario"],
      ["EDIT", "individual-calculations-api.8.0", "", "_parameters", "Gov-Test-Scenario", "DYNAMIC"],
      ["SUBMIT", "individual-calculations-api.8.0", "sheet-tax-calc"],
      ["VALIDATE", ["sheet-tax-calc", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-tax-calc", "", "json"], "TY 2026-27 onwards-3"],
      ["VALIDATE", ["sheet-tax-calc", "", "json", "", "inputs", "personalInformation", "studentLoanPlan", "0", "", "planType"], "plan1"],
      ["VALIDATE", ["sheet-tax-calc", "", "json", "", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-tax-calc", "", "json", "", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-tax-calc", "", "json", "", "calculation", "endOfYearEstimate", "totalAllowancesAndDeductions"], 5311],
      ["VALIDATE", ["sheet-tax-calc", "", "json", "", "inputs", "constructionIndustryScheme", "0", "", "periodData", "0", "", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  }
}
