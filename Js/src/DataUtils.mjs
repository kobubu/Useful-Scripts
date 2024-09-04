//path DataUtils.mjs
class DataUtils {
    static convertValue(value, expectedType) {
      if (expectedType === 'string') {
        return value !== null && value !== undefined ? String(value) : '';
      } else if (expectedType === 'number') {
        return value !== null && value !== undefined ? Number(value) : 0;
      }
      return value;
    }
  }
  
  export { DataUtils };