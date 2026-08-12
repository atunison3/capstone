# Informal Change Log

## andy/fix-mapping

### Config

1. Remapped 1 = "Yes" and 2 = "No" in config.
2. Removed *Outreach Y/N* from *voter_outreach_columns*.
3. TODO: map 7 to an education.

### data_cleaning.py

1. Reversed voting from `(df["TS_g2024"] == 7).astype(int)` to `(df["TS_g2024"] != 7).astype(int)`.
2. Started the revamp.
a. Moved the requesting of data to the new `setup_project.py`.
b. Made functions of loading data as simple as reading in csv files from the `.data` directory.

### setup_project.py

1. Created this with some basic functions to help the user set up the project.
2. Guides the user through downloading the CES data.
3. Installs the manually created NCSL data.
4. Requests the FIPS data. This assumes the FIPS data won't change location. The site seems trustworthy.
5. Added many logging functions.

### helper_functions.py

1. Added a setup_logger function. This is used to create a logger (helpful for troubleshooting) but not necessary.

### report_fig1_real.py

1. Added commas to `ORDER` for consistency.

### testing

1. Testing is changing and very much in-work.
