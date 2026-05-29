"""Project path constants resolved from the repository root."""

from pathlib import Path

# prog/paths.py -> repository root is the parent of prog/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INP_DIR = PROJECT_ROOT / "inp"
OUTP_DIR = PROJECT_ROOT / "outp"
PROG_DIR = PROJECT_ROOT / "prog"

MASTER_DATA_JSON = INP_DIR / "master_data.json"
CHARACTER_INPUTS_YAML = INP_DIR / "character_inputs.yaml"
CHARACTER_DATA_CSV = INP_DIR / "character_data.csv"
GEAR_TIERS_CSV = INP_DIR / "gear_tiers.csv"

EQUIP_POTENTIAL_CSV = OUTP_DIR / "equip_potential.csv"
EQUIP_POTENTIAL_PKL = OUTP_DIR / "equip_potential.pkl"
EQUIP_POTENTIAL_JSON = OUTP_DIR / "equip_potential.json"
UPD_ITEMS_PKL = OUTP_DIR / "upd_items.pkl"
UPD_ITEMS_JSON = OUTP_DIR / "upd_items.json"
GEAR_RECO_CSV = OUTP_DIR / "gear_reco.csv"
REMOVE_LIST_CSV = OUTP_DIR / "remove_list.csv"
