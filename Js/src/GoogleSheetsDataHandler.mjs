//path GoogleSheetsDataHandler.mjs
import { google } from 'googleapis';
import { authenticate } from '@google-cloud/local-auth';
import { credentialsPath } from './Const.mjs';

class GoogleSheetsDataHandler {
  constructor(spreadsheetId, sheetName) {
    this.spreadsheetId = spreadsheetId;
    this.sheetName = sheetName;
  }

  async fetchData() {
    const range = `${this.sheetName}!A1:Z1000`; // изменить диапазон по мере необходимости
    return await this.getSheetData(this.spreadsheetId, range);
  }

  toString() {
    return `GoogleSheetsDataHandler(spreadsheetId: ${this.spreadsheetId}, sheetName: ${this.sheetName})`;
  }

  async getSheetData(spreadsheetId, range) {
    // Авторизация
    const client = await authenticate({
      keyfilePath: credentialsPath,
      scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    });

    // Создание объекта для взаимодействия с Google Sheets API
    const sheets = google.sheets({ version: 'v4', auth: client });

    // Получение данных из таблицы
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range,
    });

    return response.data.values;
  }
}

export { GoogleSheetsDataHandler };