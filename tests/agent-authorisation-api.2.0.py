{
  "description": "Test individuals-capital-gains-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "Link mtdit user 0 to agent 0 as main agent": {
    "include": "tests/agent-authorisation-api/agent-authorisation-0.2.0.py"
  },

  "MTD-VAT full workflow": {
    "include": "tests/agent-authorisation-api/agent-authorisation-mtdvat.2.0.py"
  },

  "MTD-IT full workflow": {
    "include": "tests/agent-authorisation-api/agent-authorisation-mtdit.2.0.py"
  },

  "START": {
    "press": [
# Stateful tests
      ["CALL", "Link mtdit user 0 to agent 0 as main agent"],
      ["CALL", "MTD-IT full workflow"],
      ["CALL", "MTD-VAT full workflow"],

      ["GOTO", "END"]
    ]
  }
}

