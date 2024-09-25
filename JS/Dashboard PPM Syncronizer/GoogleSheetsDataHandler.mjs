import { google } from 'googleapis';
import { authenticate } from '@google-cloud/local-auth';
import { credentialsPath } from './Const.mjs';

class GoogleSheetsDataHandler {
  constructor(spreadsheetId) {
    this.spreadsheetId = spreadsheetId;
    this.client = null;
  }

  async fetchData(sheetName) {
    const range = `${sheetName}!A1:Z1000`; // изменить диапазон по мере необходимости
    const data = await this.getSheetData(this.spreadsheetId, range);
    console.log('Fetched data from Google Sheets:', data);
    return data;
  }

  toString() {
    return `GoogleSheetsDataHandler(spreadsheetId: ${this.spreadsheetId})`;
  }

  async getSheetData(spreadsheetId, range) {
    // Авторизация
    if (!this.client) {
      this.client = await authenticate({
        keyfilePath: credentialsPath,
        scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
      });
    }

    // Создание объекта для взаимодействия с Google Sheets API
    const sheets = google.sheets({ version: 'v4', auth: this.client });

    // Получение данных из таблицы
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range,
    });

    return response.data.values;
  }
}

export { GoogleSheetsDataHandler };