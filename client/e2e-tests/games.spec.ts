import { test, expect } from '@playwright/test';

test.describe('Game Listing and Navigation', () => {
  test('should display games with titles on index page', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check that games are displayed
    const gameCards = page.locator('[data-testid="game-card"]');
    
    // Wait for at least one game card to be visible
    await expect(gameCards.first()).toBeVisible();
    
    // Check that we have at least one game
    const gameCount = await gameCards.count();
    expect(gameCount).toBeGreaterThan(0);
    
    // Check that each game card has a title
    const firstGameCard = gameCards.first();
    await expect(firstGameCard.locator('[data-testid="game-title"]')).toBeVisible();
    
    // Verify that game titles are not empty
    const gameTitle = await firstGameCard.locator('[data-testid="game-title"]').textContent();
    expect(gameTitle?.trim()).toBeTruthy();
  });

  test('should navigate to correct game details page when clicking on a game', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get the first game card and its data attributes
    const firstGameCard = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGameCard.getAttribute('data-game-id');
    const gameTitle = await firstGameCard.getAttribute('data-game-title');
    
    // Click on the first game
    await firstGameCard.click();
    
    // Verify we're on the correct game details page
    await expect(page).toHaveURL(`/game/${gameId}`);
    
    // Verify the game details page loads
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify the title matches what we clicked on
    const detailsTitle = page.locator('[data-testid="game-details-title"]');
    await expect(detailsTitle).toHaveText(gameTitle || '');
  });

  test('should display game details with all required information', async ({ page }) => {
    // Navigate to a specific game (we'll use game ID 1 as an example)
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the game title is present and not empty
    const gameTitle = page.locator('[data-testid="game-details-title"]');
    await expect(gameTitle).toBeVisible();
    const titleText = await gameTitle.textContent();
    expect(titleText?.trim()).toBeTruthy();
    
    // Check that the game description is present and not empty
    const gameDescription = page.locator('[data-testid="game-details-description"]');
    await expect(gameDescription).toBeVisible();
    const descriptionText = await gameDescription.textContent();
    expect(descriptionText?.trim()).toBeTruthy();
    
    // Check that either publisher or category (or both) are present
    const publisherExists = await page.locator('[data-testid="game-details-publisher"]').isVisible();
    const categoryExists = await page.locator('[data-testid="game-details-category"]').isVisible();
    expect(publisherExists && categoryExists).toBeTruthy();
    
    // If publisher exists, check it has content
    if (publisherExists) {
      const publisherText = await page.locator('[data-testid="game-details-publisher"]').textContent();
      expect(publisherText?.trim()).toBeTruthy();
    }
    
    // If category exists, check it has content
    if (categoryExists) {
      const categoryText = await page.locator('[data-testid="game-details-category"]').textContent();
      expect(categoryText?.trim()).toBeTruthy();
    }
  });

  test('should display a button to back the game', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the back game button is present
    const backButton = page.locator('[data-testid="back-game-button"]');
    await expect(backButton).toBeVisible();
    await expect(backButton).toContainText('Support This Game');
    
    // Verify the button is clickable
    await expect(backButton).toBeEnabled();
  });

  test('should be able to navigate back to home from game details', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for the page to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Find and click the back to all games link
    const backLink = page.locator('a:has-text("Back to all games")');
    await expect(backLink).toBeVisible();
    await backLink.click();
    
    // Verify we're back on the home page
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
  });

  test('should handle navigation to non-existent game gracefully', async ({ page }) => {
    // Navigate to a game that doesn't exist
    await page.goto('/game/99999');
    
    // The page should load without crashing
    // Check if there's an error message or if it handles gracefully
    await page.waitForTimeout(3000);
    
    // The page should either show an error or handle it gracefully
    // We expect the page to not crash and still have a valid title
    await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
  });

  test('should display category and publisher filter controls', async ({ page }) => {
    await page.goto('/');

    // Wait for the filter controls to appear
    await page.waitForSelector('[data-testid="filter-controls"]', { timeout: 10000 });

    // Verify both filter dropdowns are present
    await expect(page.locator('[data-testid="category-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="publisher-filter"]')).toBeVisible();

    // Verify both dropdowns have options beyond the default "All" option
    const categoryOptions = page.locator('[data-testid="category-filter"] option');
    const publisherOptions = page.locator('[data-testid="publisher-filter"] option');

    expect(await categoryOptions.count()).toBeGreaterThan(1);
    expect(await publisherOptions.count()).toBeGreaterThan(1);
  });

  test('should filter games by category', async ({ page }) => {
    await page.goto('/');

    // Wait for games grid and filters to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="category-filter"]', { timeout: 10000 });

    // Count total games before filtering
    const totalGames = await page.locator('[data-testid="game-card"]').count();

    // Select the first non-default category option
    const categorySelect = page.locator('[data-testid="category-filter"]');
    const firstCategory = await categorySelect.locator('option').nth(1).textContent();
    await categorySelect.selectOption({ index: 1 });

    // Wait for the loading state to resolve and the games list to update
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });

    // All visible game cards should have the selected category badge
    const filteredCards = page.locator('[data-testid="game-card"]');
    const filteredCount = await filteredCards.count();

    // Filtered count should be less than or equal to total count
    expect(filteredCount).toBeLessThanOrEqual(totalGames);

    // Each displayed game card should show the selected category
    for (let i = 0; i < filteredCount; i++) {
      const categoryBadge = await filteredCards.nth(i).locator('[data-testid="game-category"]').textContent();
      expect(categoryBadge?.trim()).toBe(firstCategory?.trim());
    }
  });

  test('should filter games by publisher', async ({ page }) => {
    await page.goto('/');

    // Wait for games grid and filters to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="publisher-filter"]', { timeout: 10000 });

    // Count total games before filtering
    const totalGames = await page.locator('[data-testid="game-card"]').count();

    // Select the first non-default publisher option
    const publisherSelect = page.locator('[data-testid="publisher-filter"]');
    const firstPublisher = await publisherSelect.locator('option').nth(1).textContent();
    await publisherSelect.selectOption({ index: 1 });

    // Wait for the loading state to resolve and the games list to update
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });

    const filteredCards = page.locator('[data-testid="game-card"]');
    const filteredCount = await filteredCards.count();

    // Filtered count should be less than or equal to total count
    expect(filteredCount).toBeLessThanOrEqual(totalGames);

    // Each displayed game card should show the selected publisher
    for (let i = 0; i < filteredCount; i++) {
      const publisherBadge = await filteredCards.nth(i).locator('[data-testid="game-publisher"]').textContent();
      expect(publisherBadge?.trim()).toBe(firstPublisher?.trim());
    }
  });

  test('should show clear filters button when filters are active and clear on click', async ({ page }) => {
    await page.goto('/');

    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });

    // No clear button initially
    await expect(page.locator('[data-testid="clear-filters"]')).not.toBeVisible();

    // Select a category filter
    await page.locator('[data-testid="category-filter"]').selectOption({ index: 1 });

    // Wait for the clear filters button to appear (reactively set when filter active)
    await expect(page.locator('[data-testid="clear-filters"]')).toBeVisible({ timeout: 5000 });

    // Count total games before clearing
    const totalGames = await page.locator('[data-testid="game-card"]').count();

    // Click clear filters
    await page.locator('[data-testid="clear-filters"]').click();

    // Wait for the games grid to reload after clearing filters
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });

    // Clear button should be gone
    await expect(page.locator('[data-testid="clear-filters"]')).not.toBeVisible();

    // All games should be visible again
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 5000 });
    const allGames = await page.locator('[data-testid="game-card"]').count();
    expect(allGames).toBeGreaterThanOrEqual(totalGames);
  });
});

