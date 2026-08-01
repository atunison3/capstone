import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_config, load_local_config


if __name__ == "__main__":
    # Get the data path
    config = load_config()

    # Local config
    local_config = Path("config.local.toml")
    data_path = Path(load_local_config(local_config)["data_path"]) / "prod"

    df = load_full_dataframe(data_path, config)
    print(df["NCSL Classification"].unique())
    for column in df.columns:
        print(column)

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
    X_train[config["binary_features"]] = (X_train[config["binary_features"]] - 1).astype(int)

    X_train = sm.add_constant(X_train, has_constant="add")

    print(X_train[["Phone call", "In person", "Race_2", "Email or text message"]].head())
    feature_names = X_train.columns

    # # Fit a logistic regression model
    # model = sm.Logit(y_train, X_train).fit()
    # print(model.summary())

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
    """
    #       + Q("Outreach Y/N")
    #        + Q("Outreach Y/N") * C(Q("NCSL Classification"))
    model = smf.logit(formula=formula, data=df).fit()
    print(model.summary())
