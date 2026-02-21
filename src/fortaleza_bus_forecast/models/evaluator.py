"""
Model Evaluator — Metrics computation and baseline predictions.

Provides consistent metric calculation (R², RMSE, MAE, MAPE) and
naive baseline models for contextualizing ML performance.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    r2_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
)

from ..config import METRIC_NAMES


def get_performance(model, X_test, Y_test) -> list:
    """
    Evaluate a fitted model on test data.

    Parameters:
        model:  Fitted scikit-learn compatible estimator
        X_test: Test features
        Y_test: True target values

    Returns:
        [r2, rmse, mae, mape]
    """
    y_pred = model.predict(X_test)
    return get_performance_from_predictions(Y_test, y_pred)


def get_performance_from_predictions(Y_test, y_pred) -> list:
    """
    Compute metrics from raw predictions (no model needed).

    Parameters:
        Y_test: True target values
        y_pred: Predicted values

    Returns:
        [r2, rmse, mae, mape]
    """
    mse = mean_squared_error(Y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(Y_test, y_pred)
    mae = mean_absolute_error(Y_test, y_pred)
    mape = mean_absolute_percentage_error(Y_test, y_pred)
    return [r2, rmse, mae, mape]


def performance_to_dataframe(perf: list, model_name: str = "model") -> pd.DataFrame:
    """Wrap a performance list into a labeled DataFrame row."""
    return pd.DataFrame([perf], columns=METRIC_NAMES, index=[model_name])


def baseline_mean_prediction(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    group_cols: list,
    target_col: str = "validations_per_hour",
) -> tuple:
    """
    Naive baseline: predict the training-set group mean.

    For each test row, predicts the average target observed in training for
    the same combination of group_cols (e.g., ['hora', 'd_semana']).
    Falls back to the global training mean for unseen groups.

    Parameters:
        train_df:   Training DataFrame
        test_df:    Test DataFrame
        group_cols: Columns to group by (e.g., ['hora', 'd_semana'])
        target_col: Target column name

    Returns:
        (y_true, y_pred) as numpy arrays
    """
    group_means = train_df.groupby(group_cols)[target_col].mean()
    global_mean = train_df[target_col].mean()

    test_keys = test_df[group_cols].apply(tuple, axis=1)
    y_pred = test_keys.map(group_means).fillna(global_mean).values
    y_true = test_df[target_col].values

    return y_true, y_pred
