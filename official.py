import pandas as pd
import panel as pn
import hvplot.pandas
import holoviews as hv

# Lees de CSV-file in
df_filtered = pd.read_csv('hardloop.tsv', delimiter='\t')

# Filter de rijen waarin 'TQR' gelijk is aan 0 of niet ingevuld
df = df_filtered[df_filtered['TQR'].notna() & (df_filtered['TQR'] != 0)]

# Laat alleen de gewenste kolommen zien
df = df[["DATES","MOMENT", "TQR", "RPE", "DURATION", "SLEEP", "PERSON_ID", "ID", "TQR_OF_RPE"]]

# Voeg een nieuwe kolom 'COLOR' toe aan het DataFrame op basis van de datumperiodes
df['DATES'] = pd.to_datetime(df['DATES'], format='%d-%b-%y')
df['blessure'] = 'laat_alles_zien'  # Standaardkleur

df['ACUTE_WORKLOAD'] = df.groupby('PERSON_ID')['DURATION'].transform(lambda x: x * df['RPE'])
df['CHRONIC_WORKLOAD'] = df.groupby('PERSON_ID')['DURATION'].transform(lambda x: x.rolling(window=28).sum()) * df['RPE']

# Load injury information from TSV file
injury_info_df = pd.read_csv("blessures.tsv", sep='\t')

# Convert date columns to datetime format
injury_info_df['DATE_START'] = pd.to_datetime(injury_info_df['DATE_START'], format='%d-%b-%y')
injury_info_df['DATE_END'] = pd.to_datetime(injury_info_df['DATE_END'], format='%d-%b-%y')

# Iterate over rows and update the existing DataFrame
for index, row in injury_info_df.iterrows():
    start_date = row['DATE_START']
    end_date = row['DATE_END']
    condition = (df['PERSON_ID'] == row['PERSON_ID']) & (df['DATES'] >= start_date) & (df['DATES'] <= end_date)
    df.loc[condition, 'blessure'] = row['DIAGNOSE']

def plot_workloads(person_id, metric, line_color):
    selected_person_data = df.copy()[df['PERSON_ID'] == person_id]

    plot = selected_person_data.hvplot.line(
        x='DATES', y=metric, groupby='blessure',
        title=f'{metric} voor PERSON_ID {person_id}',
        xlabel='Datum', ylabel=f'{metric} waarde',
        grid=True, width=800, height=400, rot=45,
        line_color=line_color
    )

    plot.opts(shared_axes=False)

    return plot
def plot_data(person_id, metric, line_color):
    # Maak een kopie van het DataFrame om de originele gegevens ongewijzigd te houden
    selected_person_data = df.copy()[df['PERSON_ID'] == person_id]
    
    if metric == 'DURATION':
        plot = selected_person_data.hvplot.line(
            x='DATES', y='DURATION', groupby='blessure',
            title=f'Duur per dag voor PERSON_ID {person_id}',
            xlabel='Datum', ylabel='Duur (minuten)',
            grid=True, width=800, height=400, rot=45,
            line_color=line_color  # Hier voegen we de door de gebruiker gekozen kleur toe
        )
    else:
        plot = selected_person_data.hvplot.line(
            x='DATES', y=metric, groupby='blessure',
            title=f'inspanning voor PERSON_ID {person_id}',
            xlabel='Datum', ylabel='Waarde',
            grid=True, width=800, height=400, rot=45,
            line_color=line_color  # Hier voegen we de door de gebruiker gekozen kleur toe
        )

    # Zorg ervoor dat de y-aslimieten onafhankelijk zijn
    plot.opts(shared_axes=False)

    return plot

def box_plot_data(metric):
    if metric == 'RPE':
        box_plot = df[df['RPE'] > 0].hvplot.box(y='RPE', by='MOMENT', title='Boxplot van RPE per MOMENT')
    elif metric == 'TQR':
        box_plot = df[df['TQR'] > 0].hvplot.box(y='TQR', by='MOMENT', title='Boxplot van TQR per MOMENT')
    else:
        return None

    return box_plot


# Lijst met beschikbare PERSON_ID's
person_ids = df['PERSON_ID'].unique().tolist()

# Lijst met beschikbare metingen (TQR, RPE, DURATION)
metrics = ['TQR', 'RPE', 'DURATION']
metrics_box = ['TQR', 'RPE']
metric_acute = ['TQR', 'RPE', 'DURATION', 'ACUTE_WORKLOAD','CHRONIC_WORKLOAD']
box_metric_selector = pn.widgets.Select(name='Selecteer Meting (Boxplot)', options=metrics_box)

# Maak keuzelijsten voor PERSON_ID en meting
person_selector_1 = pn.widgets.Select(name='Selecteer PERSON_ID (Plot 1)', options=person_ids)
metric_selector_1 = pn.widgets.Select(name='Selecteer Meting (Plot 1)', options=metrics)

person_selector_2 = pn.widgets.Select(name='Selecteer PERSON_ID (Plot 2)', options=person_ids)
metric_selector_2 = pn.widgets.Select(name='Selecteer Meting (Plot 2)', options=metrics)

person_selector_acute = pn.widgets.Select(name='Selecteer PERSON_ID (Plot 2)', options=person_ids)
metric_selector_acute = pn.widgets.Select(name='Selecteer Meting (Plot 2)', options=metric_acute)

color_picker_1 = pn.widgets.ColorPicker(name='Kies Kleur', value='#1f77b4')  # Standaardkleur
color_picker_2 = pn.widgets.ColorPicker(name='Kies Kleur', value='#ff7f0e')  # Standaardkleur
color_picker_3 = pn.widgets.ColorPicker(name='Kies Kleur', value='#ff7f0e')


person_selector_3 = pn.widgets.Select(name='Selecteer PERSON_ID (Plot 2)', options=person_ids)
# Voeg de plot en de keuzelijsten toe aan de app
@pn.depends(person_id=person_selector_1, metric=metric_selector_1, line_color=color_picker_1)
def update_plot_1(person_id, metric, line_color):
    plot = plot_data(person_id, metric, line_color)
    return plot

@pn.depends(person_id=person_selector_2, metric=metric_selector_2, line_color=color_picker_2)
def update_plot_2(person_id, metric, line_color):
    plot = plot_data(person_id, metric, line_color)
    return plot

@pn.depends(metric=box_metric_selector)
def update_box_plot(metric):
    box_plot = box_plot_data(metric)
    return box_plot

@pn.depends(person_id=person_selector_acute, metric_acute=metric_selector_acute, line_color=color_picker_3)
def update_acute_plot(person_id, metric_acute, line_color):
    plot = plot_workloads(person_id=person_id, metric=metric_acute, line_color=line_color)
    return plot

app = pn.Column(
    '# Interactieve Lijn- en Boxplots',
    '## TQR, RPE, en DUUR per dag per ID',
    pn.Column(
        pn.Row(
            person_selector_1,
            metric_selector_1,
            color_picker_1,
            update_plot_1
        ),
        pn.Row(
            person_selector_2,
            metric_selector_2,
            color_picker_2,
            update_plot_2
        )
    ),
    pn.Row(
        box_metric_selector,
        update_box_plot
    ),
    pn.Row(
        person_selector_acute,  # Aangepast naar person_selector_acute
        metric_selector_acute,  # Aangepast naar metric_selector_acute
        color_picker_3,  # Aangepast naar color_picker_2
        update_acute_plot  # Aangepast naar update_acute_plot
    )
)


# Start de Panel-app
app.show()
#app.save(filename='interactive_plots.html', embed=True)

