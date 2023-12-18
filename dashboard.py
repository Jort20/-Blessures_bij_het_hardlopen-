import pandas as pd
import panel as pn
pn.extension('tabulator')
import hvplot.pandas

file_path = 'hardloop.tsv'

# Read the TSV file, specifying the date format for the 'DATES' column and handling quoting
df = pd.read_csv(file_path, sep='\t', dayfirst=True, infer_datetime_format=True, quoting=3, quotechar='"', na_values=['', '""'])

# Clean up column names by removing leading and trailing whitespaces and double quotes
df.columns = df.columns.str.strip().str.strip('"')

# Replace empty strings with NaN in the entire DataFrame
df.replace('', pd.NA, inplace=True)
df.replace('""', pd.NA, inplace=True)

# Drop rows with any missing values in the 'DATES' column
df = df.dropna(subset=['DATES'])

old_df = df
print(old_df)
# Create a new column 'duration_tqr_pair' by combining 'DURATION' and 'TQR' columns
df['duration_tqr_pair'] = df['DURATION'].astype(str) + '_' + df['TQR'].astype(str)

# Create a new column 'value_counts' to store the frequency of each pair of values
df['value_counts'] = df['duration_tqr_pair'].map(df['duration_tqr_pair'].value_counts())

# Display the DataFrame


# Fill NAs with 0s
df = df.fillna(0)

scatter_plot = df[df['DURATION'] > 0].hvplot.scatter(
    x='DURATION', y='TQR', c='black', alpha=0.5,
    title='Training Duur versus Intensiteit (TQR)', size='value_counts',  # Specify the 'size' parameter
)

box_plot = df[df['RPE'] > 0].hvplot.box(y='RPE', by='MOMENT', title='RPE naar Moment van de Dag (Ochtend vs. Avond)')

table = pn.widgets.DataFrame(old_df, height=400, width=800)
# Layout using Template with a toggle theme button
template = pn.template.FastListTemplate(
    title='hardlopers data dashboard', 
    sidebar=[pn.pane.Markdown("# dit data dashboard bevat"), 
             pn.pane.Markdown("#### DATES: Datum van de hardlooptraining"),
             pn.pane.Markdown("#### MOMENT: Geeft aan wanneer de training plaatsvond ochtend (0) of avond (a)."),
             pn.pane.Markdown("#### TQR: De door de hardlopers aangegeven intensiteit van de training"),
             pn.pane.Markdown("####  De door de hardlopers aangegeven mate van inspanning of Rate of Perceived Exertion."),
             pn.pane.Markdown("####  DURATION: Duur van de hardlooptraining"),
             pn.pane.Markdown("#### SLEEP: De hoeveelheid slaap die de hardloper heeft gehad voorafgaand aan de training.")],
    main=[pn.Row(pn.Column(scatter_plot, box_plot), table)],

    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)
template.show()
template.servable()
