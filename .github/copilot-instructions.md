/* Guidance for AI coding assistants working on this repository */

# Repo snapshot

This repository is a small data-processing assignment built around a single Jupyter notebook: `data_processing_main.ipynb` and a `data/` folder containing CSVs (`lms_loan_daily.csv`, `feature_clickstream.csv`, `features_financials.csv`, `features_attributes.csv`). The notebook initializes a local `pyspark` `SparkSession` and performs ETL-style transformations and exploratory analysis.

# What to change and why

- Prefer editing or adding standalone Python modules (`*.py`) for reusable transformations instead of making many changes directly in the notebook cells. If you must change the notebook, keep high-level orchestration in notebook and move reusable logic to `.py` files for testability.
- Keep data files in `data/` and do not check-in derived artifacts. The `.gitignore` already excludes common virtualenv and notebook checkpoints.

# Important patterns & conventions (from this repo)

- Single-entry notebook: `data_processing_main.ipynb` is the primary sequence for data ingestion, Spark initialization, and processing. Example: Spark is created with `pyspark.sql.SparkSession.builder.master("local[*]")` and `spark.sparkContext.setLogLevel("ERROR")`.
- Data source files are CSVs in `data/`. Code in the notebook loads these directly via `pandas` or `pyspark` (look for `pd.read_csv` or `spark.read.csv`).
- Dates are configured with string variables at the top of the notebook (e.g., `snapshot_date_str`, `start_date_str`, `end_date_str`). Respect those when adding date-based logic.

# Developer workflows (how I, the AI, should modify & test code)

- Local development: run code within the notebook or create small `*.py` scripts and run them with the system Python. The project does not include a `requirements.txt`; assume `pyspark`, `pandas`, `numpy`, and `matplotlib` are used and should be installed in the environment.
- To run notebook cells interactively, open `data_processing_main.ipynb` in VS Code or Jupyter. For scripts, use PowerShell on Windows, e.g.:  
```powershell
# install deps (example)
pip install pyspark pandas numpy matplotlib python-dateutil
# run a script
python path\to\script.py
```

# What to look for when editing

- Keep Spark initialization local and idempotent: reuse the existing `SparkSession` pattern. Avoid changing `master("local[*]")` unless adding cluster support.
- When adding new modules, export pure functions that accept/return `pyspark.sql.DataFrame` or `pandas.DataFrame`. This makes unit testing possible.
- Avoid hard-coded absolute paths; use `os.path.join` and relative paths from the repository root. Example data path: `data/features_financials.csv`.

# Integration points & external dependencies

- Primary external dependency: `pyspark`. The code expects access to a local Spark runtime (the notebook starts a local SparkSession). Other libs: `pandas`, `numpy`, `matplotlib`, `dateutil`.
- No external services, databases, or network calls are present in the repo. All data is local CSV files under `data/`.

# Examples (patterns to follow)

- Spark session pattern (copy exactly):
```python
import pyspark
spark = pyspark.sql.SparkSession.builder \
    .appName("dev") \
    .master("local[*]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
```
- Date-config pattern (top of notebook):
```python
snapshot_date_str = "2023-01-01"
start_date_str = "2023-01-01"
end_date_str = "2025-11-01"
```

# Constraints & things AI should not assume

- There is no test harness or CI config in the repo — do not add heavy build/CI changes without asking. Keep changes minimal and easy to run locally.
- Do not remove the CSV data files; they are the single source of truth for this assignment.

# If you change files, be explicit

- When creating new scripts, add a short note at the top explaining how to run them and which notebook cells they replace. If you modify the notebook, leave a markdown cell explaining the change.

-- End of guidance --
