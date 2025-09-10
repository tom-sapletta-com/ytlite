import { test, expect } from '@playwright/test'

// This suite runs against the Vite dev server (configured in playwright.config.ts)
// It exercises the UI flow with mocked Tauri invocations (via src/tauriInvoke.ts fallback)

test.describe('OAuth UI Flow (mocked)', () => {
  test('landing page shows main controls', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Tauri YouTube OAuth' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zaloguj do YouTube' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Pobierz kanały' })).toBeVisible()
  })

  test('callback page simulates code exchange and shows success', async ({ page }) => {
    await page.goto('/callback?code=PLAYWRIGHT_MOCK')
    // Our App sets a status message after invoking exchange_code
    await expect(page.locator('text=Autoryzacja zakończona. Możesz zamknąć to okno.')).toBeVisible()
  })

  test('generate .env copies to clipboard (mocked)', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /Generuj \.env/ }).click()
    await expect(page.locator('text=Skopiowano zawartość .env do schowka')).toBeVisible()
  })
})
