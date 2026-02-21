# ==============================================================================
# Helper Functions — Shared utilities for model evaluation and date features
#
# Used by notebooks to compute performance metrics (R2, RMSE, MAE, MAPE) and
# calculate the week-of-month for a given date.
# ==============================================================================

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
import numpy as np


def get_performance(model, X_test, Y_test):
    """
    Evaluate a trained model on test data and return [R2, RMSE, MAE, MAPE].
    
    Parameters:
        model: A fitted scikit-learn compatible estimator
        X_test: Test features (DataFrame or array)
        Y_test: True target values
    
    Returns:
        List of [r2, rmse, mae, mape]
    """
    y_test_predict = model.predict(X_test)
    mse = mean_squared_error(Y_test, y_test_predict)
    rmse = np.sqrt(mse)
    r2 = r2_score(Y_test, y_test_predict)
    mae = mean_absolute_error(Y_test, y_test_predict)
    mape = mean_absolute_percentage_error(Y_test, y_test_predict)
    
    performance_scoring = [r2, rmse, mae, mape]
    return performance_scoring


def get_performance_from_predictions(Y_test, y_pred):
    """
    Compute [R2, RMSE, MAE, MAPE] from raw predictions (no model needed).

    Parameters:
        Y_test: True target values
        y_pred: Predicted values (array-like, same length as Y_test)

    Returns:
        List of [r2, rmse, mae, mape]
    """
    mse = mean_squared_error(Y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(Y_test, y_pred)
    mae = mean_absolute_error(Y_test, y_pred)
    mape = mean_absolute_percentage_error(Y_test, y_pred)
    return [r2, rmse, mae, mape]


def baseline_mean_prediction(train_df, test_df, group_cols, target_col='validations_per_hour'):
    """
    Naive baseline: predict the training-set mean of the target for each group.

    For each row in test_df, the prediction is the average target value observed
    in train_df for the same combination of group_cols (e.g. ['hora', 'd_semana']).
    Rows with unseen groups fall back to the global training mean.

    Parameters:
        train_df:   Training DataFrame (must contain group_cols + target_col)
        test_df:    Test DataFrame (must contain group_cols + target_col)
        group_cols: List of column names to group by (e.g. ['hora', 'd_semana'])
        target_col: Name of the target column

    Returns:
        (y_true, y_pred) — numpy arrays aligned to test_df rows
    """
    import pandas as pd

    group_means = train_df.groupby(group_cols)[target_col].mean()
    global_mean = train_df[target_col].mean()

    # Map each test row to its group mean (or global mean if unseen)
    test_keys = test_df[group_cols].apply(tuple, axis=1)
    y_pred = test_keys.map(group_means).fillna(global_mean).values
    y_true = test_df[target_col].values

    return y_true, y_pred


# Days per month lookup (non-leap year)
d_31 = [1, 3, 5, 7, 8, 10, 12]
d_30 = [4, 6, 9, 11]


from datetime import datetime
import datetime
import calendar


def week_of_month(tgtdate):
    """
    Returns the week of the month (1-indexed) for a given date.
    
    Accepts both pandas Timestamps and plain datetime objects.
    Finds the first day of the month where (day - weekday > 0), then uses
    modulo-7 arithmetic to determine the week number.
    """
    # Handle pandas Timestamp objects
    if hasattr(tgtdate, 'to_pydatetime'):
        tgtdate = tgtdate.to_pydatetime()

    days_this_month = calendar.mdays[tgtdate.month]
    for i in range(1, days_this_month):
        d = datetime.datetime(tgtdate.year, tgtdate.month, i)
        if d.day - d.weekday() > 0:
            startdate = d
            break
    
    return (tgtdate - startdate).days // 7 + 1
