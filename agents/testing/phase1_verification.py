"""
Phase 1 Verification — Run this to check all Phase 1 items are in good shape.

Usage:
    python agents/testing/phase1_verification.py
"""
import os
import sys
import glob
import json

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Resolve project root (two levels up from this script)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    status = "✅" if condition else "❌"
    if not condition:
        FAIL += 1
    else:
        PASS += 1
    msg = f"  {status} {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)


print("=" * 60)
print("PHASE 1 VERIFICATION")
print("=" * 60)

# ── 1.1 Environment & Dependencies ──────────────────────────
print("\n── 1.1 Environment & Dependencies ──")
check("requirements.txt exists", os.path.exists("requirements.txt"))

readme_exists = os.path.exists("README.md")
check("README.md exists", readme_exists)
if readme_exists:
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    check("README has English content", "Passenger Boarding Prediction" in readme)
    check("README has PT-BR section", "Sobre o Projeto" in readme)
    check("README mentions Python 3.10+", "3.10" in readme)

# ── 1.2 Naming Consistency ──────────────────────────────────
print("\n── 1.2 Naming Consistency ──")
expected_notebooks = [
    "01-data-processing.ipynb",
    "02-data-visualization.ipynb",
    "03-cross-year-comparison.ipynb",
    "04-results.ipynb",
    "2015/05-per-line-models-2015.ipynb",
    "2015/06-per-line-models-2015-cyclical.ipynb",
    "other-related-notebooks/07-time-series-framing.ipynb",
    "other-related-notebooks/08-neural-net-time-series.ipynb",
    "other-related-notebooks/09-neural-net-standard.ipynb",
]
for nb in expected_notebooks:
    check(f"Notebook {nb}", os.path.exists(nb))

old_patterns = [
    "Modelo-*", "Comparativo-*", "Data-Visualization*",
    "Resultados*", "Tratamento-*", "PrevEmbarque-*",
    "Simples-*", "RedeNeural-*",
]
old_found = []
for pattern in old_patterns:
    old_found.extend(glob.glob(pattern))
    old_found.extend(glob.glob(f"2015/{pattern}"))
    old_found.extend(glob.glob(f"other-related-notebooks/{pattern}"))
# Filter out non-.ipynb matches
old_found = [f for f in old_found if f.endswith(".ipynb")]
check("No old-named notebooks", len(old_found) == 0, f"found: {old_found}" if old_found else "clean")

# ── 1.3 Code Deduplication ──────────────────────────────────
print("\n── 1.3 Code Deduplication ──")

# week_of_month canonical in helper-funs.py
with open("helper_scripts/helper-funs.py", "r") as f:
    hf_content = f.read()
check("helper-funs.py has canonical week_of_month()", "def week_of_month" in hf_content)

for script in ["helper_scripts/data_builder.py", "helper_scripts/zero_filler.py"]:
    with open(script, "r") as f:
        content = f.read()
    has_local_def = "def week_of_month" in content
    imports_helper = "helper-funs" in content and "week_of_month" in content
    check(f"{script} imports (not defines) week_of_month", imports_helper and not has_local_def)

# variables.py re-exports
with open("variables.py", "r") as f:
    var_content = f.read()
check("Root variables.py re-exports from 2015/", "spec_from_file_location" in var_content)

# ── 1.4 Random Seeds ────────────────────────────────────────
print("\n── 1.4 Random Seeds ──")
for nb_path in sorted(expected_notebooks):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    code = " ".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    has_seed = "random_state" in code or "RANDOM_SEED" in code or "random.seed" in code
    needs_seed = any(kw in code for kw in [
        "RandomForest", "train_test_split", "XGB", "DecisionTree",
        "tensorflow", "tf.", "GradientBoosting", "Bagging", "Ridge",
    ])
    ok = has_seed or not needs_seed
    short_name = os.path.basename(nb_path)
    check(f"{short_name} seed status", ok, f"has_seed={has_seed}, needs={needs_seed}")

# ── 1.5 Git Hygiene ─────────────────────────────────────────
print("\n── 1.5 Git Hygiene ──")
with open(".gitignore", "r") as f:
    gi = f.read()
check(".ipynb_checkpoints in .gitignore", "ipynb_checkpoints" in gi)
check("__pycache__ in .gitignore", "__pycache__" in gi)
check("model-data/README.md exists", os.path.exists("model-data/README.md"))

# ── Additional Checks ───────────────────────────────────────
print("\n── Additional Checks ──")

# University name
if readme_exists:
    check("No UFC references in README", "UFC" not in readme)
    check("UNIFOR referenced in README", "UNIFOR" in readme, f"{readme.count('UNIFOR')} occurrences")

# Header comments on Python files
py_files = [
    "helper_scripts/data_builder.py",
    "helper_scripts/zero_filler.py",
    "helper_scripts/helper-funs.py",
    "2015/variables.py",
    "variables.py",
]
for py in py_files:
    with open(py, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
    check(f"{py} has header comment", first_line.startswith("# =="))

# Notebook markdown headers
for nb_path in expected_notebooks:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    md_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
    has_header = md_cells and "".join(md_cells[0]["source"]).startswith("# ")
    short_name = os.path.basename(nb_path)
    check(f"{short_name} has markdown header", has_header)

# ── Summary ─────────────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"RESULTS: {PASS}/{total} passed, {FAIL} failed")
if FAIL == 0:
    print("🎉 Phase 1 fully verified!")
else:
    print(f"⚠️  {FAIL} item(s) need attention.")
print("=" * 60)

sys.exit(0 if FAIL == 0 else 1)
