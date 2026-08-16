# Logistic Regression

Module: `capstone.logistic_regression`

Fits a binary logistic regression for validated turnout (`Voted`) using Patsy formulas via `statsmodels`, then reports coefficient tables with an **Expit** column for probability-scale interpretation.

## `train_model`

```python
train_model(df: DataFrame) -> BinaryResultsWrapper
```

### Formula

```text
Voted ~
    C(Education)
  + C(Race)
  + C(Gender)
  + Age
  + Q("In person")
  + Q("Phone call")
  + Q("Email or text message")
  + Q("Letter or postcard")
  + C(Q("NCSL Classification"))
  + Q("In person") * C(Q("NCSL Classification"))
  + Q("Phone call") * C(Q("NCSL Classification"))
  + Q("Email or text message") * C(Q("NCSL Classification"))
  + Q("Letter or postcard") * C(Q("NCSL Classification"))
```

Main effects cover demographics, age, outreach channels, and NCSL voter ID classification. Interaction terms allow outreach effects to vary by voter ID regime.

### Parameters

`df`

Modeling frame from `load_full_dataframe`. Must include the columns referenced in the formula.

### Returns

A fitted `statsmodels` binary results wrapper (`smf.logit(...).fit()`).

### Example

```python
from capstone.helper_functions import load_model_config
from capstone.data_cleaning import load_full_dataframe
from capstone.logistic_regression import train_model, calculate_probabilities

config = load_model_config()
df = load_full_dataframe(config)
model = train_model(df)
calculate_probabilities(model)
```

## `calculate_probabilities`

```python
calculate_probabilities(model: BinaryResultsWrapper) -> None
```

Builds a `summary2()` coefficient table for the fitted model, appends an **Expit** column, and prints the result.

```python
summary = model.summary2()
summary.tables[1]["Expit"] = expit(summary.tables[1]["Coef."])
print(summary)
```

`Expit` is the logistic sigmoid of each log-odds coefficient (`scipy.special.expit`), i.e. \(1 / (1 + e^{-\beta})\).

### Parameters

`model`

Fitted binary results object returned by `train_model`.

### Returns

`None`. Output is written to stdout.

### Notes

- This is what the `capstone` CLI calls after training (via `capstone.analysis.main`). Prefer it over `print(model.summary())` when the Expit column is needed.
- References used in the implementation:
  - [Binary logistic regression interpretation notes](https://019b2da8-edfb-a262-61be-7973c056d9ae.share.connect.posit.cloud/blr-interp.html)
  - [scipy.special.expit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.expit.html)

### Example

```python
from capstone.logistic_regression import train_model, calculate_probabilities

model = train_model(df)
calculate_probabilities(model)
```

## Module notes

- The module sets `warnings.filterwarnings("ignore")` at import time.
- Feature lists in `capstone.config` document the intended analysis columns; the formula in this module is the source of truth for the fitted specification.
- `logistic_regression.main()` loads config, builds the frame, trains, and calls `calculate_probabilities` (same reporting path as the CLI).
