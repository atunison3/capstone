# from __future__ import annotations

# from dataclasses import dataclass

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from scipy.optimize import minimize
from scipy.special import expit

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_config

warnings.filterwarnings("ignore")


config = load_config()
data_path = Path(config["data_path"]) / "dev"
df = load_full_dataframe(data_path)

FEATURES = [
    "Outreach Y/N",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
    "NCSL Classification",
]

TARGET = "Voted"

# Keep only the columns needed by the model.
model_df = df[FEATURES + [TARGET]].dropna().copy()

# Convert features and target to NumPy arrays.
X = model_df[FEATURES]
y = model_df[TARGET].to_numpy(dtype=float)

# Get the dummies
X = pd.get_dummies(X, dtype=float, drop_first=True)
feature_names = list(X.columns)
X = X.to_numpy(dtype=float)

# Add a column of ones for the intercept.
X = np.column_stack([np.ones(len(X)), X])

# Start all coefficients at zero.
initial_coefficients = np.zeros(X.shape[1], dtype=float)

# Minimize the negative log-likelihood directly.
result = minimize(  # type: ignore
    lambda coefficients: np.sum(np.logaddexp(0.0, X @ coefficients) - y * (X @ coefficients)),
    x0=initial_coefficients,
    method="BFGS",  # Is there a way to use Gauss-Newton?
)

if not result.success:
    raise RuntimeError(f"Optimization failed: {result.message}")

coefficients = np.asarray(result.x, dtype=float)

# Predicted probabilities and classes.
probabilities = expit(X @ coefficients)
predictions = (probabilities >= 0.5).astype(int)

model_df["Predicted Probability"] = probabilities
model_df["Prediction"] = predictions

# Print model coefficients.
print("\n\n")
print(f"Intercept: {coefficients[0]:.4f}")

for feature, coefficient in zip(FEATURES, coefficients[1:]):
    print(f"{feature}: {coefficient:.4f}")

# Simple training accuracy.
accuracy = (model_df["Prediction"] == model_df[TARGET]).mean()

print(f"\n\nAccuracy: {accuracy:.2%}")
print(model_df.head())
