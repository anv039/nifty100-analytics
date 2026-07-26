# Sprint 2 Retrospective

## Completed
- ratios.py, cagr.py, cashflow_kpis.py — all formula modules with edge-case handling
- financial_ratios table populated: 1041 rows (deduped from 1160 raw), all KPI columns filled
- capital_allocation.csv: 1039 rows
- ratio_edge_cases.log: 54 anomalies documented and categorized
- 34/34 KPI unit tests pass (exceeds 20 minimum)
- Screener preview: 37 companies match ROE>15% & D/E<1 (within 15-50 expected range)

## Deviations from doc (flagged, not hidden)
- financial_ratios row count (1041) is below doc's literal "≥1,100" gate — this is because we
  correctly deduplicated 119 true duplicate rows the source file contained. Accuracy prioritized
  over the raw count target.
- Extreme ROE outliers (BEL, HAL, INDIGO) due to thin equity base in source data — documented
  in data_caveats.md, not silently excluded.
- Financials sector company count: sectors.xlsx has 23, doc states 19 — data/doc mismatch, not our error.