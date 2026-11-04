# International Debt Analysis w/ SQL

## Overview
Analyze World Bank Debt dataset exported via DataCamp using PostgreSQL

## Findings
- Dataset: 2,357 rows covering 124 distinct countries
- Highest sum across debt indicators: China - $285,793,494,734.90
- Lowest principal repayment for indicator DT.AMT.DLXF.CD:
    Timor-Leste - $825,000.

## Limitations
Indicators include overlapping categories and different measures.
The sum follows the exercise definition & shouldn't be interpreted as a country-s outstanding debt.
The export contains no year column, so the findings do not establish current debt levels.

## SQL Skills Used:
SELECT, COUNT, DISTINCT, SUM, GROUP BY, WHERE,
IS NOT NULL, ORDER BY, LIMIT, and column aliases.

## Requirements
- PostgreSQL and the `psql` command-line client.
- Run commands from the project's root folder

## Dataset Access
The dataset is not included in this repository.
Source: https://www.datacamp.com/projects/1906

To reproduce, obtain the dataset and follow the Data Preparation
instructions below before running the SQL scripts.

## Data Preparation
- Keep the original Excel export in `data/raw/`
- Export CSV without the extra `index` column to:
  `data/processed/1_intl_debt_data.csv`

## Running the Project:
With PostgreSQL running; execute the following commands in Terminal.
Use a new database; importing again adds duplicate rows.

```bash
createdb international_debt
psql -X -v ON_ERROR_STOP=1 -d international_debt -f sql/01_create_table.sql
psql -X -v ON_ERROR_STOP=1 -d international_debt -f sql/02_import_data.psql
psql -X -v ON_ERROR_STOP=1 -d international_debt -f sql/02_validate_data.sql
psql -X -v ON_ERROR_STOP=1 -d international_debt -f sql/03_analysis.sql
```