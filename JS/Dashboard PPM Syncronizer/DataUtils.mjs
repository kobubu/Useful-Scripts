class DataUtils {
  static convertValue(value, expectedType) {
    if (expectedType === 'string') {
      return value !== null && value !== undefined ? String(value) : '';
    } else if (expectedType === 'number') {
      if (typeof value === 'string') {
        // Заменяем запятые на точки и удаляем проценты, если они есть
        value = value.replace(/,/g, '.').replace(/%/g, '');
        // Пытаемся преобразовать строку в число
        const numberValue = Number(value);
        if (!isNaN(numberValue)) {
          return numberValue;
        } else {
          console.error(`Failed to convert value "${value}" to number`);
          return NaN;
        }
      } else if (typeof value === 'number') {
        return value;
      } else {
        console.error(`Value "${value}" is not a string or number`);
        return NaN;
      }
    }
    return value;
  }
}

export { DataUtils };