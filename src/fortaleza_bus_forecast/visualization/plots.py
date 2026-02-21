"""
Plots — Standardized visualization functions for the project.

Generates thesis-quality figures with consistent styling for:
- Predicted vs actual values
- Hourly/daily ridership patterns
- Model performance comparisons
- Feature importance (SHAP or bar charts)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Optional

from ..config import METRIC_NAMES, IMAGES_DIR


def setup_thesis_style():
    """Apply thesis-consistent matplotlib styling (LaTeX serif fonts)."""
    try:
        plt.rc("text", usetex=True)
    except Exception:
        pass  # LaTeX not available — use default renderer
    plt.rc("font", family="serif", size=16)
    plt.rc("axes", linewidth=2, labelpad=5)
    plt.rc("figure", figsize=(14, 6))


def plot_predictions_vs_actual(
    y_true,
    y_pred,
    title: str = "Predicted vs Actual",
    n_points: int = 168,
    save_path: Optional[str] = None,
    ax=None,
):
    """
    Plot predicted vs actual values over time (first n_points).

    Parameters:
        y_true:    True target values
        y_pred:    Predicted values
        title:     Plot title
        n_points:  Number of points to display (168 = 1 week of hourly data)
        save_path: If set, save figure to this path
        ax:        Matplotlib axes (creates new figure if None)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(20, 8))

    n = min(n_points, len(y_true), len(y_pred))
    x = range(n)

    ax.plot(x, np.array(y_true)[:n], color="blue", label="Actual", linewidth=2)
    ax.plot(x, np.array(y_pred)[:n], color="red", label="Predicted", linewidth=2, alpha=0.8)
    ax.set_xlabel("Hours")
    ax.set_ylabel("Validations per Hour")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=150)

    return ax


def plot_hourly_pattern(
    df: pd.DataFrame,
    line: Optional[int] = None,
    target_col: str = "validations_per_hour",
    save_path: Optional[str] = None,
    ax=None,
):
    """
    Plot average hourly ridership pattern (0–23h).

    Parameters:
        df:         DataFrame with 'hora' and target columns
        line:       If set, filter to this bus line
        target_col: Target column name
        save_path:  If set, save figure
        ax:         Matplotlib axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))

    data = df.copy()
    if line is not None:
        data = data[data["linha"] == line]

    hourly = data.groupby("hora")[target_col].mean()

    ax.bar(hourly.index, hourly.values, color="steelblue", alpha=0.8)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel(f"Avg {target_col}")
    ax.set_title(f"Hourly Ridership Pattern{f' — Line {line}' if line else ''}")
    ax.set_xticks(range(24))

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=150)

    return ax


def plot_model_comparison(
    performance_df: pd.DataFrame,
    metric: str = "R2",
    title: str = "Model Comparison",
    save_path: Optional[str] = None,
    ax=None,
):
    """
    Horizontal bar chart comparing models on a given metric.

    Parameters:
        performance_df: DataFrame with model names as index and metric columns
        metric:         Which metric to plot (R2, RMSE, MAE, MAPE)
        title:          Plot title
        save_path:      If set, save figure
        ax:             Matplotlib axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, max(4, len(performance_df) * 0.5)))

    sorted_df = performance_df.sort_values(metric, ascending=(metric != "R2"))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(sorted_df)))

    ax.barh(sorted_df.index, sorted_df[metric], color=colors)
    ax.set_xlabel(metric)
    ax.set_title(title)
    ax.grid(True, axis="x", alpha=0.3)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=150)

    return ax


def plot_feature_importance(
    feature_names: list,
    importances: np.ndarray,
    title: str = "Feature Importance",
    top_n: int = 15,
    save_path: Optional[str] = None,
    ax=None,
):
    """
    Horizontal bar chart of feature importances.

    Parameters:
        feature_names: List of feature names
        importances:   Array of importance values (SHAP mean |value| or similar)
        title:         Plot title
        top_n:         Show only top N features
        save_path:     If set, save figure
        ax:            Matplotlib axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.4)))

    # Sort and take top N
    idx = np.argsort(importances)[-top_n:]
    ax.barh(
        [feature_names[i] for i in idx],
        importances[idx],
        color="coral",
    )
    ax.set_xlabel("Importance")
    ax.set_title(title)
    ax.grid(True, axis="x", alpha=0.3)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=150)

    return ax
