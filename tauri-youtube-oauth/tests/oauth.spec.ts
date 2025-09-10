import { test, expect, _electron as electron } from '@playwright/test';
import * as http from 'http';
import * as fs from 'fs/promises';
import * as path from 'path';

const MOCK_SERVER_PORT = 14321;
const MOCK_AUTH_CODE = 'mock_auth_code_123';

// Helper to create a mock OAuth callback server
const createMockServer = () => {
  return new Promise<http.Server>((resolve) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, `http://${req.headers.host}`);
      if (url.pathname === '/callback') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('Authentication successful! You can close this window.');
        // In a real scenario, you would handle the auth code here
      } else {
        res.writeHead(404);
        res.end('Not Found');
      }
    });
    server.listen(MOCK_SERVER_PORT, () => {
      console.log(`Mock server listening on port ${MOCK_SERVER_PORT}`);
      resolve(server);
    });
  });
};

test('OAuth flow with mock server', async () => {
  // 1. Start the mock server
  const server = await createMockServer();

  // 2. Launch the Tauri app
  const appPath = './src-tauri/target/debug/ytlite-oauth';
  const electronApp = await electron.launch({ args: [appPath] });
  const window = await electronApp.firstWindow();

  // 3. Mock the googleapis.com endpoint
  await window.route('https://accounts.google.com/o/oauth2/v2/auth**', (route) => {
    const url = new URL(route.request().url());
    const redirectUri = url.searchParams.get('redirect_uri');
    const state = url.searchParams.get('state');
    
    // Redirect to our mock server with a fake code
    route.fulfill({
      status: 302,
      headers: {
        Location: `${redirectUri}?code=${MOCK_AUTH_CODE}&state=${state}`,
      },
    });
  });

  // 4. Click the login button
  await window.click('button:has-text("Login with Google")');

  // 5. Wait for the success message to appear in the app
  const successMessage = window.locator('text=Authentication successful');
  await expect(successMessage).toBeVisible({ timeout: 10000 });

  // 6. Verify that the tokens have been saved (conceptual)
  // In a real test, you would invoke a Tauri command to get the tokens
  // or check the file system where tokens are stored.
  const configDir = await electronApp.evaluate(async ({ app }) => {
    return await app.getPath('appConfig');
  });
  const tokenPath = path.join(configDir, 'tokens.json');
  
  // For this example, we'll just check if the file exists.
  // A more robust test would check its content.
  await expect(fs.access(tokenPath)).resolves.toBeUndefined();

  // 7. Clean up
  await electronApp.close();
  server.close();
});
