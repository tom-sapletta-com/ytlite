import { test, expect, _electron as electron } from '@playwright/test';

// This test is a basic example of how to launch the Tauri app and check its title.
// It requires the app to be built first.
test('launch app and check title', async () => {
  // Launch the app
  const electronApp = await electron.launch({ args: ['./src-tauri/target/release/ytlite-oauth'] });

  // Get the first window
  const window = await electronApp.firstWindow();

  // Check the title
  await expect(window).toHaveTitle('YTLite OAuth');

  // Close the app
  await electronApp.close();
});
