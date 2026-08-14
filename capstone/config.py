from pathlib import Path


DATA_PATH = Path(".data")


FULL_COLUMNS = [
    "Education",
    "Race",
    "Gender",
    "Age",
    "In person",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
    "State FIPS Code",
    "Voted",
]


CATEGORICAL_FEATURES = [
    "Education",
    "Race",
    "Gender",
    "In person",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
    "NCSL Classification",
]


MULTICLASS_FEATURES = [
    "Education",
    "Race",
    "Gender",
    "NCSL Classification",
]


BINARY_FEATURES = [
    "In person",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
]


FEATURES = [
    "Education",
    "Race",
    "Gender",
    "Age",
    "In person",
    "Phone call",
    "Email or text message",
    "Letter or postcard",
    "NCSL Classification",
]


TARGET = "Voted"


# Columns in CES data to be renamed
DEMOGRAPHIC_COLUMNS = {
    "educ": "Education",
    "race": "Race",
    "hispanic": "Hispanic",
    "gender4": "Gender",
    "birthyr": "Birth Year",
}


VOTER_OUTREACH_COLUMNS = {
    "CC24_431b_1": "In person",
    "CC24_431b_2": "Phone call",
    "CC24_431b_3": "Email or text message",
    "CC24_431b_4": "Letter or postcard",
}


STATE_COLUMN = {
    "inputstate": "State FIPS Code",
}


MAPS = {
    "Education": "educ_mapping",
    "Race": "race_mapping",
    "Gender": "gender_mapping",
    "In person": "in_person_mapping",
    "Phone call": "phone_mapping",
    "Email or text message": "email_mapping",
    "Letter or postcard": "letter_mapping",
}


EDUC_MAPPING = {
    1: "No HS degree",
    2: "High school graduate",
    3: "Some college, no degree (yet)",
    4: "2 year college degree",
    5: "4 year college degree",
    6: "Postgraduate degree",
    8: "Skipped",
    9: "Not asked",
}


RACE_MAPPING = {
    1: "White",
    2: "Black",
    3: "Hispanic",
    4: "Asian",
    5: "Native American",
    6: "Two or more races",
    7: "Other",
    8: "Middle Eastern",
}


GENDER_MAPPING = {
    1: "Man",
    2: "Woman",
    3: "Non-binary",
    4: "Other",
}


IN_PERSON_MAPPING = {
    1.0: "Yes",
    2.0: "No",
}


PHONE_MAPPING = {
    1.0: "Yes",
    2.0: "No",
}


EMAIL_MAPPING = {
    1.0: "Yes",
    2.0: "No",
}


LETTER_MAPPING = {
    1.0: "Yes",
    2.0: "No",
}
