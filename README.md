# MLE_Assignment-1

This repository contains a small data-processing assignment (single-entry notebook) for the "Machine Learning Engineering" course. It demonstrates local ETL-style transformations using PySpark and Pandas on CSV data files.

## Contents

- `data_processing_main.ipynb` - Primary Jupyter notebook that initializes a local PySpark `SparkSession` and performs data ingestion, ETL transformations, and exploratory analysis.
- `main.py` - Optional script entrypoint (if present) for running some processing outside the notebook.
- `utils/` - Reusable Python modules that contain data processing functions for bronze/silver/gold tables. Prefer importing and testing functions from here rather than editing notebook cells.
- `data/` - Source CSV data files used by the notebook:
  - `feature_clickstream.csv`
  - `features_attributes.csv`
  - `features_financials.csv`
  - `lms_loan_daily.csv`
- `datamart/` - Example output directories (bronze/silver/gold) used by the assignment.
- `Dockerfile`, `docker-compose.yaml` - Optional container definitions for packaging the environment.
- `requirements.txt` - Python dependencies used by the project.

## Quick start (local development)

1. Create and activate a virtual environment (recommended):

   powershell
   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Open the notebook in VS Code or Jupyter and run cells. The notebook creates a local SparkSession using the pattern below and sets the Spark log level to `ERROR`:

```python
import pyspark
spark = pyspark.sql.SparkSession.builder \
    .appName("dev") \
    .master("local[*]") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
```

4. Data files are read from the `data/` directory. Do not check-in derived artifacts. Use `utils/` modules for reusable transformations and for easier testing.

## Docker (optional)

If you prefer running inside a container, build the image and run with Docker / Docker Compose. The repository includes a `Dockerfile` and `docker-compose.yaml`. Example:

```powershell
# Build image (example)
docker build -t mle_assignment .
# Run container (example)
docker run --rm -it -v ${PWD}:/app mle_assignment
```

Adjust the commands to match your Docker setup on Windows (use PowerShell or Docker Desktop).

## Conventions and notes

- Keep reusable logic in `utils/*.py` and avoid large blocks of processing inside the notebook. This makes unit testing and validation straightforward.
- Use relative paths (e.g., `data/features_financials.csv`) when referring to files in code.
- Date variables in the notebook are configured as strings near the top (for example `snapshot_date_str`, `start_date_str`, `end_date_str`) — keep that pattern if adding date-based logic.
- The notebook uses `pyspark`, `pandas`, `numpy`, and optional plotting libraries. See `requirements.txt` for the exact packages.

## Running scripts / tests

There is no test harness included by default. For quick checks, import functions from `utils/` and run small Python scripts or use the notebook to exercise processing steps.

## Contact / License

This repository is part of a course assignment. No license is included; add one if you plan to reuse or publish the code.

---

Notes: This README summarizes repository structure and the recommended development workflow taken from `.github/copilot-instructions.md`. If you want, I can also extract key functions from the notebook into unit-testable `.py` modules and add a minimal test runner.
