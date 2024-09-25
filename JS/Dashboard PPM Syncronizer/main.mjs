import { DataSync } from './DataSync.mjs'; 
import { translatorsDataSheetName, editorsDataSheetName } from './Const.mjs'; 
import readline from 'readline';

async function main() {
  try {
    const dataSync = new DataSync();
    await dataSync.exportDataToDashboard(translatorsDataSheetName, 'translators');
    await dataSync.exportDataToDashboard(editorsDataSheetName, 'editors');
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