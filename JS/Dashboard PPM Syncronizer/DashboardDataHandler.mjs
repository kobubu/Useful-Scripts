import { COLUMN_MAPPING, LANGUAGE_MAPPING, DASHBOARD_TRANSLATORS_API_URL, DASHBOARD_EDITORS_API_URL } from './Const.mjs';
import { NetworkHandler } from './NetworkHandler.mjs';

class DashboardDataHandler {
  mapRecords(records) {
    const headers = Object.keys(COLUMN_MAPPING);
    const dataToWrite = records.map(record => {
      const row = {};
      headers.forEach(header => {
        row[COLUMN_MAPPING[header]] = record[header];
      });
          // Преобразуем языки в соответствии с LANGUAGE_MAPPING
          if (row['source_language']) {
            row['source_language'] = LANGUAGE_MAPPING[row['source_language']] || row['source_language'];
          }
          if (row['target_language']) {
            row['target_language'] = LANGUAGE_MAPPING[row['target_language']] || row['target_language'];
          }
    
          return row;
        });
    console.log('Mapped Google Sheet Records for Writing:', JSON.stringify(dataToWrite, null, 2));
    return dataToWrite;
  }

  async addTranslatorsRecords(records) {
    const url = `${DASHBOARD_TRANSLATORS_API_URL}`;
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

  async addEditorsRecords(records) {
    const url = `${DASHBOARD_EDITORS_API_URL}`;
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ editors: records })
    };

    console.log('Sending request to:', url);
    console.log('Request headers:', JSON.stringify(options.headers, null, 2));
    console.log('Request body:', JSON.stringify({ editors: records }, null, 2));

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