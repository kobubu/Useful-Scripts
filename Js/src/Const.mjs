//path Const.mjs
import path from 'path';

const spreadsheetId = '1eWMY77jHrw4ruCbKQ86Yv3f7Nbc3JPXmFlriKy50wzA';
const vendorsDataSheetName = 'По переводчикам';
const credentialsPath = path.join(process.cwd(), 'client_secret_1064250263292_f6tc4th0pcmji86dsqd5fs9gn5desrso_apps.json');
const DASHBOARD_API_URL = 'https://dashboard.inlingo.local/api/ratings/vendor/ppm_update';

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