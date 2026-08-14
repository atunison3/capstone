import statsmodels.formula.api as smf
import warnings
from pandas import DataFrame
from statsmodels.discrete.discrete_model import BinaryResultsWrapper

from capstone.data_cleaning import load_full_dataframe
from capstone.helper_functions import load_model_config

warnings.filterwarnings("ignore")


def train_model(df: DataFrame) -> BinaryResultsWrapper:
    """Trains the model"""

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

    return model


if __name__ == "__main__":

    # Load the config
    config = load_model_config()

    # Get the full dataframe
    df = load_full_dataframe(config)

    # Train the model
    model = train_model(df)
    print(model.summary())
