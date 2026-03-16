{
  "press": [
    ["CALL", "Get test mtdit user", "mtdit-user-0"],
    ["GOTO", "run"]
  ],

  "run": {
    "setup": { "include": "tests/example/individual-calculations-api.8.0._individuals_calculations_{nino}_self-assessment_{taxYear}_{calculationId}-get.example.py", },
    "press": [
      ["CALL", "setup"],
      ["GENSHEET", "sheet._$0_"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],
      ["COPY", ["sheet._$0_", "_control", "_username"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_userId"]],
      ["COPY", ["sheet._$0_", "_control", "_userId"], ["mtdit-user-0", "json", "userId"]],
      ["ADD", ["sheet._$0_", "_control", "_password"]],
      ["COPY", ["sheet._$0_", "_control", "_password"], ["mtdit-user-0", "json", "password"]],

      ["EDIT", ["sheet._$0_", "_parameters", "taxYear"], "2023-24"],
      ["CALL", "CannedResponse", "sheet._$0_"],

      ["EDIT", ["sheet._$0_", "_parameters", "taxYear"], "2025"],
      ["CALL", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_TAX_YEAR", "The provided tax year format is invalid"],
      ["EDIT", ["sheet._$0_", "_parameters", "taxYear"], "2023-24"],

      ["EDIT", ["sheet._$0_", "_parameters", "nino"], "ANINO"],
      ["CALL", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_NINO", "The NINO format is invalid"],
      ["COPY", ["sheet._$0_", "_parameters", "nino"], ["mtdit-user-0", "json", "nino"]],

      ["EDIT", ["sheet._$0_", "_parameters", "calculationId"], "f2fb30e5-4ab6-4a29-b3c1-c7264259ff1Z"],
      ["CALL", "ErrorChecker2", "sheet._$0_", "DUMMY", "400", "FORMAT_CALCULATION_ID", "The provided calculation ID is invalid"],
      ["EDIT", ["sheet._$0_", "_parameters", "calculationId"], "f2fb30e5-4ab6-4a29-b3c1-c7264259ff1c"],

      ["NOTE: DYNAMIC seems to make no difference here"],
      ["ADD", ["sheet._$0_", "_parameters", "Gov-Test-Scenario"]],
      ["EDIT", ["sheet._$0_", "_parameters", "Gov-Test-Scenario"], "DYNAMIC"],

      ["CALL", "CannedResponse-2023-24", "sheet._$0_"],
      ["CALL", "CannedResponse-2024-25", "sheet._$0_"],
      ["CALL", "CannedResponse-2025-26", "sheet._$0_"],
      ["CALL", "CannedResponse-2026-27", "sheet._$0_"],
      ["CALL", "CannedResponse-2027-28", "sheet._$0_"],

      ["CALL", "CannedResponseScenario", "sheet._$0_", "ERROR_MESSAGES_EXIST"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_MULTIPLE_INCOMES_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_PROP_DIVIDENDS_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_PROP_GIFTAID_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_PROP_SAVINGS_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_SE_GIFTAID_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "UK_SE_SAVINGS_EXAMPLE"],
      ["CALL", "CannedResponseScenario", "sheet._$0_", "SCOT_SE_DIVIDENDS_EXAMPLE"],

      ["CALL", "ErrorChecker", "sheet._$0_", "NOT_FOUND", "404", "MATCHING_RESOURCE_NOT_FOUND", "Matching resource not found"],

      ["GOTO", "END"]
    ]
  },

  "CannedResponse": {
    "press": [
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2023-24 or before-0"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponseScenario": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2026-27"],
      ["EDIT", ["_$1_", "_parameters", "Gov-Test-Scenario"], "_$2_"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2025-26-2"],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse-2023-24": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2023-24"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2023-24 or before-0"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculation", "lossesAndClaims", "defaultCarriedForwardLosses", "0", "currentLossValue"], 12500],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse-2024-25": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2024-25"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2024-25-1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculation", "transitionProfit", "transitionProfitDetail", "0", "transitionProfitsAfterIncomeTaxLossDeductions"], 2000],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse-2025-26": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2025-26"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2025-26-2"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculation", "transitionProfit", "transitionProfitDetail", "0", "transitionProfitsAfterIncomeTaxLossDeductions"], 2000],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse-2026-27": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2026-27"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2026-27 onwards-3"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculation", "endOfYearEstimate", "totalAllowancesAndDeductions"], 5311],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "CannedResponse-2027-28": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "taxYear"], "2027-28"],
      ["SUBMIT", "_$1_", "sheet-info._$0_"],
      ["VALIDATE", ["sheet-info._$0_", "_control", "_response"], "200"],
      ["VALIDATE", ["sheet-info._$0_", "json"], "TY 2026-27 onwards-3"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "studentLoanPlan", "0", "planType"], "plan1"],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "class2VoluntaryContributions"], True],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "personalInformation", "uniqueTaxpayerReference"], "1234567890"],
      ["VALIDATE", ["sheet-info._$0_", "json", "calculation", "endOfYearEstimate", "totalAllowancesAndDeductions"], 5311],
      ["VALIDATE", ["sheet-info._$0_", "json", "inputs", "constructionIndustryScheme", "0", "periodData", "0", "deductionAmount"], 5000.99],
      ["GOTO", "END"]
    ]
  },

  "ErrorChecker": {
    "press": [
      ["EDIT", ["_$1_", "_parameters", "Gov-Test-Scenario"], "_$2_"],
      ["GOTO", "ErrorChecker2"]
    ]
  },

  "ErrorChecker2": {
    "press": [
      ["SUBMIT", "_$1_", "response._$0_"],
      ["VALIDATE", ["response._$0_", "_control", "_response"], "_$3_"],
      ["VALIDATE", ["response._$0_", "json", "code"], "_$4_"],
      ["VALIDATE", ["response._$0_", "json", "message"], "_$5_"],
      ["GOTO", "END"]
    ]
  }
}
