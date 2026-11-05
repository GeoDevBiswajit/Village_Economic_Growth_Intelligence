# Village_Economic_Growth_Intelligence
An intelligence system that identifies the top 100 villages in India that have shown the highest economic growth over the last 5 years, using satellite data and any publicly available datasets you find relevant.

village-economic-growth-intelligence/
│
├── README.md
├── methodology.md
│
├── data/
│   ├── input_data/
│   │   ├──csvs
│   │   └──vectore_file
│   └── output/
│       ├──results
│       └──vectore
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_EDA_and_modeling.ipynb
│
├── src/
│   ├── config.py
│   ├── eda.py
│   ├── extract.py
│   ├── processes.py
│   ├── score.py
│   ├── visualize.py
│   └── run_pipeline.py
│
│
└── presentation/
    └── village_growth_intelligence.pdf

## Architecture (SRP)
- `config.py`: Centralized parameters, file paths, and weights.
- `extract.py`: GEE extraction and Drive export.
- `process.py`: Geometry parsing, merging, and spatial/growth filtering.
- `score.py`: Feature scaling and weighted sum calculation.
- `visualize.py`: Static choropleth (Matplotlib) and Interactive Web Map (Folium).
- `run_pipeline.py`: Main orchestrator script.

## How to Run
1. Update paths in `config.py`.
2. Run `python run_pipeline.py`.
   - If CSVs are missing, it triggers GEE exports.
   - Once CSVs are in the input directory, running it again completes processing and visualization.
