import pandas as pd

# Load both CSVs
req_df = pd.read_csv("shl_req.csv")
req_df["Assessment URL"] = req_df["Assessment URL"].str.replace("//", "/", regex=False)
req_df.to_csv("shl_req.csv", index=False)