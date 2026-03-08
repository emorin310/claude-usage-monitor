// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Claude Usage Monitor Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for WebSocket to connect and first render
    await page.waitForFunction(() =>
      document.getElementById('liveTs')?.textContent !== 'connecting…',
      { timeout: 10000 }
    );
  });

  // ── Page structure ───────────────────────────────────────────────────────

  test('page loads with correct title', async ({ page }) => {
    await expect(page).toHaveTitle('Claude Usage Monitor');
  });

  test('top bar is visible', async ({ page }) => {
    const topbar = page.locator('.topbar');
    await expect(topbar).toBeVisible();
    await expect(topbar.locator('.app-title')).toContainText('Claude Usage Monitor');
  });

  test('status bar is visible', async ({ page }) => {
    await expect(page.locator('.statusbar')).toBeVisible();
  });

  // ── Live indicator ────────────────────────────────────────────────────────

  test('live indicator shows a timestamp after connecting', async ({ page }) => {
    const liveTs = page.locator('#liveTs');
    await expect(liveTs).toBeVisible();
    // Timestamp should be in HH:MM:SS or HH:MM format, not the placeholder
    const text = await liveTs.textContent();
    expect(text).toMatch(/\d{1,2}:\d{2}/);
  });

  test('live dot is pulsing (has animation class)', async ({ page }) => {
    const dot = page.locator('.live-dot');
    await expect(dot).toBeVisible();
    // Should NOT have the inactive class when connected
    await expect(dot).not.toHaveClass(/inactive/);
  });

  // ── Gauge cards ───────────────────────────────────────────────────────────

  test('weekly gauge card is visible and content-height only', async ({ page }) => {
    const card = page.locator('.weekly-gauge-area');
    await expect(card).toBeVisible();

    // Card should contain its gauge
    await expect(card.locator('.gauge-wrap')).toBeVisible();

    // Verify the card does NOT stretch to full viewport height
    const cardBox = await card.boundingBox();
    const viewportSize = page.viewportSize();
    expect(cardBox.height).toBeLessThan(viewportSize.height * 0.6);
  });

  test('5-hour utilization gauge card is visible and content-height only', async ({ page }) => {
    const card = page.locator('.gauge-area');
    await expect(card).toBeVisible();
    await expect(card.locator('.gauge-wrap')).toBeVisible();

    const cardBox = await card.boundingBox();
    const viewportSize = page.viewportSize();
    expect(cardBox.height).toBeLessThan(viewportSize.height * 0.6);
  });

  test('monthly add. API credits gauge card is visible and content-height only', async ({ page }) => {
    const card = page.locator('.monthly-gauge-area');
    await expect(card).toBeVisible();
    await expect(card.locator('.card-title')).toContainText('Monthly Add. API Credits');

    const cardBox = await card.boundingBox();
    const viewportSize = page.viewportSize();
    expect(cardBox.height).toBeLessThan(viewportSize.height * 0.6);
  });

  test('gauge cards do not stretch when window is resized smaller', async ({ page }) => {
    // Narrow window to trigger layout stress
    await page.setViewportSize({ width: 900, height: 600 });
    await page.waitForTimeout(300); // allow layout to settle

    for (const sel of ['.weekly-gauge-area', '.gauge-area', '.monthly-gauge-area']) {
      const box = await page.locator(sel).boundingBox();
      // Each gauge card must be shorter than 60% of the viewport height
      expect(box.height, `${sel} should not stretch`).toBeLessThan(600 * 0.6);
    }
  });

  // ── Chart cards ───────────────────────────────────────────────────────────

  test('rate chart card is visible', async ({ page }) => {
    await expect(page.locator('.rate-area')).toBeVisible();
    await expect(page.locator('#rateChart')).toBeVisible();
  });

  test('model breakdown card is visible', async ({ page }) => {
    await expect(page.locator('.model-area')).toBeVisible();
  });

  // ── Sessions table ────────────────────────────────────────────────────────

  test('sessions area is visible', async ({ page }) => {
    await expect(page.locator('.sessions-area')).toBeVisible();
    await expect(page.locator('.sessions-table')).toBeVisible();
  });

  test('sessions count is displayed', async ({ page }) => {
    const count = page.locator('#sessionCount');
    await expect(count).toBeVisible();
    await expect(count).toContainText('session');
  });

  // ── Settings modal ────────────────────────────────────────────────────────

  test('settings button is visible in top bar', async ({ page }) => {
    const btn = page.locator('#gearBtn');
    await expect(btn).toBeVisible();
    await expect(btn).toContainText('Settings');
  });

  test('settings modal opens on button click', async ({ page }) => {
    await page.click('#gearBtn');
    // The overlay gains the "open" class when shown
    const overlay = page.locator('#configOverlay');
    await expect(overlay).toHaveClass(/open/);
  });

  test('settings modal has session key field', async ({ page }) => {
    await page.click('#gearBtn');
    await expect(page.locator('#cfgSessionKey')).toBeVisible();
  });

  test('settings modal has org ID field', async ({ page }) => {
    await page.click('#gearBtn');
    await expect(page.locator('#cfgOrgId')).toBeVisible();
  });

  test('settings modal has poll interval selector', async ({ page }) => {
    await page.click('#gearBtn');
    const pollSelect = page.locator('#cfgPollInterval');
    await expect(pollSelect).toBeVisible();
    const options = await pollSelect.locator('option').count();
    expect(options).toBeGreaterThanOrEqual(4);
  });

  test('settings modal closes on Cancel click', async ({ page }) => {
    await page.click('#gearBtn');
    await expect(page.locator('#configOverlay')).toHaveClass(/open/);
    await page.click('#cfgCancel');
    await expect(page.locator('#configOverlay')).not.toHaveClass(/open/);
  });

  test('settings modal closes on Escape key', async ({ page }) => {
    await page.click('#gearBtn');
    await expect(page.locator('#configOverlay')).toHaveClass(/open/);
    await page.keyboard.press('Escape');
    await expect(page.locator('#configOverlay')).not.toHaveClass(/open/);
  });

  test('settings modal loads current config values', async ({ page }) => {
    await page.click('#gearBtn');
    // Wait for openConfig() async fetch to populate the field
    await page.waitForFunction(() =>
      document.getElementById('cfgOrgId')?.value.length > 0,
      { timeout: 5000 }
    );
    const orgVal = await page.locator('#cfgOrgId').inputValue();
    expect(orgVal.length).toBeGreaterThan(0);
  });

  // ── Status bar ────────────────────────────────────────────────────────────

  test('status bar shows connected state', async ({ page }) => {
    const sb = page.locator('.statusbar');
    await expect(sb).toContainText('Connected');
  });

  test('status bar shows polling interval', async ({ page }) => {
    const sb = page.locator('.statusbar');
    // Should mention poll frequency (e.g. "polling every 30s")
    await expect(sb).toContainText(/polling every/i);
  });

  // ── Session flyout ────────────────────────────────────────────────────────

  test('session flyout element exists in DOM', async ({ page }) => {
    await expect(page.locator('#sessionFlyout')).toBeAttached();
  });

  test('session row hover shows flyout when sessions exist', async ({ page }) => {
    // Only run this check if there are actual session rows
    const rows = page.locator('.session-row');
    const count = await rows.count();

    if (count > 0) {
      await rows.first().hover();
      await page.waitForTimeout(200); // hover delay
      const flyout = page.locator('#sessionFlyout');
      await expect(flyout).toBeVisible();
      // Flyout should contain session info
      const text = await flyout.textContent();
      expect(text.length).toBeGreaterThan(10);
    } else {
      test.skip(); // No sessions to hover over
    }
  });

});
