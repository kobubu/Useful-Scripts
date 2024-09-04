// FilePath: Main.mjs
import { DataSync } from './DataSync.mjs'; 
import { spreadsheetId, vendorsDataSheetName } from './Const.mjs'; 
import readline from 'readline';

async function main() {
  try {
    const dataSync = new DataSync(spreadsheetId, vendorsDataSheetName);
    await dataSync.exportDataToDashboard();
  } catch (error) {
    console.error('Произошла ошибка:', error);
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.question('Press ENTER to exit...', (answer) => {
    rl.close();
  });
}

main();