# Intelligent Livestock Management Simulation

A Streamlit dashboard that simulates real-time IoT livestock telemetry: geo-fencing, SVR-based grazing intensity forecasts, and live map/chart updates. Built for Chapter 4 validation of an intelligent livestock management framework.

## Features

- **Live IoT simulation** — Mock collar data (GPS, temperature, humidity, activity) streamed in configurable intervals
- **Geo-fencing** — Point-in-polygon checks against a virtual grazing boundary (Shapely)
- **Predictive analytics** — SVR-style grazing intensity scoring and overgrazing risk alerts
- **Interactive map** — Folium map with fence polygon, trajectory marker, and breach toasts
- **Time-series charts** — Grazing intensity vs. ambient temperature over the simulation run

## Prerequisites

- **Python 3.10+** (3.12 recommended)
- `pip` (bundled with Python)
- A modern web browser (for the Streamlit UI)

## Project structure

```
My-Simulation/
├── app.py                 # Main Streamlit application (run this)
├── app_notebook.ipynb     # Notebook version / development cells
├── requirements.txt       # Python dependencies
├── .gitignore             # Ignores venv/
└── README.md
```

The `venv/` folder is local only and is not committed to git.

## Setup

### 1. Clone or open the project

```bash
cd /path/to/My-Simulation
```

### 2. Create a virtual environment

**Linux / macOS:**

```bash
python3 -m venv venv
```

**Windows (Command Prompt):**

```cmd
python -m venv venv
```

**Windows (PowerShell):**

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

**Linux / macOS:**

```bash
source venv/bin/activate
```

Your shell prompt should show `(venv)`.

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run once (as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install dependencies

With the venv active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. (Optional) Register the venv as a Jupyter kernel

Only needed if you use `app_notebook.ipynb` in Jupyter or VS Code:

```bash
python -m ipykernel install --user --name=my-simulation --display-name="Python (My-Simulation)"
```

Select **Python (My-Simulation)** as the notebook kernel.

## Running the dashboard

With `venv` activated:

```bash
streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in your browser.

### Using the app

1. Adjust **IoT Transmission Interval** and **Total Data Packets** in the sidebar.
2. Click **Run Live IoT Simulation**.
3. Watch KPIs, the map, and charts update in real time.
4. When the run finishes, review the telemetry table at the bottom.

## Jupyter notebook

`app_notebook.ipynb` mirrors `app.py` in cells for experimentation. Streamlit is meant to run as a web app, not inside standard notebook cells; you may see `ScriptRunContext` warnings if you execute Streamlit code in Jupyter.

**Recommended workflow:** develop logic in the notebook if needed, then run the full dashboard with:

```bash
streamlit run app.py
```

To open the notebook (with venv active):

```bash
jupyter notebook app_notebook.ipynb
```

## Deactivating the virtual environment

When you are done:

```bash
deactivate
```

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `command not found: streamlit` | Activate `venv` and run `pip install -r requirements.txt` again |
| `python3: command not found` | Install Python 3.10+ or use `python` instead of `python3` on Windows |
| Map not loading | Allow localhost in the browser; refresh after the first packet |
| PowerShell won’t activate venv | Use `venv\Scripts\Activate.ps1` or Command Prompt `activate.bat` |
| Wrong packages / broken env | Delete `venv`, recreate it, and reinstall from `requirements.txt` |

## Dependencies

| Package | Role |
|---------|------|
| [Streamlit](https://streamlit.io/) | Web dashboard UI |
| [pandas](https://pandas.pydata.org/) | Telemetry tables |
| [NumPy](https://numpy.org/) | Synthetic IoT data |
| [Shapely](https://shapely.readthedocs.io/) | Geo-fence polygon checks |
| [Folium](https://python-visualization.github.io/folium/) | Interactive maps |
| [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) | Folium widgets in Streamlit |
| [Jupyter](https://jupyter.org/) / [ipykernel](https://ipython.readthedocs.io/) | Optional notebook support |

## License

Add your license here if you plan to distribute this project.
