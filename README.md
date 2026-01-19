# Miraclib Trial Analysis

This repository implements all four parts of Bob’s analysis using `cell-count.csv` + `example.db`, and the Streamlit dashboard is live at https://teiknical-chofcssjksgrbd6i7guk4y.streamlit.app/.

### Schema overview
`sqlite.py` builds a single `cell_counts` table where each row represents a sample and stores the project/subject metadata (`project`, `subject`, `condition`, `treatment`, `response`, demographics, `sample_type`, `time_from_treatment_start`) along with the five immune-cell counts (`b_cell`, `cd8_t_cell`, `cd4_t_cell`, `nk_cell`, `monocyte`). This schema keeps the facts in one place, which simplifies joins for per-sample analytics, lets you filter on patient attributes, and still allows efficient aggregation when you add indexes on frequently queried columns (e.g., `project`, `sample_type`, `response`, `time_from_treatment_start`). When the workload scales to hundreds of projects and thousands of samples, you can partition the data by project or sample_type, add covering indexes, and store derived summaries (e.g., totals, percentages) in cached views without changing the fundamental schema.

### Code layout
The `scripts/` directory holds every Python tool so that users can find the loader (`sqlite.py`), the relative-frequency exporter (`data_overview.py`), responder analysis (`stats.py`), subset reporting (`subset_analysis.py`), the dashboard (`dashboard.py`), and helper visuals (`plot_response.py`) in one place. Each script focuses on a single responsibility and reads from `example.db`, which keeps replayable analytics and lets you swap the storage layer if needed (e.g., swap SQLite for Postgres) without rewriting the dashboard or analyses. The dashboard pulls together these scripts’ outputs and adds Streamlit UI, while Docker/requirements files standardize the runtime so you can run anything from the command line or container without installing multiple environments.

The Python tools live in `scripts/` so the root stays focused on data and documentation:

```
scripts/
  ├── dashboard.py
  ├── data_overview.py
  ├── plot_response.py
  ├── sqlite.py
  ├── stats.py
  └── subset_analysis.py
```

Move on to each step below once you refresh the database.

1. **Data Management** – schema design + loader.
2. **Initial Analysis** – sample-level population frequencies.
3. **Statistical Analysis** – responder vs non-responder comparison with visualization and tests.
4. **Data Subset Analysis** – melanoma baseline PBMC subset summaries.

An interactive Streamlit dashboard (`dashboard.py`) stitches the parts together for easier exploration.

## Getting started

1. Build or prepare the SQLite DB:
   ```bash
   python scripts/sqlite.py
   ```
   That creates/refreshes `cell_counts` in `example.db` by reading every row from `cell-count.csv` using the schema defined in `scripts/sqlite.py`.

2. Inspect relative frequencies:
   ```bash
   python scripts/data_overview.py > relative_frequencies.csv
   ```
   The script emits one row per sample/population with `total_count`, `count`, and `percentage`.

3. Statistical analysis:
   ```bash
   python scripts/stats.py
   ```
   Prints responder/non-responder means, differences, optional p-values (if `scipy` installed) from a Welch’s two-sided t-test (which is appropriate because it compares two independent PBMC groups without assuming equal variances), and — when `matplotlib` is available — generates `response_boxplot.png`.

4. Subset summary:
   ```bash
   python scripts/subset_analysis.py
   ```
   Lists baseline melanoma PBMC samples on miraclib plus counts per project, response, and sex.

## Interactive dashboard

Install dependencies (see below) and run:

```bash
streamlit run scripts/dashboard.py
```

That page shows:

- Raw table preview (Part 1)
- Relative frequencies per sample with filtering (Part 2)
- Responder vs non-responder summary table, statistical flags, and boxplots (Part 3)
- Baseline melanoma subset overview plus project/response/sex counts (Part 4)

## Dependencies

Install the shared environment before running scripts or the dashboard:

```bash
pip install -r requirements.txt
```

Required packages: `numpy`, `pandas`, `streamlit`, `matplotlib`, `scipy`.

## Docker

Build the image:

```bash
docker build -t docker.io/library/miraclib-analysis .
```

Run analysis scripts inside the container:

```bash
docker run --rm -v "$PWD":/app -w /app docker.io/library/miraclib-analysis python scripts/stats.py
```

Other examples are in [DOCKER.md](DOCKER.md). Use the Streamlit command from that document to expose the dashboard.
