import path from 'path';

const SpreadsheetId = '1eWMY77jHrw4ruCbKQ86Yv3f7Nbc3JPXmFlriKy50wzA';
const translatorsDataSheetName = 'По переводчикам';
const editorsDataSheetName ='Редакторы';
const credentialsPath = path.join(process.cwd(), 'client_secret_1064250263292_f6tc4th0pcmji86dsqd5fs9gn5desrso_apps.json');
const DASHBOARD_TRANSLATORS_API_URL = 'https://dashboard.inlingo.local/api/ratings/vendor/ppm_update';
const DASHBOARD_EDITORS_API_URL = 'https://dashboard.inlingo.local/api/ratings/editor/stats_data';


const COLUMN_TYPES = {
  'source_language': 'string',
  'target_language': 'string',
  'translator_name': 'string',
  'PPM': 'number',
  'precision_score': 'number',
  'recall_score': 'number',
  'f_score': 'number'
};

const COLUMN_MAPPING = {
  'Сорс': 'source_language',
  'Таргет': 'target_language',
  'Имя в QH/дэшборде': 'translator_name',
  'Имя редактора в QH/дэшборде': 'editor_name',
  'PPM': 'PPM',
  'Precision': 'precision_score',
  'Recall': 'recall_score',
  'F-score': 'f_score'
};


const LANGUAGE_MAPPING = {
  'Arabic [AR]': 'ARB',
  'Chinese (Simplified) [ZH]': 'ZH-CN',
  'Chinese (Traditional) [ZH-TW]': 'ZH-TW',
  'Czech [CS]': 'CS',
  'Danish [DA]': 'DA',
  'Dutch [NL]': 'NL',
  'English [EN]': 'ENG',
  'French (Canada) [FR-CA]': 'FR-CA',
  'French [FR]': 'FR',
  'German [DE]': 'DE',
  'Indonesian [ID]': 'IN',
  'Italian [IT]': 'IT',
  'Japanese [JA]': 'JA',
  'Korean [KO]': 'KO',
  'Norwegian [NO]': 'NO-NO',
  'Polish [PL]': 'PL',
  'Portuguese (Brazil) [PT-BR]': 'PT-BR',
  'Portuguese (Portugal) [PT]': 'PT',
  'Russian [RU]': 'RU',
  'Spanish (Latin America) [ES-LA]': 'ES-XL',
  'Spanish (Mexico) [ES-MX]': 'ES-MX',
  'Spanish [ES]': 'ES',
  'Swedish [SV]': 'SV',
  'Thai [TH]': 'TH',
  'Turkish [TR]': 'TR',
  'Ukrainian [UK]': 'UK',
  'Vietnamese [VI]': 'VI'
};

export { SpreadsheetId, translatorsDataSheetName, editorsDataSheetName, credentialsPath,
   DASHBOARD_TRANSLATORS_API_URL, DASHBOARD_EDITORS_API_URL, COLUMN_MAPPING, COLUMN_TYPES, LANGUAGE_MAPPING 
};