//path Const.mjs
import path from 'path';

const spreadsheetId = 'Placeholder';
const vendorsDataSheetName = 'Placeholder';
const credentialsPath = path.join(process.cwd(), 'Placeholder.json');
const DASHBOARD_API_URL = 'Placeholder';

const COLUMN_MAPPING = {
  'Таргет': 'target_language',
  'Имя в QH/дэшборде': 'translator_name',
  'PPM': 'PPM'
};

const COLUMN_TYPES = {
  'target_language': 'string',
  'translator_name': 'string',
  'PPM': 'number'
};

export { spreadsheetId, vendorsDataSheetName, credentialsPath, DASHBOARD_API_URL, COLUMN_MAPPING, COLUMN_TYPES };