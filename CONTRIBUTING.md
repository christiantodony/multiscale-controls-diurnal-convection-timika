# Contributing

Please open an issue before changing a scientific default. A proposed method
change should state its physical-time window, sampling interval, missing-data
treatment, expected event counts, and whether it reproduces or intentionally
departs from the published analysis.

Install development dependencies and run checks:

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src scripts tests
```

Do not commit restricted station observations, credentials, large input files,
or local filesystem paths. Contributions that add a publication figure should
also add a regression test or an expected summary statistic where practical.

