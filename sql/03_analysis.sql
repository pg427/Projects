-- TASK 1: Count distinct countries
SELECT COUNT(DISTINCT country_name) AS total_distinct_countries FROM international_debt;

-- TASK 2: Find country with highest summed debt value
SELECT country_name, SUM(debt) AS total_debt
FROM international_debt
GROUP BY country_name
ORDER BY total_debt DESC
LIMIT 1;

-- TASK 3: Lowest amount of principal repayments
SELECT country_name, indicator_name, debt AS lowest_repayment
FROM international_debt
WHERE indicator_code = 'DT.AMT.DLXF.CD'
    AND debt is NOT NULL
ORDER BY debt ASC, country_code ASC
LIMIT 1;