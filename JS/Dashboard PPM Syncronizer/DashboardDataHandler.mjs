//path DashboardDataHandler.mjs
import { COLUMN_MAPPING, DASHBOARD_API_URL } from './Const.mjs';
import { NetworkHandler } from './NetworkHandler.mjs';

class DashboardDataHandler {
  mapRecords(records) {
    const headers = Object.keys(COLUMN_MAPPING);
    const dataToWrite = records.map(record => {
      const row = {};
      headers.forEach(header => {
        row[COLUMN_MAPPING[header]] = record[header];
      });
      return row;
    });
    console.log('Mapped Google Sheet Records for Writing:', JSON.stringify(dataToWrite, null, 2));
    return dataToWrite;
  }

  async addRecords(records) {
    const url = `${DASHBOARD_API_URL}`;
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ translators: records })
    };

    console.log('Sending request to:', url);
    console.log('Request headers:', JSON.stringify(options.headers, null, 2));
    console.log('Request body:', JSON.stringify({ translators: records }, null, 2));

    try {
      const response = await NetworkHandler.fetchWithRetry(url, options);
      const responseCode = response.status;
      const responseBody = await response.text();

      if (responseCode >= 200 && responseCode < 300) {
        console.log('Records successfully added to Dashboard.');
      } else {
        throw new Error(`Failed to add records to Dashboard. Response code: ${responseCode}, Response body: ${responseBody}`);
      }
    } catch (error) {
      console.error('Error adding records to Dashboard:', error.message);
    }
  }

  toString() {
    return `DashboardHandler(viewId: ${this.viewId})`;
  }
}

export { DashboardDataHandler };