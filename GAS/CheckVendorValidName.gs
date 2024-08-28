function CheckVendorValidName(value) {

var ss = SpreadsheetApp.getActiveSpreadsheet();
var vendorsValidNamesSheet = "Vendors names in dashboard"
var sheet = ss.getSheetByName(vendorsValidNamesSheet);

if (!sheet) {
  Logger.log("Лист с именем "+ vendorsValidNamesSheet +" не найден")
} 

var vendorsValidNames = sheet.getRange("B2:B2105").getValues();

for(var i=0; i < vendorsValidNames.length; i++) {
  if (vendorsValidNames[i][0] === value)
  return true;
}

return false;
}
