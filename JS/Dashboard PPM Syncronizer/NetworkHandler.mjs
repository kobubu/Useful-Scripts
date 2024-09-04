// path NetworkHandler.mjs
import fetch from 'node-fetch';
import https from 'https';

class NetworkHandler {
  static async fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        console.log(`Attempt ${i + 1} to fetch ${url}`);
        console.log('Request options:', JSON.stringify(options, null, 2));

        const response = await fetch(url, {
          ...options,
          agent: new https.Agent({
            rejectUnauthorized: false
          })
        });

        console.log(`Response status: ${response.status}`);
        console.log('Response headers:', JSON.stringify(response.headers.raw(), null, 2));

        const responseCode = response.status;

        switch (responseCode) {
          case 200:
          case 201:
          case 204:
            return response;
          case 401:
            throw new Error('Unauthorized: Check your API key.');
          case 403:
            throw new Error('Forbidden: You do not have permission to access this resource.');
          case 404:
            throw new Error('Not Found: The requested resource was not found.');
          case 500:
            throw new Error('Internal Server Error: The server encountered an internal error.');
          case 504:
            throw new Error('Bad Gateway: The server was acting as a gateway or proxy and received an invalid response.');
          default:
            throw new Error(`Unexpected response code: ${responseCode}`);
        }
      } catch (e) {
        if (e.message.startsWith('Unauthorized') || e.message.startsWith('Forbidden')) {
          throw e;
        }
        if (e.message.includes('DNS error')) {
          console.log(`DNS error encountered: ${e.message}. Retrying...`);
        }
        if (i === maxRetries - 1) {
          console.log(`Failed after ${maxRetries} attempts. Error: ${e.message}`);
          throw e;
        }
        const backoffTime = Math.pow(2, i) * 1000;
        await new Promise(resolve => setTimeout(resolve, backoffTime));
      }
    }
  }
}

export { NetworkHandler };