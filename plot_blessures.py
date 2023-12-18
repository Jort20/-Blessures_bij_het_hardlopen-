import pandas as pd

# Lees de twee bestanden in Pandas DataFrames
df_filtered = pd.read_csv("hardloop.tsv", delimiter='\t')
df2 = pd.read_csv("blessures.tsv", delimiter='\t')

df1 = df_filtered[df_filtered['TQR'].notna() & (df_filtered['TQR'] != 0)]

# Laat alleen de gewenste kolommen zien
df1 = df1[["DATES","TQR", "RPE", "DURATION", "SLEEP", "PERSON_ID", "ID", "TQR_OF_RPE"]]

# Toon het resulterende DataFrame

# Voeg de twee DataFrames samen op basis van de gemeenschappelijke kolommen "PERSON_ID" en "ID"
result = pd.merge(df1, df2, how='inner', on=['PERSON_ID'])
result['DATES'] = pd.to_datetime(result['DATES'], format='%d-%b-%y')
# Laat de samengevoegde gegevens zien
print(result)
