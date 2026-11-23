# 📊 Indian Startup Funding Analysis (2015 – May 2022)

> End-to-end data analytics project: merging three public sources, cleaning messy real-world data, SQL analysis, Python exploration and an interactive Power BI dashboard.

![Python](https://img.shields.io/badge/Python-pandas%20%7C%20Matplotlib%20%7C%20Seaborn-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![Google Colab](https://img.shields.io/badge/Google-Colab-F9AB00?logo=googlecolab&logoColor=white)


---

## Table of contents
1. [Project overview](#project-overview)
2. [Key findings](#key-findings)
3. [Dashboard](#dashboard)
4. [Data sources and credits](#data-sources-and-credits)
5. [Methodology](#methodology)
6. [Data dictionary](#data-dictionary)
7. [Repository structure](#repository-structure)
8. [How to reproduce](#how-to-reproduce)
9. [Limitations](#limitations)
10. [Skills demonstrated](#skills-demonstrated)
11. [Author](#author)

---

## Project overview

India's startup ecosystem attracted tens of billions of dollars in venture funding between 2015 and 2022, but no single free dataset covers the whole period. This project **builds one**: it merges three public sources into about 5,900 real deals, cleans them step by step, and answers five business questions:

1. Which **sectors** receive the most funding?
2. Which **cities** are the main startup hubs?
3. How did funding change **year by year**, including the COVID period and the 2021 boom?
4. Which **funding stages** are the most common, and which bring in the most money?
5. Which **investors** are the most active?

## Key findings

| Question | Finding |
|---|---|
| Total funding | About **$96.7 billion** across **5,857 deals** (4,332 deals disclosed an amount) |
| Peak year | **2021**: about $29.3B across 1,187 deals |
| Top sectors | E-commerce & Retail ($18.6B), Tech & SaaS ($15.4B) and FinTech ($14.5B) together received about **half** of all funding |
| Top cities | **Bengaluru 46%**, Delhi-NCR 23%, Mumbai 19%; every other city had 3% or less |
| Stages | Seed/Angel is the most common (2,196 deals) but brings only ~$1.8B; **124 Series D+ rounds brought ~$16.9B** |
| Deal size | The average disclosed deal grew from ~$6.5M (2016) to ~$47.7M (Jan–May 2022) |
| Top startups | Flipkart (~$4.1B), Swiggy, Reliance, Paytm and BYJU'S lead the list |
| Most active investors | Sequoia Capital (~178 deals) and Accel Partners (~125) |

The totals are lower than the figures in industry reports because many deals in public lists do not disclose an amount. The shape of the trend (a 2021 peak followed by a fall) matches the reports.

### Charts

| Funding by year | Top sectors |
|---|---|
| ![Funding by year](charts/01_funding_by_year.png) | ![Top sectors](charts/02_top_sectors.png) |

| City share | Sector × year heatmap |
|---|---|
| ![City share](charts/03_city_share.png) | ![Heatmap](charts/07_sector_year_heatmap.png) |

## Dashboard

`startup_funding_dashboard.pbix` is a two-page interactive Power BI report. Open it with the free Power BI Desktop (Windows).

- **Page 1 – Overview:** KPI cards (total funding, total deals, average deal size), funding by year, funding by sector, and the top cities by deals.
- **Page 2 – Top Startups:** a top-10 table with slicers for year range, city and funding stage.
- **DAX measures:** `Total Funding (B$)`, `Total Deals`, `Avg Deal Size (M$)` and `Deal Count`.

<!-- Tip: add screenshots of both pages here, e.g. ![Overview](dashboard/page1.png) -->

## Data sources and credits

All original data belongs to its authors and is used here for **educational purposes**. Please check each source's licence before reusing the data.

| Period | Source | Notes |
|---|---|---|
| 2015 – 2017 | [Indian Startup Funding – Sudalai Rajkumar (Kaggle)](https://www.kaggle.com/datasets/sudalairajkumar/indian-startup-funding) | Covers Jan 2015 – Aug 2017 |
| 2018 – 2021 | Yearly files `startup_funding2018.csv` to `startup_funding2021.csv` from a public GitHub repository: [https://github.com/abhishekbuild/Streamlit-Indian-Startup-Funding] | Data originally compiled from public startup-funding news |
| Jan – May 2022 | [Indian Startups – Funding & Investors Data [January-May 2022] (Kaggle, omkargowda)](https://www.kaggle.com/datasets/omkargowda/indian-startups-funding-data-januarymay-2022) – confirm link | Original data from [StartupTalky](https://startuptalky.com/indian-startups-funding-investors-data-2022/) |

**Checked and rejected:**
- A 2020–2025 sample dataset: synthetic (the same startup appeared in unrelated industries, no missing values at all).
- A separate cleaned 2018–2021 file: overlapped the files above and had 219 of 550 rows duplicated.
- Monthly scraped files for 2015–2021: 99–100% of their startups were already present.

Industry totals for 2021–2025 used in the report for context come from Inc42, YourStory, Tracxn and TheKredible; they are **not** part of this dataset.

## Methodology

1. **Merge** (`01_merge_and_clean.ipynb`): standardised column names across 9 source files, kept non-overlapping years, added `Year` and `Source_File`, and stacked everything with `pd.concat()` into a **raw** file of 5,922 rows.
2. **Clean amounts:** a custom `clean_amount()` function handled Indian-style commas, `$`/`₹` symbols, ranges, two amounts in one cell, "Undisclosed"/"N/A", amounts written in millions, and converted rupees at about ₹70 = $1 (2018 file).
3. **Standardise categories:** keyword rules mapped 242 city spellings to 167 (`City_Std`), 96 stage labels to 10 stages (`Stage_Std`) and 1,675 industry labels to 18 sectors (`Sector`).
4. **De-duplicate:** removed 34 duplicate rows. Final file: **5,857 rows × 13 columns**.
5. **SQL analysis** (`02_sql_analysis.ipynb`): SQLite inside Colab with aggregations, joins of ideas such as "top sector per year" using a CTE and the `RANK()` window function.
6. **EDA** (`03_eda_python.ipynb`): 7 charts, plus investor-name splitting with `.explode()`.
7. **Dashboard:** Power BI Desktop with DAX measures, Top N filters and slicers.

Example query, the leading sector in each year:

```sql
WITH yearly AS (
    SELECT Year, Sector, SUM(Amount_USD) AS total
    FROM funding
    GROUP BY Year, Sector
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY Year ORDER BY total DESC) AS rnk
    FROM yearly
)
SELECT Year, Sector, ROUND(total / 1e9, 2) AS total_billion_usd
FROM ranked
WHERE rnk = 1
ORDER BY Year;
```

### Data quality issues found and fixed

| Issue | Action |
|---|---|
| Hidden encoding junk in 87 rows (the digits inside it turned `$20,000,000` into about $2 billion and "N/A" into 20) | Removed from every column, then re-cleaned |
| 31 April-2022 rows were cumulative totals ("Multiples"), not single deals | Removed |
| 2022 amounts written in millions (e.g. `84.2`) | Multiplied by 1,000,000 |
| Impossible values (e.g. $150B for one small investor, a US company, garbled text) | Amount set to missing; row kept for deal counts |
| The same city written many ways (Bangalore / Banglore / Bengaluru) | Mapped to one name |

## Data dictionary

`startup_funding_clean.csv` (5,857 rows × 13 columns)

| Column | Description |
|---|---|
| `Year` | Year of the deal |
| `Date` | Deal date where available (2015–2017 and 2022); 2018–2021 have only the year |
| `Startup` | Startup name |
| `Sector` | Standardised sector (18 groups) |
| `City_Std` | Standardised city (Delhi, Gurugram and Noida kept separate) |
| `Investors` | Investor names as listed in the source |
| `Stage_Std` | Standardised funding stage (10 groups) |
| `Amount_USD` | Cleaned amount in US dollars (blank if undisclosed) |
| `Industry`, `City`, `Stage`, `Amount` | Original uncleaned values, kept so every change can be traced |
| `Source_File` | Which source file the row came from |

## Repository structure

```
.
├── 01_merge_and_clean.ipynb         # merge + clean (Google Colab)
├── 02_sql_analysis.ipynb            # SQL analysis (SQLite in Colab)
├── 03_eda_python.ipynb              # Python EDA and charts
├── indian_startup_funding_raw.csv   # merged, uncleaned (5,922 rows)
├── startup_funding_clean.csv        # cleaned (5,857 rows)
├── startup_funding_dashboard.pbix   # Power BI dashboard
└── charts/                          # 7 exported charts (PNG)
```

## How to reproduce

1. Open the three notebooks in Google Colab and run them **in order: 01 → 02 → 03**.
2. In notebook 01, upload the source files when asked (see the credits table for where to download them).
3. Notebooks 02 and 03 read `startup_funding_clean.csv`, which notebook 01 produces.
4. Open the `.pbix` file in Power BI Desktop (Windows) to explore the dashboard.

## Limitations

- About **26% of deals have no disclosed amount**, so funding totals are under-counted.
- Many 2015–2017 sector labels are broad (for example "Technology"), so some sector assignments are approximate.
- The 2019 source file is small (89 deals), so 2019 looks much lower than it really was.
- Deal-level data stops in **May 2022**. Later years are covered only by published industry totals in the project report.
- Rupee amounts in the 2018 file use a fixed rate of ₹70 = $1.
- Startup names are not fully standardised (for example "Byju's" and "BYJU'S" count separately in SQL and Power BI).

## Skills demonstrated

Data collection and validation (spotting a synthetic dataset) · data merging · data cleaning with regex and custom functions · SQL (aggregations, CTEs, window functions) · exploratory analysis with pandas, Matplotlib and Seaborn · Power BI (DAX measures, Top N filters, slicers) · data storytelling · documenting a reproducible workflow. AI assistants (Claude, ChatGPT, Gemini, Copilot) were used to help with code, formulas and debugging; all results were checked against the data.

## Author

**Ritu Prabhat** 

---
*Educational project. Datasets belong to their original authors and sources; see the credits above.*
