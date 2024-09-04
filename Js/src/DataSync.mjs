//path DataSync.mjs
import { DashboardDataHandler } from './DashboardDataHandler.mjs'; 
import { DataUtils } from './DataUtils.mjs';
import { COLUMN_MAPPING, COLUMN_TYPES } from './Const.mjs'; 
import { GoogleSheetsDataHandler } from './GoogleSheetsDataHandler.mjs';

class DataSync {
  constructor(spreadsheetId, sheetName) {
    this.googleSheetsDataHandler = new GoogleSheetsDataHandler(spreadsheetId, sheetName);
    this.dashboardDataHandler = new DashboardDataHandler();
  }

  async exportDataToDashboard() {
    try {
      const googleSheetsData = await this.googleSheetsDataHandler.fetchData();
      console.log('Data fetched from Google Sheets:', googleSheetsData);

      const preparedData = this.prepareData(googleSheetsData);
      console.log('Data prepared by DataSync:', preparedData);

      const mappedData = this.dashboardDataHandler.mapRecords(preparedData);
      console.log('Data mapped by DashboardHandler:', mappedData);

      await this.dashboardDataHandler.addRecords(mappedData);

    } catch (error) {
      console.error(`An error occurred: ${error.message}`);
    }
  }

  prepareData(data) {
    const headers = data[0];
    console.log('Headers from Google Sheets:', headers);

    const records = data.slice(1).map(row => {
      const record = {};
      headers.forEach((header, index) => {
        record[header] = DataUtils.convertValue(row[index], COLUMN_TYPES[COLUMN_MAPPING[header]]);
      });
      return record;
    }).filter(record => {
      // Отсекаем пустые значения
      return record['Таргет'] && record['Имя в QH/дэшборде'] && record['PPM'];
    });

    // Убеждаемся, что нет дубликатов translator_name для одного и того же target_language
    const uniqueRecords = [];
    const seen = new Set();

    records.forEach(record => {
      const key = `${record['Таргет']}-${record['Имя в QH/дэшборде']}`;
      if (!seen.has(key)) {
        seen.add(key);
        uniqueRecords.push(record);
      }
    });

    console.log('Prepared records:', uniqueRecords);
    return uniqueRecords;
  }
}

export { DataSync };