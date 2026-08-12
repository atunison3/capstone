# Informal Change Log

## andy/fix-mapping

### Config

1. Remapped 1 = "Yes" and 2 = "No" in config.
2. Removed *Outreach Y/N* from *voter_outreach_columns*.
3. TODO: map 7 to an education.

### data_cleaning.py

1. Reversed voting from `(df["TS_g2024"] == 7).astype(int)` to `(df["TS_g2024"] != 7).astype(int)`.

### report_fig1_real.py

1. Added commas to `ORDER` for consistency.
