# ==============================================================================
# Variables — Holiday definitions and shared constants
#
# Re-exports from 2015/variables.py with generic aliases expected by
# 03-cross-year-comparison.ipynb.
#
# Each holiday/eve entry: [name, day, month]
# Includes Brazilian national holidays + Ceara/Fortaleza local holidays.
#
# Note: The generic `feriados` / `vesperas` lists default to 2018 holidays,
# which is what the original root variables.py contained. Per-year lists
# (feriados_2015, etc.) are also available for year-specific usage.
# ==============================================================================

import importlib.util as _ilu
import os as _os

# Load 2015/variables.py directly by path to avoid circular import
_spec = _ilu.spec_from_file_location(
    "variables_2015",
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '2015', 'variables.py')
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export all definitions
day_of_week_translator = _mod.day_of_week_translator

feriados_2015 = _mod.feriados_2015
vesperas_2015 = _mod.vesperas_2015
feriados_2018 = _mod.feriados_2018
vesperas_2018 = _mod.vesperas_2018
feriados_2020 = _mod.feriados_2020
vesperas_2020 = _mod.vesperas_2020

# Generic aliases (used by cross-year comparison notebook as flat lists)
feriados = feriados_2018
vesperas = vesperas_2018
