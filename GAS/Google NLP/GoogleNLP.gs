function analyzeText(text, language) {
  if (!text || text.trim() === "") return null;

  var url = "https://language.googleapis.com/v2/documents:annotateText";
  var payload = {
    "document": {
      "type": "PLAIN_TEXT",
      "content": text,
      "languageCode": language
    },
    "features": {
      "extractEntities": true,
      "extractDocumentSentiment": true,
      "classifyText": true,
      "extractEntitySentiment": true,
      "moderateText": true
    },
    "encodingType": "UTF8"
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "headers": { "Authorization": "Bearer " + ScriptApp.getOAuthToken() },
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    return response.getResponseCode() === 200 ? JSON.parse(response.getContentText()) : null;
  } catch (e) {
    Logger.log("Ошибка API: " + e.toString());
    return null;
  }
}

function processSheet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var language = "fr";
  var resultStartColumn = 12; // Столбец, с которого начинаем записывать анализ
  var maxEmptyRows = 5;
  var emptyRowCount = 0;
  var maxAnalysisColumns = 6; // Максимальное количество колонок для анализа

  // Опасные категории
  var dangerousCategories = [
    "Toxic", "Insult", "Profanity", "Derogatory", "Sexual", "Death, Harm & Tragedy",
    "Violent", "Firearms & Weapons", "Religion & Belief", "Illicit Drugs", "War & Conflict", "Politics"
  ];

  Logger.log("Начало обработки таблицы. Всего строк: " + (data.length - 1));

  // Создаем заголовки один раз перед циклом
  for (var j = 0; j < maxAnalysisColumns; j++) {
    sheet.getRange(1, resultStartColumn + j).setValue("Analysis " + (j + 1));
  }

  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    var words = row[1] ? row[1].split(/\s+/) : [];
    var tips = row[2] ? row[2].split(/\s+/) : [];
    
    if (words.length === 0 && tips.length === 0) {
      emptyRowCount++;
      if (emptyRowCount >= maxEmptyRows) {
        Logger.log("Прерываем из-за " + maxEmptyRows + " пустых строк подряд.");
        break;
      }
      continue;
    } else {
      emptyRowCount = 0;
    }

    var currentColumn = resultStartColumn;

    Logger.log("Обрабатываем строку " + (i + 1));
    
    var analysisResults = [];

    // Анализируем #Word
    for (var j = 0; j < words.length; j++) {
      var word = words[j].trim();
      if (!word) continue;

      Logger.log("Анализируем слово: " + word);
      var result = analyzeText(word, language);

      if (result) {
        var sentimentScore = result.documentSentiment ? result.documentSentiment.score : null;
        var moderationCategories = result.moderationCategories || [];

        // Опасные категории с confidence > 0.1
        var filteredCategories = [];
        for (var k = 0; k < moderationCategories.length; k++) {
          var cat = moderationCategories[k];
          if (dangerousCategories.indexOf(cat.name) !== -1 && cat.confidence > 0.1) {
            filteredCategories.push(cat.name + " (" + cat.confidence.toFixed(3) + ")");
          }
        }

        var moderation = filteredCategories.length > 0;

        // Фильтруем: только если Sentiment Score <= -0.2 или есть опасные категории
        if (sentimentScore <= -0.2 || moderation) {
          var analysisParts = [word];

          if (sentimentScore !== null) {
            analysisParts.push("Sentiment Score " + sentimentScore.toFixed(3));
          }
          if (filteredCategories.length > 0) {
            analysisParts.push(filteredCategories.join(", "));
          }

          var analysisText = analysisParts.join("\n");

          // Добавляем результат в список анализов
          analysisResults.push(analysisText);
        }
      }

      Utilities.sleep(500); // Чтобы не перегружать API
    }

    // Анализируем #Tips
    for (var j = 0; j < tips.length; j++) {
      var tip = tips[j].trim();
      if (!tip) continue;

      Logger.log("Анализируем совет: " + tip);
      var result = analyzeText(tip, language);

      if (result) {
        var sentimentScore = result.documentSentiment ? result.documentSentiment.score : null;
        var moderationCategories = result.moderationCategories || [];

        // Опасные категории с confidence > 0.1
        var filteredCategories = [];
        for (var k = 0; k < moderationCategories.length; k++) {
          var cat = moderationCategories[k];
          if (dangerousCategories.indexOf(cat.name) !== -1 && cat.confidence > 0.15) {
            filteredCategories.push(cat.name + " (" + cat.confidence.toFixed(3) + ")");
          }
        }

        var moderation = filteredCategories.length > 0;

        // Фильтруем: только если Sentiment Score <= -0.2 или есть опасные категории
        if (sentimentScore <= -0.2 || moderation) {
          var analysisParts = [tip];

          if (sentimentScore !== null) {
            analysisParts.push("Sentiment Score " + sentimentScore.toFixed(3));
          }
          if (filteredCategories.length > 0) {
            analysisParts.push(filteredCategories.join(", "));
          }

          var analysisText = analysisParts.join("\n");

          // Добавляем результат в список анализов
          analysisResults.push(analysisText);
        }
      }

      Utilities.sleep(500);
    }

    // Ограничиваем количество колонок анализов
    analysisResults = analysisResults.slice(0, maxAnalysisColumns);

    // Записываем результаты в соответствующие колонки
    for (var j = 0; j < analysisResults.length; j++) {
      sheet.getRange(i + 1, resultStartColumn + j).setValue(analysisResults[j]);
      sheet.getRange(i + 1, resultStartColumn + j).setWrap(true);
      sheet.autoResizeColumn(resultStartColumn + j);
    }
  }

  Logger.log("Обработка завершена.");
}





function formatAnalysis(word, result, dangerousCategories) {
  if (!result) return null;

  var sentimentScore = result.documentSentiment ? result.documentSentiment.score : null;
  var moderationCategories = result.moderationCategories || [];
  var entities = result.entities || [];

 var isProperNoun = false;

for (var i = 0; i < entities.length; i++) {
  if (entities[i].mentions) {
    for (var j = 0; j < entities[i].mentions.length; j++) {
      if (entities[i].mentions[j].type === "PROPER") {
        isProperNoun = true;
        break;
      }
    }
  }
  if (isProperNoun) break;
}

  // Опасные категории с confidence > 0.1
var filteredCategories = [];
for (var i = 0; i < moderationCategories.length; i++) {
  var cat = moderationCategories[i];
  if (dangerousCategories.indexOf(cat.name) !== -1 && cat.confidence > 0.1) {
    filteredCategories.push(cat.name + " (" + cat.confidence.toFixed(3) + ")");
  }
}

var moderation = filteredCategories.length > 0;

// Фильтруем: только если Sentiment Score <= -0.2 или есть опасные категории или Proper Noun
if (sentimentScore <= -0.2 || moderation || isProperNoun) {
  var analysisParts = [word];

  if (sentimentScore !== null) {
    analysisParts.push("Sentiment Score " + sentimentScore.toFixed(3));
  }
  if (filteredCategories.length > 0) {
    analysisParts.push(filteredCategories.join(", "));
  }

  return analysisParts.join("\n");
}

  return null;
}


function deleteAllImages() {
  // Получаем активный лист
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Получаем все изображения на листе
  var images = sheet.getDrawings();

  // Перебираем все изображения и удаляем их
  for (var i = 0; i < images.length; i++) {
    sheet.removeDrawing(images[i]);
  }

  Logger.log("Удалено " + images.length + " изображений.");
}

function deleteAllOverlaidImages() {
  // Получаем активный лист
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Очищаем весь лист (включая изображения и другие объекты)
  sheet.clear();

  Logger.log("Все объекты, включая изображения, удалены с листа: " + sheet.getName());
}
