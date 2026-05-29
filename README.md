# Equipment Selection and Hero Optimization for Epic Seven
## using Python / Jupyter Notebook

### About

This program supports hero/equipment optimization for the mobile game Epic Seven. It helps sort through equipment and quickly regear heroes during free unequipment events.

The tool runs from the **command line** or from the provided **Jupyter notebooks** in `prog/`.

Gear and hero data live in `inp/master_data.json`, compatible with [Compeanansi's OCR Tool](https://github.com/compeanansi/epic7) or JSON output from [Zarroc's Gear Optimizer](https://github.com/Zarroc2762/E7-Gear-Optimizer).

### Requirements

- **Python 3.8+**
- Dependencies: `pip install -r requirements.txt`
- Optional (notebooks): `pip install -e ".[notebook]"`
- Optional (tests): `pip install -e ".[dev]"`

### Project layout

```
inp/          Input data (gear JSON, hero stats, build templates)
outp/         Generated outputs (pickles, CSV, updated JSON)
prog/
  config.py   Runtime settings (GEAR_LIMIT, etc.)
  paths.py    Project path constants
  e7_gear/    Core library (scoring, combos, optimize_hero)
  item_potential.py   Step 1: score all gear
  run_hero_opt.py     Step 2: optimize heroes (CLI)
tests/        Pytest suite
```

Existing scripts can still use `import fx_lib as fx` — it re-exports the `e7_gear` package.

### Quickstart (CLI)

From the `prog/` directory:

```bash
# 1. Score gear inventory
python item_potential.py

# 2. Optimize heroes (uses inp/character_inputs.yaml)
python run_hero_opt.py
```

Results are written to `outp/gear_reco.csv` and `outp/upd_items.json`.

### Quickstart (Notebook)

1. Put your gear in `inp/master_data.json`
2. Open `prog/Hero_Optimization_Notebook.ipynb`
3. Run cells in order (the first cell runs `item_potential.py`)

A detailed walkthrough is also at [jupyter-walkthrough](https://ja-bru.github.io/E7_Py_Gear_Selector/jupyter-walkthrough.html).

### Configuration

Edit `prog/config.py` or override in the notebook before running:

| Setting | Purpose |
|---------|---------|
| `GEAR_LIMIT` | Top-N gear per slot used in search (affects speed) |
| `AUTO_ADJ_GEAR_LIMIT` | Auto-reduce limit when combos exceed 1M |
| `NO_EQUIPPED_GEAR` | Use unequipped gear only |
| `MANUAL_SELECTION` | Prompt to pick gear vs fully automated (CLI) |

Build templates and hero order: `inp/character_inputs.yaml`

### Running tests

From the repository root:

```bash
py -3 -m pytest tests -v
```

### Features

- Hero optimization with weighted stat targets
- Batch optimization for multiple heroes (CLI)
- Set include/exclude filters
- Unequipped, unlocked, or all gear modes
- Minimum enhance level for stat projection
- EE / imprint / artifact bonuses via hero `BonusStats`

### Restrictions

- Only outputs complete sets
- No main-stat picker for Necklace / Ring / Boots yet
- CP calculation excludes skill enhance and artifact CP
- Assumes max awakened hero at level 50 or 60
- Character base stats from `inp/character_data.csv` (refresh via `python api_get.py`)
