//path getConfig.mjs
function getConfig() {
    if (!spreadsheetId) {
        throw new Error('Spreadsheet ID is not set in script properties.');
    }
    if (!vendorsDataSheetName) {
        throw new Error('vendorsDataSheetName name is not set in script properties.');
    }
  
    return { spreadsheetId, vendorsDataSheetName };
}