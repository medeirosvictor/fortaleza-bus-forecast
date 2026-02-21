"""
Model Trainer — Build, train, and evaluate ML models with a consistent interface.

Provides a model suite (all algorithms used in the thesis) and utilities for
per-line model training with multi-run averaging.
"""

import warnings
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    BaggingRegressor,
    GradientBoostingRegressor,
    StackingRegressor,
)
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, TimeSeriesSplit

from ..config import RANDOM_SEED, METRIC_NAMES, TARGET_COL
from .evaluator import get_performance, performance_to_dataframe


def build_model_suite(random_state: int = RANDOM_SEED) -> dict:
    """
    Return a dict of {name: model_instance} for all thesis models.

    Does NOT include XGBoost/LightGBM to avoid hard dependency —
    use add_xgboost() and add_lightgbm() to extend.
    """
    rf = RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1)

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=0.5),
        "SVR": SVR(),
        "Decision Tree": DecisionTreeRegressor(random_state=random_state),
        "Random Forest": rf,
        "Bagging (Decision Tree)": BaggingRegressor(
            estimator=DecisionTreeRegressor(),
            n_estimators=50,
            random_state=random_state,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            random_state=random_state,
        ),
    }
    return models


def add_xgboost(models: dict, random_state: int = RANDOM_SEED) -> dict:
    """Add XGBoost to a model suite. Requires xgboost to be installed."""
    import xgboost as xg

    models["XGBoost"] = xg.XGBRegressor(
        n_estimators=100, seed=random_state, eval_metric="mae", booster="gbtree"
    )
    return models


def add_lightgbm(models: dict, random_state: int = RANDOM_SEED) -> dict:
    """Add LightGBM to a model suite. Requires lightgbm to be installed."""
    import lightgbm as lgb

    models["LightGBM"] = lgb.LGBMRegressor(
        n_estimators=100, random_state=random_state, verbose=-1
    )
    return models


def add_stacking(models: dict, base_model_names: list = None, random_state: int = RANDOM_SEED) -> dict:
    """
    Add a Stacking ensemble using existing models as base estimators.

    Parameters:
        models:           Existing model dict to pick base estimators from
        base_model_names: Names of models to use as base (default: RF, Bagging, GB)
        random_state:     Random seed for the meta-learner
    """
    if base_model_names is None:
        base_model_names = ["Random Forest", "Bagging (Decision Tree)", "Gradient Boosting"]

    estimators = [
        (name, make_pipeline(models[name]))
        for name in base_model_names
        if name in models
    ]

    if len(estimators) < 2:
        raise ValueError(f"Need at least 2 base models for stacking, got {len(estimators)}")

    try:
        import xgboost as xg
        meta = xg.XGBRegressor(n_estimators=100, seed=random_state)
    except ImportError:
        meta = GradientBoostingRegressor(n_estimators=100, random_state=random_state)

    models["Stacking Ensemble"] = StackingRegressor(
        estimators=estimators,
        final_estimator=meta,
        n_jobs=-1,
    )
    return models


def train_and_evaluate(
    model,
    X_train,
    X_test,
    Y_train,
    Y_test,
    model_name: str = "model",
) -> pd.DataFrame:
    """
    Fit a model and return a performance DataFrame row.

    Returns:
        DataFrame with columns [R2, RMSE, MAE, MAPE] and model_name as index.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(X_train, Y_train)

    perf = get_performance(model, X_test, Y_test)
    return performance_to_dataframe(perf, model_name)


def train_per_line(
    df: pd.DataFrame,
    feature_names: list,
    lines: list = None,
    models: dict = None,
    test_size: float = 0.2,
    n_runs: int = 10,
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Train all models on each bus line, averaging over multiple runs.

    Parameters:
        df:            Full DataFrame with all lines
        feature_names: List of feature column names
        lines:         Bus lines to train on (default: all unique lines)
        models:        Model suite dict (default: build_model_suite())
        test_size:     Test split ratio
        n_runs:        Number of runs per model (different seeds)
        random_state:  Base random seed

    Returns:
        DataFrame with columns: [linha, model, R2, RMSE, MAE, MAPE,
                                 R2_std, RMSE_std, MAE_std, MAPE_std]
    """
    if models is None:
        models = build_model_suite(random_state)

    if lines is None:
        lines = sorted(df["linha"].unique())

    results = []

    for linha in lines:
        line_data = df[df["linha"] == linha]
        X = line_data[feature_names]
        y = line_data[TARGET_COL]

        if len(X) < 10:
            continue

        for model_name, model_template in models.items():
            run_perfs = []
            for run in range(n_runs):
                seed = random_state + run
                X_train, X_test, Y_train, Y_test = train_test_split(
                    X, y, test_size=test_size, random_state=seed
                )

                # Clone model with new seed if possible
                from sklearn.base import clone
                model = clone(model_template)
                if hasattr(model, "random_state"):
                    model.random_state = seed

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model.fit(X_train, Y_train)

                perf = get_performance(model, X_test, Y_test)
                run_perfs.append(perf)

            perfs = np.array(run_perfs)
            means = perfs.mean(axis=0)
            stds = perfs.std(axis=0)

            results.append({
                "linha": linha,
                "model": model_name,
                "R2": means[0], "RMSE": means[1], "MAE": means[2], "MAPE": means[3],
                "R2_std": stds[0], "RMSE_std": stds[1], "MAE_std": stds[2], "MAPE_std": stds[3],
            })

    return pd.DataFrame(results)
