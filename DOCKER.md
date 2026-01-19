# Docker workflow

The repository now exposes one `Dockerfile` and a shared `requirements.txt`. The image installs the packages required by all scripts (`streamlit`, `pandas`, `numpy`, `matplotlib`, `scipy`) so whichever tool you run (`stats.py`, `data_overview.py`, `subset_analysis.py`, `dashboard.py`, etc.) executes against the same environment.

## Build the image

```bash
docker build -t miraclib-analysis .
```

## Run individual scripts

You can run any script by mounting the workspace and specifying the script name. For example, to regenerate the diagnostics summary:

```bash
docker run --rm -v "$PWD":/app -w /app miraclib-analysis python stats.py
```

To print the baseline melanoma subset:

```bash
docker run --rm -v "$PWD":/app -w /app miraclib-analysis python subset_analysis.py
```

## Run the dashboard

The Streamlit dashboard can be served from inside the container:

```bash
docker run --rm -p 8501:8501 -v "$PWD":/app -w /app miraclib-analysis \
    streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

Then open `http://localhost:8501` in the browser (or whichever host port you map).

## Notes

- The CSV data file `cell-count.csv` lives inside the workspace, so make sure it is present before running the container.  
- The default `CMD ["python3"]` is just a placeholder; always specify the script name (or Streamlit command) when running the container.  
