import pandas as pd
import panel as pn
import hvplot.pandas
import holoviews as hv
import numpy as np

pn.extension()

# read the CSV-file
df_filtered = pd.read_csv("raw_data/hardloop.tsv", delimiter="\t")

# Filter the rows where 'TQR' is equal to 0 or not filled in
df = df_filtered[df_filtered["TQR"].notna() & (df_filtered["TQR"] != 0)]

# add a new column 'HOUR' to DataFrame on the basis of'MOMENT' column
df["HOUR"] = np.where(df["MOMENT"] == "A", 0, 12)

# rewrite the 'DATES' column to datetime
df["DATES"] = pd.to_datetime(df["DATES"], format="%d-%b-%y")

# add the 'HOUR' column to the 'DATES' column
df["DATES"] = df["DATES"] + pd.to_timedelta(df["HOUR"], unit="h")

# delete the hour column isnt needed anymore
df = df.drop("HOUR", axis=1)

# only show the wanted columns
df = df[
    [
        "DATES",
        "MOMENT",
        "TQR",
        "RPE",
        "DURATION",
        "SLEEP",
        "PERSON_ID",
        "ID",
        "TQR_OF_RPE",
    ]
]
# add show everything to df blessures
df["blessure"] = "laat_alles_zien"

df["ACUTE_WORKLOAD"] = df["DURATION"] * df["RPE"]
# Load injury information from TSV file
injury_info_df = pd.read_csv("raw_data/blessures.tsv", sep="\t")

# Convert date columns to datetime format
injury_info_df["DATE_START"] = pd.to_datetime(
    injury_info_df["DATE_START"], format="%d-%b-%y"
)
injury_info_df["DATE_END"] = pd.to_datetime(
    injury_info_df["DATE_END"], format="%d-%b-%y"
)
# make the return all ID's option
person_ids_options = ["Alle ID's"] + df["PERSON_ID"].unique().tolist()
# Iterate over rows and update the existing DataFrame
for index, row in injury_info_df.iterrows():
    start_date = row["DATE_START"]
    end_date = row["DATE_END"]
    condition = (
        (df["PERSON_ID"] == row["PERSON_ID"])
        & (df["DATES"] >= start_date)
        & (df["DATES"] <= end_date)
    )
    df.loc[condition, "blessure"] = row["DIAGNOSE"]


def line_plot_data(person_id, metric, line_color):
    """
    Generate a line plot based on the selected person's data.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - metric (str): Metric for the y-axis of the plot.
    - line_color (str): Color of the lines in the plot.

    Returns:
    - plot: Line plot generated using HoloViews.
    """
    # Make a copy of the DataFrame to keep the original data unchanged
    selected_person_data = df.copy()[df["PERSON_ID"] == person_id]
    # for loop so that the titles match the graphs and their information
    if metric == "DURATION":
        plot = selected_person_data.hvplot.line(
            x="DATES",
            y="DURATION",
            groupby="blessure",
            title=f"Duur per dag voor PERSON_ID {person_id}",
            xlabel="Datum",
            ylabel="Duur (minuten)",
            grid=True,
            width=800,
            height=400,
            rot=45,
            line_color=line_color,  # Here we add the color chosen by the user
        )
    else:
        plot = selected_person_data.hvplot.line(
            x="DATES",
            y=metric,
            groupby="blessure",
            title=f"Activiteiten voor PERSON_ID {person_id}",
            xlabel="Datum",
            ylabel="Waarde",
            grid=True,
            width=800,
            height=400,
            rot=45,
            line_color=line_color,  # Here we add the color chosen by the user
        )

    # Make sure the y-axis limits are independent
    plot.opts(shared_axes=False)

    return plot


def box_plot_data(person_id, metric):
    """
    Generate a box plot based on the selected person's data.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - metric (str): Metric for the y-axis of the plot.

    Returns:
    - box_plot: Box plot generated using HoloViews.
    """
    if person_id is not None:
        filtered_df = df[df["PERSON_ID"] == person_id]
    else:
        filtered_df = df.copy()
    # create a for loop to ensure that the titles match the correct plot
    if metric == "RPE":
        box_plot = filtered_df[filtered_df["RPE"] > 0].hvplot.box(
            y="RPE", by="MOMENT", title="Boxplot van RPE per MOMENT"
        )
    elif metric == "TQR":
        box_plot = filtered_df[filtered_df["TQR"] > 0].hvplot.box(
            y="TQR", by="MOMENT", title="Boxplot van TQR per MOMENT"
        )
    elif metric == "ACUTE_WORKLOAD":
        # Take the log2 of the 'ACUTE_WORKLOAD' column
        filtered_df["log2_ACUTE_WORKLOAD"] = np.log2(filtered_df["ACUTE_WORKLOAD"])
        box_plot = filtered_df[filtered_df["ACUTE_WORKLOAD"] > 0].hvplot.box(
            y="log2_ACUTE_WORKLOAD",
            by="MOMENT",
            title="Boxplot van log2(ACUTE_WORKLOAD) per MOMENT",
        )
    else:
        return None

    return box_plot


# make the sleep limit widgets due to unrealistic outliers
sleep_limit_options = ["Geen limiet", "15 als slaap limiet", "10 als slaap limiet"]
sleep_limit_radio = pn.widgets.RadioButtonGroup(
    name="Limiteer Sleep", options=sleep_limit_options, value="Geen limiet"
)


def scatter_plot_data(person_id, line_color, sleep_limit, sleep_metric="SLEEP"):
    """
    Generate a scatter plot based on the selected person's data.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - line_color (str): Color of the lines in the plot.
    - sleep_limit (str): Sleep limit option for filtering.
    - sleep_metric (str): Metric for the y-axis of the plot.

    Returns:
    - scatter_plot: Scatter plot generated using HoloViews.
    """
    selected_person_data_2 = df.copy()

    # Apply sleep limit filter
    if sleep_limit == "15 als slaap limiet":
        selected_person_data_2 = selected_person_data_2[
            selected_person_data_2[sleep_metric] <= 15
        ]
    elif sleep_limit == "10 als slaap limiet":
        selected_person_data_2 = selected_person_data_2[
            selected_person_data_2[sleep_metric] <= 10
        ]
    if person_id is not None:
        selected_person_data_2 = selected_person_data_2[
            selected_person_data_2["PERSON_ID"] == person_id
        ]

    # Determine the size of the circles based on a new column 'SIZE'
    selected_person_data_2["SIZE"] = selected_person_data_2[
        "ACUTE_WORKLOAD"
    ]  # Here you can choose a different column for size
    # make the scatterplot
    scatter_plot = selected_person_data_2.hvplot.scatter(
        x="ACUTE_WORKLOAD",
        y=sleep_metric,
        color="blessure",
        size="SIZE",
        alpha=0.7,
        title=f"Scatterplot van {sleep_metric} vs Workload",
        ylabel=f"{sleep_metric} (uren)",
        xlabel="WORKLOAD",
        grid=True,
        width=800,
        height=400,
        line_color=line_color,
    )
    return scatter_plot


# List of available PERSON_IDs
person_ids = df["PERSON_ID"].unique().tolist()

# List of available measurements for different charts
metrics = ["TQR", "RPE", "DURATION", "ACUTE_WORKLOAD"]
metrics_box = ["TQR", "RPE", "ACUTE_WORKLOAD"]
metric_scatter = ["TQR", "SLEEP"]
box_metric_selector = pn.widgets.Select(
    name="Selecteer Meting (Boxplot)", options=metrics_box
)

# Create selection lists for PERSON_ID, color and measurement widgets

person_selector_1 = pn.widgets.Select(
    name="Selecteer PERSON by ID (Plot 1)", options=person_ids
)
metric_selector_1 = pn.widgets.Select(
    name="Selecteer Meting waarde (Plot 1)", options=metrics
)

person_selector_2 = pn.widgets.Select(
    name="Selecteer PERSON by ID (Plot 2)", options=person_ids
)
metric_selector_2 = pn.widgets.Select(
    name="Selecteer Meting waarde (Plot 2)", options=metrics
)

person_selector_3 = pn.widgets.Select(
    name="Selecteer PERSON by ID (Scatter Plot)", options=person_ids_options
)
person_selector_4 = pn.widgets.Select(
    name="Selecteer PERSON by ID (box Plot)", options=person_ids_options
)

sleep_metric_selector = pn.widgets.Select(
    name="Selecteer SLEEP Meting", options=metric_scatter, value="SLEEP"
)

color_picker_1 = pn.widgets.ColorPicker(name="Kies Kleur", value="#1f77b4")
color_picker_2 = pn.widgets.ColorPicker(name="Kies Kleur", value="#ff7f0e")
color_picker_3 = pn.widgets.ColorPicker(name="Kies Kleur", value="#ff7f0e")


# panel function to update the plot when the widgets are adjusted
@pn.depends(
    person_id=person_selector_1, metric=metric_selector_1, line_color=color_picker_1
)
def update_plot_1(person_id, metric, line_color):
    """
    Update line Plot 1 based on selected parameters.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - metric (str): Metric for the y-axis of the plot.
    - line_color (str): Color of the lines in the plot.

    Returns:
    - plot: Updated Line plot using HoloViews.
    """
    plot = line_plot_data(person_id, metric, line_color)
    return plot


# panel function to update the plot when the widgets are adjusted
@pn.depends(
    person_id=person_selector_2, metric=metric_selector_2, line_color=color_picker_2
)
def update_plot_2(person_id, metric, line_color):
    """
    Update line Plot 2 based on selected parameters.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - metric (str): Metric for the y-axis of the plot.
    - line_color (str): Color of the lines in the plot.

    Returns:
    - plot: Updated Line plot using HoloViews.
    """
    plot = line_plot_data(person_id, metric, line_color)
    return plot


# panel function to update the plot when the widgets are adjusted
@pn.depends(person_id=person_selector_4.param.value, metric=box_metric_selector)
def update_box_plot(person_id, metric):
    """
    Update the Box Plot based on selected parameters.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - metric (str): Metric for the y-axis of the plot.

    Returns:
    - box_plot: Updated Box plot using HoloViews.
    """
    # show all ID's
    if person_id == "Alle ID's":
        box_plot = box_plot_data(None, metric)
    else:
        box_plot = box_plot_data(person_id, metric)
    return box_plot


# panel function to update the plot when the widgets are adjusted
@pn.depends(
    person_id=person_selector_3.param.value,
    line_color=color_picker_3.param.value,
    sleep_limit=sleep_limit_radio.param.value,
    sleep_metric=sleep_metric_selector.param.value,
)
def update_scatter_plot(person_id, line_color, sleep_limit, sleep_metric):
    """
    Update the Scatter Plot based on selected parameters.

    Parameters:
    - person_id (str): ID of the person for the plot.
    - line_color (str): Color of the lines in the plot.
    - sleep_limit (str): Sleep limit option for filtering.
    - sleep_metric (str): Metric for the y-axis of the plot.

    Returns:
    - scatter_plot: Updated Scatter plot using HoloViews.
    """
    # show all ID's if statement
    if person_id == "Alle ID's":
        scatter_plot = scatter_plot_data(None, line_color, sleep_limit, sleep_metric)
    else:
        scatter_plot = scatter_plot_data(
            person_id, line_color, sleep_limit, sleep_metric
        )
    return scatter_plot


welcome_message = pn.pane.Markdown(
    "# Welkom op het Data dashboard van Hardloop Blessures\n"
    "Dit dashboard bevat informatie over hardlopers en hun blessures in de tab plots.\n"
    "research verteld over de onderzoeken van deze data en info verteld de info over wat wat betekent van de variablen "
)
# header of the app and the app itself are created here
header = pn.pane.Markdown(
    "# Plots over data hardlopers \n## Deze plots bevatten informatie over de hardloper en hun blessures",
    background="#88d8b0",
    style={"width": "110%"},
)

# combine header, sidebar, and main content
sidebar_tab = pn.Column(
    "\n \n \n #### Info over de values in de plots \n"
    "#### dates = datum hardgelopen\n"
    "#### moment = moment van de dag hardgelopen ochtend of avond \n"
    "#### TQR = mate van inspanning na hardlopen \n"
    "#### RPE = een mate hoe belastend het is tijdens het lopen \n"
    "#### duration = hoelang die dag is hardgelopen in minuten \n"
    "#### sleep = hoeveel uren er zijn geslapen die dag door de hardloper \n"
    "#### person_id = de persoon waar het omgaat er zijn 24 personen.",
)
research_tab = pn.pane.Markdown(
    "## Research\n Hier zijn links naar de onderzoeken met deze dataset.\n\n[Increase in the Acute: Chronic Workload Ratio relates to Injury Risk in Competitive Runners](https://research.rug.nl/en/publications/increase-in-the-acute-chronic-workload-ratio-relates-to-injury-ri)\n\n[Prediction of Running Injuries from Training Load:a Machine Learning Approach.](https://research.hanze.nl/ws/portalfiles/portal/16171742/eTelemed2017Predictionofinjuries.pdf)"
)

tabs = pn.Tabs(
    (
        "Home",
        welcome_message,
    ),
    (
        "Plots",
        pn.Column(
            pn.Row(person_selector_1, metric_selector_1, color_picker_1, update_plot_1),
            pn.Row(person_selector_2, metric_selector_2, color_picker_2, update_plot_2),
            pn.Row(person_selector_4, box_metric_selector, update_box_plot),
            pn.Row(
                person_selector_3,
                sleep_metric_selector,
                color_picker_3,
                update_scatter_plot,
            ),
            pn.Row(
                sleep_limit_radio,
            ),
        ),
    ),
    ("Info", sidebar_tab),
    ("Research", research_tab),
)

app_layout = pn.Column(header, tabs)

# Start the Panel app
app_layout.show()
