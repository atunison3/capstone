from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize
from scipy.special import expit

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_config


FEATURES = [
    "Outreach Y/N",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
    "NCSL Classification",
]

TARGET = "Voted"


@dataclass
class LogisticRegressionResult:
    coefficients: np.ndarray
    feature_names: list[str]
    optimization_result: object
    reference_columns: list[str]


def prepare_voting_data(
    df: pd.DataFrame, features: list[str] = FEATURES, target: str = TARGET
) -> tuple[pd.DataFrame, pd.Series]:
    """Clean the predictors and target used by the voting model."""
    required_columns = features + [target]

    # Check if dataframe has any missing columns
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")

    if not pd.api.types.is_integer_dtype(df[target]):
        raise TypeError("Model target must be type int.")

    model_df = df[required_columns].copy()
    model_df = model_df.dropna(subset=[target])

    model_df[target] = model_df[target].astype(int)

    # Data integrity: verify target only has 0 and 1
    if set(model_df[target].unique()) != {0, 1}:
        raise ValueError(f"{target!r} must contain both binary classes 0 and 1.")

    X = model_df[features].copy()
    y = model_df[target].copy()

    return X, y


def fit_preprocessor(X: pd.DataFrame, features: list[str] = FEATURES) -> tuple[pd.DataFrame, list[str]]:
    """
    Impute missing values and one-hot encode categorical predictors.

    The first category for each predictor is omitted and becomes the
    reference category.
    """
    X_clean = X.copy()

    for column in X_clean.columns:
        mode = X_clean[column].mode(dropna=True)

        if mode.empty:
            fill_value = "Missing"
        else:
            fill_value = mode.iloc[0]

        X_clean[column] = X_clean[column].fillna(fill_value)
        X_clean[column] = X_clean[column].astype(str)

    encoded = pd.get_dummies(
        X_clean,
        columns=features,
        drop_first=True,
        dtype=float,
    )

    return encoded, encoded.columns.tolist()


def transform_predictors(
    X: pd.DataFrame,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Apply preprocessing to new observations.

    Columns absent from the new data are added with zeros, while unknown
    categories are ignored.
    """
    X_clean = X.copy()

    for column in FEATURES:
        mode = X_clean[column].mode(dropna=True)

        if mode.empty:
            fill_value = "Missing"
        else:
            fill_value = mode.iloc[0]

        X_clean[column] = X_clean[column].fillna(fill_value)
        X_clean[column] = X_clean[column].astype(str)

    encoded = pd.get_dummies(
        X_clean,
        columns=FEATURES,
        drop_first=True,
        dtype=float,
    )

    return encoded.reindex(
        columns=feature_names,
        fill_value=0.0,
    )


def add_intercept(X: np.ndarray) -> np.ndarray:
    """Add a column of ones for the logistic-regression intercept."""
    intercept = np.ones((X.shape[0], 1))

    return np.hstack((intercept, X))


def negative_log_likelihood(
    coefficients: np.ndarray,
    X: np.ndarray,
    y: np.ndarray,
    l2_penalty: float = 0.0,
) -> float:
    """
    Calculate the penalized negative log-likelihood.

    The intercept is not regularized.
    """
    linear_predictor = X @ coefficients
    probabilities = expit(linear_predictor)

    epsilon = np.finfo(float).eps

    probabilities = np.clip(
        probabilities,
        epsilon,
        1.0 - epsilon,
    )

    log_likelihood = np.sum(y * np.log(probabilities) + (1 - y) * np.log(1 - probabilities))

    penalty = 0.5 * l2_penalty * np.sum(coefficients[1:] ** 2)

    return -log_likelihood + penalty


def negative_log_likelihood_gradient(
    coefficients: np.ndarray,
    X: np.ndarray,
    y: np.ndarray,
    l2_penalty: float = 0.0,
) -> np.ndarray:
    """Calculate the gradient of the negative log-likelihood."""
    probabilities = expit(X @ coefficients)

    gradient = X.T @ (probabilities - y)

    penalty_gradient = np.zeros_like(coefficients)
    penalty_gradient[1:] = l2_penalty * coefficients[1:]

    return gradient + penalty_gradient


def fit_logistic_regression(
    df: pd.DataFrame,
    l2_penalty: float = 0.0,
) -> LogisticRegressionResult:
    """Fit a binary logistic regression model using SciPy."""
    X_raw, y = prepare_voting_data(df)

    X_encoded, feature_names = fit_preprocessor(X_raw)

    X_matrix = add_intercept(X_encoded.to_numpy(dtype=float))
    y_array = y.to_numpy(dtype=float)

    initial_coefficients = np.zeros(X_matrix.shape[1])

    result = minimize(
        fun=negative_log_likelihood,
        x0=initial_coefficients,
        args=(X_matrix, y_array, l2_penalty),
        jac=negative_log_likelihood_gradient,
        method="BFGS",
        options={
            "maxiter": 1_000,
            "gtol": 1e-6,
        },
    )

    if not result.success:
        raise RuntimeError("Logistic regression optimization failed: " f"{result.message}")

    return LogisticRegressionResult(
        coefficients=result.x,
        feature_names=["Intercept", *feature_names],
        optimization_result=result,
        reference_columns=feature_names,
    )


def predict_probabilities(
    model: LogisticRegressionResult,
    X: pd.DataFrame,
) -> np.ndarray:
    """Predict the probability that each person voted."""
    encoded_feature_names = model.feature_names[1:]

    X_encoded = transform_predictors(
        X,
        feature_names=encoded_feature_names,
    )

    X_matrix = add_intercept(X_encoded.to_numpy(dtype=float))

    return expit(X_matrix @ model.coefficients)


def predict(
    model: LogisticRegressionResult,
    X: pd.DataFrame,
    threshold: float = 0.5,
) -> np.ndarray:
    """Predict binary voting outcomes."""
    probabilities = predict_probabilities(model, X)

    return (probabilities >= threshold).astype(int)


def coefficient_table(
    model: LogisticRegressionResult,
) -> pd.DataFrame:
    """Return the model coefficients and odds ratios."""
    return (
        pd.DataFrame(
            {
                "feature": model.feature_names,
                "coefficient": model.coefficients,
                "odds_ratio": np.exp(model.coefficients),
            }
        )
        .sort_values(
            "odds_ratio",
            ascending=False,
        )
        .reset_index(drop=True)
    )


config = load_config()
data_path = Path(config["data_path"]) / "dev"
df = load_full_dataframe(data_path)

model = fit_logistic_regression(df, l2_penalty=0.0)
