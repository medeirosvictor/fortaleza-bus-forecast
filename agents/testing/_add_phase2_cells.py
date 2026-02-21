"""Add Phase 2 cells (baseline, SHAP, multi-run) to notebook 05."""
import json
import sys
import os

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

nb_path = "2015/05-per-line-models-2015.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

def make_md(source_lines):
    return {"cell_type": "markdown", "metadata": {}, "source": source_lines}

def make_code(source_lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": source_lines}


# ── Find insertion point: after "End Setup / Model Creation" markdown ──
insert_at = None
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "markdown" and "End Setup" in "".join(c["source"]):
        insert_at = i + 1
        break

if insert_at is None:
    print("ERROR: Could not find 'End Setup' markdown cell")
    sys.exit(1)

# Check if baseline already added
all_code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
if "baseline_mean_prediction" in all_code:
    print("Baseline cells already present — skipping baseline insertion")
else:
    baseline_md = make_md([
        "## Baseline Models\n",
        "\n",
        "Before training ML models, establish naive baselines to contextualize how much ML actually helps.\n",
        "\n",
        "**Baseline 1 — Global Mean:** Predict the overall training-set average for every row.  \n",
        "**Baseline 2 — Group Mean:** Predict the training-set average for each (hour, day_of_week) combination.  \n",
        "**Baseline 3 — Detailed Group Mean:** Predict by (hour, day_of_week, month).\n",
        "\n",
        "If XGBoost only beats the group-mean baseline by a small margin, the ML complexity may not be justified.",
    ])

    baseline_code = make_code([
        "# ── 2.6 Baseline Models ──\n",
        "# Naive baselines to contextualize ML model performance\n",
        "import os as _os; import sys as _sys\n",
        "_sys.path.insert(0, _os.path.join('..', 'helper_scripts'))\n",
        "from importlib import import_module as _im\n",
        "_hf = _im('helper-funs')\n",
        "baseline_mean_prediction = _hf.baseline_mean_prediction\n",
        "get_perf_pred = _hf.get_performance_from_predictions\n",
        "\n",
        "# Use same train/test split as the ML models\n",
        "X_bl = line_data_model.filter(feature_names, axis=1)\n",
        "y_bl = line_data_model.validations_per_hour\n",
        "X_train_bl, X_test_bl, _, _ = train_test_split(X_bl, y_bl, test_size=0.2, random_state=5)\n",
        "train_df = line_data_model.loc[X_train_bl.index].copy()\n",
        "test_df = line_data_model.loc[X_test_bl.index].copy()\n",
        "\n",
        "# Baseline 1: Global mean\n",
        "global_mean = train_df['validations_per_hour'].mean()\n",
        "y_pred_global = np.full(len(test_df), global_mean)\n",
        "baseline_global_perf = get_perf_pred(test_df['validations_per_hour'].values, y_pred_global)\n",
        "\n",
        "# Baseline 2: Group mean by (hour, day_of_week)\n",
        "y_true_grp, y_pred_grp = baseline_mean_prediction(train_df, test_df, ['hora', 'd_semana'])\n",
        "baseline_group_perf = get_perf_pred(y_true_grp, y_pred_grp)\n",
        "\n",
        "# Baseline 3: Group mean by (hour, day_of_week, month)\n",
        "y_true_grp2, y_pred_grp2 = baseline_mean_prediction(train_df, test_df, ['hora', 'd_semana', 'mes'])\n",
        "baseline_group2_perf = get_perf_pred(y_true_grp2, y_pred_grp2)\n",
        "\n",
        "baseline_df = pd.DataFrame([\n",
        "    baseline_global_perf,\n",
        "    baseline_group_perf,\n",
        "    baseline_group2_perf,\n",
        "], columns=['R2', 'RMSE', 'MAE', 'MAPE'], index=[\n",
        "    'Baseline: Global Mean',\n",
        "    'Baseline: Mean(hour, weekday)',\n",
        "    'Baseline: Mean(hour, weekday, month)',\n",
        "])\n",
        "\n",
        "print(f'Baseline results for bus line {busline_filter}:')\n",
        "display(baseline_df)\n",
        "baseline_df.to_csv(f'../performances/2015/baseline_linha{busline_filter}.csv')\n",
    ])

    nb["cells"].insert(insert_at, baseline_md)
    nb["cells"].insert(insert_at + 1, baseline_code)
    print(f"Baseline cells inserted at position {insert_at}")
    insert_at += 2  # shift for next insertions


# ── SHAP cell: insert after XGBoost training cell ──
if "import shap" in all_code:
    print("SHAP cell already present — skipping")
else:
    shap_md = make_md([
        "## Feature Importance (SHAP)\n",
        "\n",
        "Use SHAP (SHapley Additive exPlanations) on the trained XGBoost model to identify\n",
        "which features drive predictions the most. Expect `hour` and `day_of_week` to dominate.\n",
        "\n",
        "> Requires `pip install shap`.",
    ])

    shap_code = make_code([
        "# ── 2.4 Feature Importance — SHAP on XGBoost ──\n",
        "try:\n",
        "    import shap\n",
        "    explainer = shap.TreeExplainer(xgb_r)\n",
        "    shap_values = explainer.shap_values(X_test)\n",
        "    print('SHAP Feature Importance (mean |SHAP value|):')\n",
        "    shap_importance = pd.DataFrame({\n",
        "        'feature': feature_names,\n",
        "        'mean_abs_shap': np.abs(shap_values).mean(axis=0)\n",
        "    }).sort_values('mean_abs_shap', ascending=False)\n",
        "    display(shap_importance)\n",
        "    shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=True)\n",
        "except ImportError:\n",
        "    print('shap not installed — run: pip install shap')\n",
    ])

    # Find XGBoost training cell
    shap_inserted = False
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            src = "".join(c["source"])
            if "xgb_r = xg.XGBRegressor" in src and "xgb_r.fit" in src:
                nb["cells"].insert(i + 1, shap_md)
                nb["cells"].insert(i + 2, shap_code)
                shap_inserted = True
                print(f"SHAP cells inserted after cell {i}")
                break

    if not shap_inserted:
        print("WARNING: Could not find XGBoost training cell for SHAP insertion")


# ── Multi-run cell: insert after "All Trained Models in model_list" section ──
if "n_runs" in all_code or "multirun" in all_code:
    print("Multi-run cell already present — skipping")
else:
    multirun_md = make_md([
        "## Multi-Run Evaluation (Statistical Significance)\n",
        "\n",
        "Run each model with multiple random seeds and report mean ± std of metrics.\n",
        "The thesis reports averages of 10 executions — this replicates that approach\n",
        "and adds standard deviation to quantify variance between runs.",
    ])

    multirun_code = make_code([
        "# ── 2.2 Multi-Run Evaluation ──\n",
        "# Run models with different random seeds to get mean ± std\n",
        "n_runs = 10\n",
        "seeds = list(range(42, 42 + n_runs))\n",
        "\n",
        "multirun_results = {name: [] for name in [\n",
        "    'GradientBoosting', 'RandomForest', 'XGBoost', 'Ridge', 'LinearRegression'\n",
        "]}\n",
        "\n",
        "for seed in seeds:\n",
        "    X_tr, X_te, Y_tr, Y_te = train_test_split(X, y, test_size=0.2, random_state=seed)\n",
        "\n",
        "    models_run = {\n",
        "        'LinearRegression': LinearRegression().fit(X_tr, Y_tr),\n",
        "        'Ridge': Ridge(alpha=0.5).fit(X_tr, Y_tr),\n",
        "        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=seed).fit(X_tr, Y_tr),\n",
        "        'GradientBoosting': GradientBoostingRegressor(\n",
        "            n_estimators=300, learning_rate=0.05, max_depth=4, random_state=seed\n",
        "        ).fit(X_tr, Y_tr),\n",
        "        'XGBoost': xg.XGBRegressor(\n",
        "            n_estimators=100, seed=seed, eval_metric='mae', booster='gbtree', verbosity=0\n",
        "        ).fit(X_tr, Y_tr),\n",
        "    }\n",
        "\n",
        "    for name, model in models_run.items():\n",
        "        y_pred = model.predict(X_te)\n",
        "        r2 = r2_score(Y_te, y_pred)\n",
        "        rmse = np.sqrt(mean_squared_error(Y_te, y_pred))\n",
        "        mae = mean_absolute_error(Y_te, y_pred)\n",
        "        mape = mean_absolute_percentage_error(Y_te, y_pred)\n",
        "        multirun_results[name].append([r2, rmse, mae, mape])\n",
        "\n",
        "# Build summary: mean ± std\n",
        "summary_rows = []\n",
        "for name, runs in multirun_results.items():\n",
        "    if not runs:\n",
        "        continue\n",
        "    arr = np.array(runs)\n",
        "    means = arr.mean(axis=0)\n",
        "    stds = arr.std(axis=0)\n",
        "    summary_rows.append({\n",
        "        'Model': name,\n",
        "        'R2_mean': means[0], 'R2_std': stds[0],\n",
        "        'RMSE_mean': means[1], 'RMSE_std': stds[1],\n",
        "        'MAE_mean': means[2], 'MAE_std': stds[2],\n",
        "        'MAPE_mean': means[3], 'MAPE_std': stds[3],\n",
        "    })\n",
        "\n",
        "multirun_df = pd.DataFrame(summary_rows).set_index('Model')\n",
        "multirun_df = multirun_df.sort_values('R2_mean', ascending=False)\n",
        "\n",
        "print(f'Multi-run results ({n_runs} seeds) for bus line {busline_filter}:')\n",
        "display(multirun_df)\n",
        "multirun_df.to_csv(f'../performances/2015/multirun_linha{busline_filter}.csv')\n",
    ])

    # Find "All Trained Models" markdown
    multirun_inserted = False
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "markdown" and "All Trained Models" in "".join(c["source"]):
            # Skip the model_list code cell + get_performance redef cell
            j = i + 1
            while j < len(nb["cells"]) and nb["cells"][j]["cell_type"] != "code":
                j += 1
            # Skip the model_list code cell
            j += 1
            # Skip the get_performance redef cell
            if j < len(nb["cells"]) and "def get_performance" in "".join(nb["cells"][j].get("source", [])):
                j += 1

            nb["cells"].insert(j, multirun_md)
            nb["cells"].insert(j + 1, multirun_code)
            multirun_inserted = True
            print(f"Multi-run cells inserted at position {j}")
            break

    if not multirun_inserted:
        print("WARNING: Could not find insertion point for multi-run cells")


# ── Save ──
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\nNotebook saved. Total cells: {len(nb['cells'])}")
