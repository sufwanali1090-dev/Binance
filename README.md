# Binance Live Arbitrage Signals

Read-only Binance Spot triangular-arbitrage scanner.

## Run
Upload this repository to GitHub → Actions → Binance Live Arbitrage Signals → Run workflow.

It automatically discovers Binance Spot symbols, builds triangular routes, consumes live bookTicker data, applies 3 trading fees, and outputs only opportunities above the configured profit threshold.

No API keys, private keys, orders, withdrawals, or auto-trading are included.

GitHub Actions is useful for testing/monitoring but is not a low-latency 24/7 production server.
