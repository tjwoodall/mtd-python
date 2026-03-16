{
  "description": "This creates a new agent, a new mtdvat user, gets agent authorisation and then the agent requests the business vat details",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",
  "include": ["tests/include/create-mtdvat-user.py", "tests/include/create-agent.py"],

  "START": {
    "press": [
      ["GOSUB", "Create a new test mtdvat user on sheet new-mtdvat-user"],
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
      ["EDIT", "agent-authorisation-api.1.0", "", "json", "Agent Invitation Request for VAT-1"],
      ["COPY", ["agent-authorisation-api.1.0", "", "json", "", "clientId"], ["new-mtdvat-user", "", "json", "vrn"]],
      ["COPY", ["agent-authorisation-api.1.0", "", "json", "", "knownFact"], ["new-mtdvat-user", "", "json", "vatRegistrationDate"]],
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
      ["GOTO", "vat-info", ["agent-auth-response", "", "_control", "_response"], "204"]
    ]
  },

  "vat-info": {
    "include": "tests/example/vat-api.1.0._organisations_vat_{vrn}_information-get.example.py",
    "press": [
      ["GENSHEET", "vat-api.1.0"],
      ["COPY", ["vat-api.1.0", "", "_parameters", "vrn"], ["new-mtdvat-user", "", "json", "vrn"]],
      ["ADD", "vat-api.1.0", "", "_control", "arn"],
      ["COPY", ["vat-api.1.0", "", "_control", "arn"], ["new-agent", "", "json", "agentServicesAccountNumber"]],
      ["COPY", ["vat-api.1.0", "", "_control", "_username"], ["new-agent", "", "json", "userId"]],
      ["ADD", "vat-api.1.0", "", "_control", "_userId"],
      ["COPY", ["vat-api.1.0", "", "_control", "_userId"], ["new-agent", "", "json", "userId"]],
      ["ADD", "vat-api.1.0", "", "_control", "_password"],
      ["COPY", ["vat-api.1.0", "", "_control", "_password"], ["new-agent", "", "json", "password"]],
      ["SUBMIT", "vat-api.1.0", "sheet-vat"],
      ["VALIDATE", ["sheet-vat", "", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-vat", "", "json", "customerDetails", "effectiveRegistrationDate"], "2018-03-04"],
      ["GOTO", "END"]
    ]
  }
}
