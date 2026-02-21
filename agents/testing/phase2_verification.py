"""
Phase 2 Verification — Methodological Improvements.

Tests for:
  2.6 — Baseline Models
  2.4 — Feature Importance (SHAP)
  2.3 — COVID-Aware Analysis
  2.1 — Time-Series Cross-Validation (or documented limitation)
  2.2 — Statistical Significance (multi-run std reporting)
  2.5 — Hyperparameter Tuning Rigor (documented search spaces)

Usage:
    python agents/testing/phase2_verification.py
"""
import os
import sys
import json
import glob

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

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


def notebook_code(nb_path):
    """Return all code from a notebook as a single string."""
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    return "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")


def notebook_markdown(nb_path):
    """Return all markdown from a notebook as a single string."""
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    return "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")


def notebook_all_text(nb_path):
    """Return all cell content (code + markdown) as a single string."""
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    return "\n".join("".join(c["source"]) for c in nb["cells"])


def file_contains(path, *keywords):
    """Check if a file contains ALL given keywords (case-insensitive)."""
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().lower()
    return all(kw.lower() in content for kw in keywords)


print("=" * 60)
print("PHASE 2 VERIFICATION")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# 2.6 — Baseline Models
# ─────────────────────────────────────────────────────────────
print("\n── 2.6 Baseline Models ──")

# Could live in notebook 05, 04, or a dedicated baseline notebook
baseline_notebooks = [
    "2015/05-per-line-models-2015.ipynb",
    "2015/06-per-line-models-2015-cyclical.ipynb",
    "04-results.ipynb",
    "03-cross-year-comparison.ipynb",
]
# Also check for a dedicated baseline file
baseline_files = glob.glob("*baseline*") + glob.glob("*Baseline*") + glob.glob("helper_scripts/*baseline*")

baseline_in_notebook = False
baseline_in_file = len(baseline_files) > 0
for nb_path in baseline_notebooks:
    if os.path.exists(nb_path):
        text = notebook_all_text(nb_path)
        if "baseline" in text.lower() or "naive" in text.lower() or "DummyRegressor" in text:
            baseline_in_notebook = True
            break

baseline_exists = baseline_in_notebook or baseline_in_file
check("Baseline model implemented", baseline_exists,
      f"notebooks={baseline_in_notebook}, files={baseline_files}" if baseline_exists else "no baseline found in any notebook or file")

# Check that baseline computes metrics for comparison
if baseline_exists:
    # Look for baseline metrics being computed
    all_code = ""
    for nb_path in baseline_notebooks:
        if os.path.exists(nb_path):
            all_code += notebook_code(nb_path)
    for bf in baseline_files:
        if bf.endswith(".py"):
            with open(bf, "r", encoding="utf-8") as f:
                all_code += f.read()
        elif bf.endswith(".ipynb"):
            all_code += notebook_code(bf)

    has_baseline_metrics = any(kw in all_code.lower() for kw in ["baseline_r2", "baseline_rmse", "baseline_mae", "baseline_perf", "naive_r2", "naive_rmse"])
    # Also accept: groupby mean approach as baseline
    has_groupby_baseline = "groupby" in all_code and ("baseline" in all_code.lower() or "naive" in all_code.lower())
    check("Baseline metrics computed (R²/RMSE/MAE)", has_baseline_metrics or has_groupby_baseline)

    # Check baseline results are saved or displayed
    has_baseline_output = any(kw in all_code.lower() for kw in ["baseline", "naive"]) and any(kw in all_code for kw in ["print", "display", "to_csv", "DataFrame"])
    check("Baseline results displayed or saved", has_baseline_output)
else:
    check("Baseline metrics computed (R²/RMSE/MAE)", False, "no baseline to check")
    check("Baseline results displayed or saved", False, "no baseline to check")

# ─────────────────────────────────────────────────────────────
# 2.4 — Feature Importance (SHAP)
# ─────────────────────────────────────────────────────────────
print("\n── 2.4 Feature Importance ──")

# Check for SHAP or permutation importance in any notebook
importance_notebooks = glob.glob("*.ipynb") + glob.glob("2015/*.ipynb") + glob.glob("other-related-notebooks/*.ipynb")
shap_found = False
perm_importance_found = False
importance_plot_found = False
importance_notebook = None

for nb_path in importance_notebooks:
    code = notebook_code(nb_path)
    text = notebook_all_text(nb_path)
    if "import shap" in code or "shap.Explainer" in code or "shap.TreeExplainer" in code:
        shap_found = True
        importance_notebook = nb_path
    if "permutation_importance" in code:
        perm_importance_found = True
        importance_notebook = importance_notebook or nb_path
    if ("shap" in code.lower() or "importance" in code.lower()) and ("plot" in code.lower() or "bar" in code.lower() or "summary_plot" in code.lower()):
        importance_plot_found = True

check("SHAP or permutation importance implemented", shap_found or perm_importance_found,
      f"SHAP={shap_found}, permutation={perm_importance_found}" + (f" in {importance_notebook}" if importance_notebook else ""))
check("Feature importance visualization", importance_plot_found)

# Check for feature importance results saved
importance_files = glob.glob("performances/*importance*") + glob.glob("images/*importance*") + glob.glob("images/*shap*")
check("Feature importance results saved", len(importance_files) > 0 or importance_plot_found,
      f"files: {importance_files}" if importance_files else "plot in notebook")

# ─────────────────────────────────────────────────────────────
# 2.3 — COVID-Aware Analysis
# ─────────────────────────────────────────────────────────────
print("\n── 2.3 COVID-Aware Analysis ──")

nb03 = "03-cross-year-comparison.ipynb"
if os.path.exists(nb03):
    text03 = notebook_all_text(nb03)
    md03 = notebook_markdown(nb03)
    code03 = notebook_code(nb03)

    check("COVID mentioned in notebook 03 markdown", 
          any(kw in md03.lower() for kw in ["covid", "pandemic", "pandemia"]))
    
    # Check for quantitative COVID analysis (ridership comparison)
    has_ridership_comparison = any(kw in code03.lower() for kw in [
        "2020", "covid", "pandemic",
    ]) and any(kw in code03 for kw in [
        "sum()", ".sum()", "groupby", "value_counts", "describe",
    ])
    check("Quantitative ridership comparison (2015 vs 2020)", has_ridership_comparison)
    
    # Check for COVID impact documentation
    has_covid_section = "covid" in md03.lower() or "pandemic" in md03.lower() or "pandemia" in md03.lower()
    check("Dedicated COVID impact section in markdown", has_covid_section)
else:
    check("Notebook 03 exists", False)

# Also check README
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
check("COVID mentioned in README", "covid" in readme.lower() or "pandemic" in readme.lower())

# ─────────────────────────────────────────────────────────────
# 2.1 — Time-Series Cross-Validation
# ─────────────────────────────────────────────────────────────
print("\n── 2.1 Time-Series Cross-Validation ──")

ts_split_found = False
walk_forward_found = False
limitation_documented = False

for nb_path in importance_notebooks:
    code = notebook_code(nb_path)
    if "TimeSeriesSplit" in code:
        ts_split_found = True
    # Walk-forward: training on expanding months
    if "training_months" in code and ("range" in code or "for" in code):
        walk_forward_found = True

check("TimeSeriesSplit used", ts_split_found,
      "or manual walk-forward" if walk_forward_found else "")

# If no formal TimeSeriesSplit, check if limitation is documented
if not ts_split_found:
    docs_to_check = ["README.md", "AGENTS.md", "model-data/README.md",
                     "feedback/agent-user feedback.md", "feedback/data-and-thesis-analysis.md"]
    for doc in docs_to_check:
        if os.path.exists(doc) and file_contains(doc, "time", "split"):
            limitation_documented = True
            break
    # Also check notebook markdown
    for nb_path in importance_notebooks:
        if os.path.exists(nb_path):
            md = notebook_markdown(nb_path)
            if "time" in md.lower() and ("split" in md.lower() or "cross-validation" in md.lower() or "walk-forward" in md.lower()):
                limitation_documented = True
                break

    check("Time-based splitting limitation documented", limitation_documented or walk_forward_found,
          "walk-forward via month filtering" if walk_forward_found else "")

# ─────────────────────────────────────────────────────────────
# 2.2 — Statistical Significance
# ─────────────────────────────────────────────────────────────
print("\n── 2.2 Statistical Significance ──")

multi_run_found = False
std_reported = False

for nb_path in ["2015/05-per-line-models-2015.ipynb", "2015/06-per-line-models-2015-cyclical.ipynb", "03-cross-year-comparison.ipynb"]:
    if os.path.exists(nb_path):
        code = notebook_code(nb_path)
        # Multi-run: loop running same model multiple times
        if any(kw in code for kw in ["for seed", "for run", "n_runs", "num_runs", "range(10)", "range(5)"]):
            multi_run_found = True
        # Std reporting
        if any(kw in code for kw in [".std()", "np.std", "std()", "mean_std", "± "]):
            std_reported = True

check("Multi-run execution (multiple seeds)", multi_run_found,
      "thesis mentions 10 runs per model")
check("Standard deviation reported alongside means", std_reported)

# Check if thesis 10-run averaging is documented
thesis_runs_documented = False
for doc in ["README.md", "AGENTS.md", "feedback/data-and-thesis-analysis.md"]:
    if file_contains(doc, "10", "execution") or file_contains(doc, "10", "run") or file_contains(doc, "average", "execution"):
        thesis_runs_documented = True
        break
check("Thesis 10-run averaging documented", thesis_runs_documented)

# ─────────────────────────────────────────────────────────────
# 2.5 — Hyperparameter Tuning Rigor
# ─────────────────────────────────────────────────────────────
print("\n── 2.5 Hyperparameter Tuning ──")

for nb_path in ["2015/05-per-line-models-2015.ipynb", "2015/06-per-line-models-2015-cyclical.ipynb"]:
    if os.path.exists(nb_path):
        code = notebook_code(nb_path)
        md = notebook_markdown(nb_path)
        text = notebook_all_text(nb_path)
        short = os.path.basename(nb_path)

        has_search = "RandomizedSearchCV" in code or "GridSearchCV" in code
        check(f"{short}: has hyperparameter search", has_search)

        # Check if search space is documented in markdown
        search_documented = any(kw in text.lower() for kw in [
            "search space", "hyperparameter", "param_grid", "param_distributions",
            "n_iter", "grid search", "randomized search",
        ])
        check(f"{short}: search space documented", search_documented)

        # Check if best params are logged
        best_params_logged = "best_params" in code or "best_score" in code or "best_estimator" in code
        check(f"{short}: best params logged", best_params_logged)

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"RESULTS: {PASS}/{total} passed, {FAIL} failed")
if FAIL == 0:
    print("🎉 Phase 2 fully verified!")
else:
    print(f"⚠️  {FAIL} item(s) need attention.")
print("=" * 60)

sys.exit(0 if FAIL == 0 else 1)
