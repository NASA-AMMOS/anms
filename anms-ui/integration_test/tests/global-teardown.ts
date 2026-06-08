/**
 * Global Playwright teardown - runs once after all tests.
 *
 * Currently empty - containers should be managed externally
 * via docker compose down --remove-orphans
 */

export default async function globalTeardown() {
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║  ANMS Angular UI Integration Tests       ║');
  console.log('║  Global Teardown                         ║');
  console.log('╚══════════════════════════════════════════╝');
  console.log('\nTo clean up test environment:');
  console.log('  docker compose -f docker-compose-full.yml down --remove-orphans');
  console.log('\n');
}
