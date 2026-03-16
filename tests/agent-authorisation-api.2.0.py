{
  "description": "Test individuals-capital-gains-income-api STATEFUL requests",
  "schema": "artifacts/webscrape.json",
  "config": "tests/test.db",

  "Link mtdit user 0 to agent 0 as main agent": {
    "include": "tests/agent-authorisation-api/agent-authorisation-0.py"
  },

  "MTD-VAT full workflow": {
    "include": "tests/agent-authorisation-api/agent-authorisation-mtdvat.py"
  },

  "MTD-IT full workflow": {
    "include": "tests/agent-authorisation-api/agent-authorisation-mtdit.py"
  },

  "START": {
    "press": [
# Stateful tests
      ["GOSUB", "Link mtdit user 0 to agent 0 as main agent"],
      ["GOSUB", "MTD-IT full workflow"],
      ["GOSUB", "MTD-VAT full workflow"],

      ["GOTO", "END"]
    ]
  }
}

