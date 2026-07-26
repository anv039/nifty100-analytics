# Known Data Caveats — Sprint 2

## Extreme ROE values (near-zero equity base)
BEL, HAL, INDIGO, and possibly others show ROE > 200% because their equity_capital + reserves
figures in balancesheet.xlsx are disproportionately small relative to net_profit for their
scale of operations. Formula is mathematically correct; the anomaly stems from source data
(possibly a units mismatch or genuinely thin book equity for these companies).
These values are NOT excluded from financial_ratios or the screener — flagged here for
analyst awareness before using in Module 3 (Screener) or Module 5 (Health Score).