-- 1. Row counts per table
SELECT 'companies' AS tbl, COUNT(*) FROM companies
UNION ALL SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL SELECT 'stock_prices', COUNT(*) FROM stock_prices;

-- 2. Companies with <5 years of P&L history
SELECT company_id, COUNT(*) AS yrs FROM profitandloss GROUP BY company_id HAVING yrs < 5;

-- 3. Null check - net_profit
SELECT COUNT(*) FROM profitandloss WHERE net_profit IS NULL;

-- 4. Year coverage range per table
SELECT MIN(year), MAX(year) FROM profitandloss;
SELECT MIN(year), MAX(year) FROM balancesheet;
SELECT MIN(year), MAX(year) FROM cashflow;

-- 5. Sector distribution
SELECT broad_sector, COUNT(*) FROM sectors GROUP BY broad_sector ORDER BY COUNT(*) DESC;

-- 6. Companies missing from sectors (should be 0)
SELECT id FROM companies WHERE id NOT IN (SELECT company_id FROM sectors);

-- 7. Debt-free companies latest year (financial_ratios)
SELECT company_id FROM financial_ratios WHERE debt_to_equity = 0 AND year = (SELECT MAX(year) FROM financial_ratios);

-- 8. Avg sales by year
SELECT year, ROUND(AVG(sales),1) AS avg_sales FROM profitandloss GROUP BY year ORDER BY year;

-- 9. Peer group member counts
SELECT peer_group_name, COUNT(*) FROM peer_groups GROUP BY peer_group_name;

-- 10. Companies with negative net_profit (loss-making) count
SELECT COUNT(DISTINCT company_id) FROM profitandloss WHERE net_profit < 0;