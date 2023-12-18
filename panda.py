import pandas as pd

# Lees de TSV-file in met behulp van pd.read_csv
file_path = 'hardloop_blessures_export.tsv'  # Vervang 'jouw_bestandsnaam.tsv' door de daadwerkelijke bestandsnaam
df = pd.read_csv(file_path, sep='\t', quotechar='"', index_col=0)

# Toon de eerste paar rijen van de DataFrame om te controleren of het correct is ingelezen
print(df.head())

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
df['DIAGNOSE'].value_counts().plot(kind='bar')
plt.title('Frequentie van Diagnoses')
plt.xlabel('Diagnose')
plt.ylabel('Aantal gevallen')
plt.show()

plt.figure(figsize=(10, 6))
df.groupby('DIAGNOSE')['TIME_LOSS'].mean().sort_values().plot(kind='barh')
plt.title('Gemiddelde tijdverlies per Diagnose')
plt.xlabel('Gemiddelde tijdverlies (dagen)')
plt.ylabel('Diagnose')
plt.show()

df['DATE_START'] = pd.to_datetime(df['DATE_START'])
df['DATE_END'] = pd.to_datetime(df['DATE_END'])


