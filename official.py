import pandas as pd
import panel as pn
import hvplot.pandas
import holoviews as hv
import numpy as np
pn.extension()
# Lees de CSV-file in
df_filtered = pd.read_csv('hardloop.tsv', delimiter='\t')

# Filter de rijen waarin 'TQR' gelijk is aan 0 of niet ingevuld
df = df_filtered[df_filtered['TQR'].notna() & (df_filtered['TQR'] != 0)]

# Voeg een nieuwe kolom 'HOUR' toe aan het DataFrame op basis van de 'MOMENT' kolom
df['HOUR'] = np.where(df['MOMENT'] == 'A', 0, 12)

# Zet de 'DATES' kolom om naar datetime
df['DATES'] = pd.to_datetime(df['DATES'], format='%d-%b-%y')

# Voeg de 'HOUR' kolom toe aan de 'DATES' kolom
df['DATES'] = df['DATES'] + pd.to_timedelta(df['HOUR'], unit='h')

# Verwijder de 'HOUR' kolom omdat deze niet langer nodig is
df = df.drop('HOUR', axis=1)

# Laat alleen de gewenste kolommen zien
df = df[["DATES","MOMENT", "TQR", "RPE", "DURATION", "SLEEP", "PERSON_ID", "ID", "TQR_OF_RPE"]]

# Voeg een nieuwe kolom 'COLOR' toe aan het DataFrame op basis van de datumperiodes
df['blessure'] = 'laat_alles_zien'  # Standaardkleur

df['ACUTE_WORKLOAD'] = df['DURATION'] * df['RPE']
# Load injury information from TSV file
injury_info_df = pd.read_csv("blessures.tsv", sep='\t')

# Convert date columns to datetime format
injury_info_df['DATE_START'] = pd.to_datetime(injury_info_df['DATE_START'], format='%d-%b-%y')
injury_info_df['DATE_END'] = pd.to_datetime(injury_info_df['DATE_END'], format='%d-%b-%y')

person_ids_options = ["Alle ID's"] + df['PERSON_ID'].unique().tolist()
# Iterate over rows and update the existing DataFrame
for index, row in injury_info_df.iterrows():
    start_date = row['DATE_START']
    end_date = row['DATE_END']
    condition = (df['PERSON_ID'] == row['PERSON_ID']) & (df['DATES'] >= start_date) & (df['DATES'] <= end_date)
    df.loc[condition, 'blessure'] = row['DIAGNOSE']

def line_plot_data(person_id, metric, line_color):
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
            title=f'Activiteiten voor PERSON_ID {person_id}',
            xlabel='Datum', ylabel='Waarde',
            grid=True, width=800, height=400, rot=45,
            line_color=line_color  # Hier voegen we de door de gebruiker gekozen kleur toe
        )

    # Zorg ervoor dat de y-aslimieten onafhankelijk zijn
    plot.opts(shared_axes=False)

    return plot

def box_plot_data(person_id, metric):
    if person_id is not None:
        filtered_df = df[df['PERSON_ID'] == person_id]
    else:
        filtered_df = df.copy()

    if metric == 'RPE':
        box_plot = filtered_df[filtered_df['RPE'] > 0].hvplot.box(y='RPE', by='MOMENT', title='Boxplot van RPE per MOMENT')
    elif metric == 'TQR':
        box_plot = filtered_df[filtered_df['TQR'] > 0].hvplot.box(y='TQR', by='MOMENT', title='Boxplot van TQR per MOMENT')
    elif metric == 'ACUTE_WORKLOAD':
        # Take the log2 of the 'ACUTE_WORKLOAD' column
        filtered_df['log2_ACUTE_WORKLOAD'] = np.log2(filtered_df['ACUTE_WORKLOAD'])
        box_plot = filtered_df[filtered_df['ACUTE_WORKLOAD'] > 0].hvplot.box(y='log2_ACUTE_WORKLOAD', by='MOMENT', title='Boxplot van log2(ACUTE_WORKLOAD) per MOMENT')
    else:
        return None

    return box_plot


sleep_limit_options = ["Geen limiet", "15 als limiet", "10 als limiet"]
sleep_limit_radio = pn.widgets.RadioButtonGroup(name='Limiteer Sleep', options=sleep_limit_options, value="Geen limiet")

def scatter_plot_data(person_id, line_color, sleep_limit, sleep_metric='SLEEP'):
    selected_person_data_2 = df.copy()

    # Apply sleep limit filter
    if sleep_limit == "15 als limiet":
        selected_person_data_2 = selected_person_data_2[selected_person_data_2[sleep_metric] <= 15]
    elif sleep_limit == "10 als limiet":
        selected_person_data_2 = selected_person_data_2[selected_person_data_2[sleep_metric] <= 10]

    if person_id is not None:
        selected_person_data_2 = selected_person_data_2[selected_person_data_2['PERSON_ID'] == person_id]

    # Bepaal de grootte van de rondjes op basis van een nieuwe kolom 'SIZE'
    selected_person_data_2['SIZE'] = selected_person_data_2['ACUTE_WORKLOAD']  # Hier kun je een andere kolom kiezen als grootte

    scatter_plot = selected_person_data_2.hvplot.scatter(
        x='ACUTE_WORKLOAD', y=sleep_metric, color='blessure', size='SIZE',alpha=0.7,
        title=f'Scatterplot van {sleep_metric} vs Workload',
        ylabel=f'{sleep_metric} (uren)', xlabel='WORKLOAD',
        grid=True, width=800, height=400,
        line_color=line_color
    )
    return scatter_plot


def plot_chronic_ratio(person_id, metric, line_color):
    selected_person_data_3 = df.copy()
    if person_id is not None:
        selected_person_data_3 = selected_person_data_3[selected_person_data_3['PERSON_ID'] == person_id]

    if metric == 'TQR':
        plot_workload = selected_person_data_3.hvplot.line(
            x='ACUTE_WORKLOAD', y='TQR', groupby='blessure',
            title=f'chronic_ratio voor PERSON_ID {person_id}',
            xlabel='Chronic_ratio', ylabel='TQR waarde',
            grid=True, width=800, height=400, rot=45,
            line_color=line_color  # Hier voegen we de door de gebruiker gekozen kleur toe
        )
    else:
        plot_workload = selected_person_data_3.hvplot.line(
            x= 'ACUTE_WORKLOAD' , y= metric, groupby='blessure',
            title=f'chronic_ratio voor PERSON_ID {person_id}',
            xlabel='Chronic_ratio', ylabel='TQR waarde',
            grid=True, width=800, height=400, rot=45,
            line_color=line_color  # Hier voegen we de door de gebruiker gekozen kleur toe
        )


    return plot_workload




# Lijst met beschikbare PERSON_ID's
person_ids = df['PERSON_ID'].unique().tolist()

# Lijst met beschikbare metingen (TQR, RPE, DURATION)
metrics = ['TQR', 'RPE', 'DURATION','ACUTE_WORKLOAD']
metrics_box = ['TQR', 'RPE', 'ACUTE_WORKLOAD']
metric_scatter = ['TQR','SLEEP']
metric_workload = ['TQR','RPE']
box_metric_selector = pn.widgets.Select(name='Selecteer Meting (Boxplot)', options=metrics_box)

# Maak keuzelijsten voor PERSON_ID en meting
person_selector_1 = pn.widgets.Select(name='Selecteer PERSON by ID (Plot 1)', options=person_ids)
metric_selector_1 = pn.widgets.Select(name='Selecteer Meting waarde (Plot 1)', options=metrics)

person_selector_2 = pn.widgets.Select(name='Selecteer PERSON by ID (Plot 2)', options=person_ids)
metric_selector_2 = pn.widgets.Select(name='Selecteer Meting waarde (Plot 2)', options=metrics)

person_selector_3 = pn.widgets.Select(name='Selecteer PERSON by ID (Scatter Plot)', options=person_ids_options)
person_selector_4 = pn.widgets.Select(name='Selecteer PERSON by ID (box Plot)', options=person_ids_options)

sleep_metric_selector = pn.widgets.Select(name='Selecteer SLEEP Meting', options=metric_scatter, value='SLEEP')

color_picker_1 = pn.widgets.ColorPicker(name='Kies Kleur', value='#1f77b4')  # Standaardkleur
color_picker_2 = pn.widgets.ColorPicker(name='Kies Kleur', value='#ff7f0e')  # Standaardkleur
color_picker_3 = pn.widgets.ColorPicker(name='Kies Kleur', value='#ff7f0e')  # Standaardkleur

person_selector_5 = pn.widgets.Select(name='Selecteer PERSON by ID (Chronische Ratio)', options=person_ids_options)
color_picker_4 = pn.widgets.ColorPicker(name='Kies Kleur', value='#1f77b4')  # Standaardkleur
metric_selector_chronic_ratio = pn.widgets.Select(name='Selecteer Meting waarde (Chronische Ratio)', options=metric_workload)
# Voeg de plot en de keuzelijsten toe aan de app
@pn.depends(person_id=person_selector_1, metric=metric_selector_1, line_color=color_picker_1)
def update_plot_1(person_id, metric, line_color):
    plot = line_plot_data(person_id, metric, line_color)
    return plot

@pn.depends(person_id=person_selector_2, metric=metric_selector_2, line_color=color_picker_2)
def update_plot_2(person_id, metric, line_color):
    plot = line_plot_data(person_id, metric, line_color)
    return plot


@pn.depends(person_id=person_selector_4.param.value, metric=box_metric_selector)
def update_box_plot(person_id, metric):
    if person_id == "Alle ID's":
        box_plot = box_plot_data(None, metric)
    else:
        box_plot = box_plot_data(person_id, metric)
    return box_plot


@pn.depends(person_id=person_selector_3.param.value, line_color=color_picker_3.param.value, sleep_limit=sleep_limit_radio.param.value, sleep_metric=sleep_metric_selector.param.value)
def update_scatter_plot(person_id, line_color, sleep_limit, sleep_metric):
    if person_id == "Alle ID's":
        scatter_plot = scatter_plot_data(None, line_color, sleep_limit, sleep_metric)
    else:
        scatter_plot = scatter_plot_data(person_id, line_color, sleep_limit, sleep_metric)
    return scatter_plot

@pn.depends(person_id=person_selector_5.param.value, line_color=color_picker_4.param.value, metric=metric_selector_chronic_ratio)
def update_chronic_ratio_plot(person_id, line_color, metric):
    if person_id == "Alle ID's":
        plot_workload = plot_chronic_ratio(None, metric, line_color)
    else:
        plot_workload = plot_chronic_ratio(person_id, metric, line_color)
    return plot_workload



header = pn.pane.Markdown("# Interactive Lijn-, Box- en Scatterplots\n## TQR, RPE, en DUUR per dag per ID")

sidebar = pn.Column(
    'Info about page',

)

# Define the main content layout
main_content = pn.Column(
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
    ),
    pn.Row(
        person_selector_4,
        box_metric_selector,
        update_box_plot
    ),
    pn.Row(
        person_selector_3,

        sleep_metric_selector,
        color_picker_3,
        update_scatter_plot  # Scatter plot here
    ),
    pn.Row(
        sleep_limit_radio,
    ),
    pn.Row(
        person_selector_5,
        metric_selector_chronic_ratio,
        color_picker_4,
        update_chronic_ratio_plot
    )
)

# Combine header, sidebar, and main content
app_layout = pn.Column(
    header,
    pn.Row(
        sidebar,
        main_content,
    )
)

# Start the Panel app
app_layout.show()
