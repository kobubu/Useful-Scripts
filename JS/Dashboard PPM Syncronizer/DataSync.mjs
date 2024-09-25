import { DashboardDataHandler } from './DashboardDataHandler.mjs'; 
import { DataUtils } from './DataUtils.mjs';
import { COLUMN_MAPPING, COLUMN_TYPES, SpreadsheetId } from './Const.mjs'; 
import { GoogleSheetsDataHandler } from './GoogleSheetsDataHandler.mjs';

class DataSync {
  constructor() {
    this.googleSheetsDataHandler = new GoogleSheetsDataHandler(SpreadsheetId);
    this.dashboardDataHandler = new DashboardDataHandler();
  }

  async exportDataToDashboard(sheetName, target) {
    try {
      const fetchedData = await this.googleSheetsDataHandler.fetchData(sheetName);
      console.log('Data fetched from Google Sheets:', fetchedData);
      
      const preparedData = this.prepareData(fetchedData, target);
      console.log('Data prepared by DataSync:', preparedData);
      
      const mappedData = this.dashboardDataHandler.mapRecords(preparedData);
      console.log('Data mapped by DashboardHandler:', mappedData);

      if(target == "translators"){
        await this.dashboardDataHandler.addTranslatorsRecords(mappedData);
      } else {
        await this.dashboardDataHandler.addEditorsRecords(mappedData);
      }

    } catch (error) {
      console.error(`An error occurred: ${error.message}`);
    }
  }

  prepareData(data, target) {
    if (target === "translators") {
      return this.prepareTranslatorsData(data);
    } else {
      return this.prepareEditorsData(data);
    }
  }

  prepareTranslatorsData(data) {
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
      return record['Сорс'] && record['Таргет'] && record['Имя в QH/дэшборде'] && record['PPM'];
    });

    // Убеждаемся, что нет дубликатов translator_name для одного и того же target_language
    const uniqueRecords = [];
    const seen = new Set();

    records.forEach(record => {
      const key = `${record['Сорс']} ${record['Таргет']}-${record['Имя в QH/дэшборде']}`;
      if (!seen.has(key)) {
        seen.add(key);
        uniqueRecords.push(record);
      }
    });

    console.log('Prepared records:', uniqueRecords);
    return uniqueRecords;
  }

  prepareEditorsData(data) {
    const headers = data[0];
    console.log('Headers from Google Sheets:', headers);
  
    const records = data.slice(1).map(row => {
      const record = {};
      headers.forEach((header, index) => {
        const columnType = COLUMN_TYPES[COLUMN_MAPPING[header]];
        record[header] = DataUtils.convertValue(row[index], columnType);
      });
      return record;
    }).filter(record => {
      // Преобразуем значения в проценты, если они являются строками с процентами или числами
      const precision = typeof record['Precision'] === 'string' && record['Precision'].includes('%')
        ? parseFloat(record['Precision'].replace(/,/g, '.').replace('%', '')) / 100
        : typeof record['Precision'] === 'number'
        ? record['Precision'] / 100
        : NaN;

      const recall = typeof record['Recall'] === 'string' && record['Recall'].includes('%')
        ? parseFloat(record['Recall'].replace(/,/g, '.').replace('%', '')) / 100
        : typeof record['Recall'] === 'number'
        ? record['Recall'] / 100
        : NaN;

      const fScore = typeof record['F-score'] === 'string' && record['F-score'].includes('%')
        ? parseFloat(record['F-score'].replace(/,/g, '.').replace('%', '')) / 100
        : typeof record['F-score'] === 'number'
        ? record['F-score'] / 100
        : NaN;

      // Проверяем, что все необходимые поля заполнены и не являются пустыми строками
      const isValid = record['Сорс'] && record['Таргет'] && record['Имя редактора в QH/дэшборде'] &&
        !isNaN(precision) && !isNaN(recall) && !isNaN(fScore) && record['Штат/фриланс'] != 'Штат';

      if (!isValid) {
        console.log('Filtered out record:', record);
        console.log('Precision:', precision);
        console.log('Recall:', recall);
        console.log('F-score:', fScore);
      }

      return isValid;
    });

    // Убеждаемся, что нет дубликатов translator_name для одного и того же target_language
    const uniqueRecords = [];
    const seen = new Set();

    records.forEach(record => {
      const key = `${record['Сорс']}${record['Таргет']}-${record['Имя в QH/дэшборде']}`;
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