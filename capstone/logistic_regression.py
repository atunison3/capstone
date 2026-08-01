import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
from pathlib import Path

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_config, load_local_config

warnings.filterwarnings("ignore")


if __name__ == "__main__":
    # Get the data path
    config = load_config()

    # Local config
    local_config = Path("config.local.toml")
    data_path = Path(load_local_config(local_config)["data_path"]) / "prod"

    # Get the full dataframe
    df = load_full_dataframe(data_path, config)

    # Split the data
    X_train = df[config["features"]]
    y_train = df[config["target"]]

    # Get dummies
    X_train = pd.get_dummies(
        X_train,
        columns=config["multiclass_features"],
        drop_first=True,  # Not including an intercept
        dtype=int,
    )
    # X_train[config["binary_features"]] = (X_train[config["binary_features"]] - 1).astype(int)
    print(X_train.dtypes)

    # Add a constant
    X_train = sm.add_constant(X_train, has_constant="add")

    # Retain the feature names (might only be needed for sklearn)
    feature_names = X_train.columns

    # Fit logistic regression model using formula
    formula = """
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
    """
    model = smf.logit(formula=formula, data=df).fit()
    print(model.summary())
