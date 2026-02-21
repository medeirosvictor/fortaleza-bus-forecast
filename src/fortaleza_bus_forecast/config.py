"""
Configuration — Feature lists, constants, and paths used across the project.
"""

import os

# ── Paths ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "dados-para-modelos")
PERFORMANCES_DIR = os.path.join(PROJECT_ROOT, "performances")
PREDICTIONS_DIR = os.path.join(PROJECT_ROOT, "predict-vs-real")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

# ── Random seed ──
RANDOM_SEED = 42

# ── Target column ──
TARGET_COL = "validations_per_hour"

# ── Feature sets ──
# Standard features (one-hot day-of-week + cyclical hour)
FEATURE_NAMES_STANDARD = [
    "hour_sin", "hour_cos",
    "d_mes", "mes",
    "feriado", "vespera_feriado",
    "domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado",
]

# Cyclical features (all temporal features encoded as sin/cos pairs)
FEATURE_NAMES_CYCLICAL = [
    "hour_sin", "hour_cos",
    "d_mes_sin", "d_mes_cos",
    "d_semana_sin", "d_semana_cos",
    "d_ano_sin", "d_ano_cos",
    "mes_sin", "mes_cos",
    "semana_do_mes_sin", "semana_do_mes_cos",
    "feriado", "vespera_feriado",
]

# One-hot day-of-week column names
DAY_OF_WEEK_COLS = ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"]

# Metric column names (order matters — matches get_performance output)
METRIC_NAMES = ["R2", "RMSE", "MAE", "MAPE"]

# ── Supported years ──
SUPPORTED_YEARS = [2015, 2018, 2020]

# ── Data coverage per year (inclusive month ranges) ──
YEAR_COVERAGE = {
    2015: (1, 12),   # Full year
    2018: (1, 8),    # Jan–Aug only
    2020: (3, 12),   # Mar–Dec only (COVID, no Jan/Feb data)
}
