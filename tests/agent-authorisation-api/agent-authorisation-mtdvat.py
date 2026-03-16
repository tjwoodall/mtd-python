{
  "include": ["tests/include/create-mtdvat-user.py", "tests/include/create-agent.py"],

  "press": [
    ["GOSUB", "Create a new test mtdvat user on sheet new-mtdvat-user"],
    ["GOSUB", "Create a new test agent on sheet new-agent"],
    ["GOSUB", "Create Request"],
    ["GOSUB", "Accept Request"],
    ["GOSUB", "Agent Request for user"],
    ["GOTO", "END"]
  ],

  "Create Request": {
    "setup": { "include": "tests/example/agent-authorisation-api.1.0._agents_{arn}_invitations-post.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "arn"], ["new-agent", "json", "agentServicesAccountNumber"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["new-agent", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["new-agent", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["new-agent", "json", "password"]],
      ["EDIT", "sheet._$0_", "json", "Agent Invitation Request for VAT-1"],
      ["COPY", ["sheet._$0_", "json", "clientId"], ["new-mtdvat-user", "json", "vrn"]],
      ["COPY", ["sheet._$0_", "json", "knownFact"], ["new-mtdvat-user", "json", "vatRegistrationDate"]],
      ["SUBMIT", "sheet._$0_", "agent-auth-req"],
      ["GOTO", "END", ["agent-auth-req", "_control", "_response"], "204"],
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

  "Agent Request for user": {
    "setup": { "include": "tests/example/vat-api.1.0._organisations_vat_{vrn}_information-get.example.py" },
    "press": [
      ["GOSUB", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "vrn"], ["new-mtdvat-user", "json", "vrn"]],
      ["ADD", "sheet._$0_", "_control", "arn"],
      ["COPY", ["sheet._$0_", "_control", "arn"], ["new-agent", "json", "agentServicesAccountNumber"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["new-agent", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_userId"],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["new-agent", "json", "userId"]],
      ["ADD", "sheet._$0_", "_control", "_password"],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["new-agent", "json", "password"]],
      ["SUBMIT", "sheet._$0_", "sheet-vat"],
      ["VALIDATE", ["sheet-vat", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-vat", "json", "customerDetails", "effectiveRegistrationDate"], "2018-03-04"],
      ["GOTO", "END"]
    ]
  },
}
