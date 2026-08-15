# Logistic Regression

Module: `capstone.logistic_regression`

Fits a binary logistic regression for validated turnout (`Voted`) using Patsy formulas via `statsmodels`.

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
from capstone.logistic_regression import train_model

config = load_model_config()
df = load_full_dataframe(config)
model = train_model(df)
print(model.summary())
```

### Notes

- The module sets `warnings.filterwarnings("ignore")` at import time.
- Feature lists in `capstone.config` document the intended analysis columns; the formula in this module is the source of truth for the fitted specification.
