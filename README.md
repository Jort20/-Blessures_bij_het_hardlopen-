# -Blessures_bij_het_hardlopen-

# Running Data Dashboard

This dashboard provides visualizations and insights into running data, including information about individual runners and their injuries.

## Features

- Line plots showing various metrics over time for individual runners.
- Box plots for analyzing distributions of metrics across different moments of the day.
- Scatter plots depicting the relationship between workload and sleep, with the option to filter outliers.
- Chronic ratio plots to understand the chronic workload and its impact on different metrics.

## Getting Started

### Prerequisites

Make sure you have the following Python libraries installed:

```bash
pip install pandas panel hvplot holoviews numpy
```

### Installation

Clone the repository:
```bash
git clone https://github.com/your-username/running-data-dashboard.git
cd running-data-dashboard
```
### usage 
Run the dashboard script:
```bash
python dashboard.py
```
Visit http://localhost:500 in your web browser to interact with the dashboard.

## plots
### Line Plots
#### Plot 1

    Select a person by ID.
    Choose a metric for the y-axis.
    Pick a line color.

#### Plot 2

    Select another person by ID.
    Choose a different metric for the y-axis.
    Pick another line color.

#### Box Plots

    Select a person by ID or choose "All IDs."
    Choose a metric for the box plot.

#### Scatter Plot

    Select a person by ID or choose "All IDs."
    Choose a line color.
    Select a sleep limit option.
    Choose a sleep metric.

#### Chronic Ratio Plot

    Select a person by ID or choose "All IDs."
    Choose a line color.
    Choose a metric for the chronic ratio plot.

## Info

    The dataset includes information about dates, moments, TQR, RPE, duration, sleep, person IDs, and more.
    There are 24 unique person IDs in the dataset.

## Research

Find related research based on this dataset:

- [Increase in the Acute: Chronic Workload Ratio relates to Injury Risk in Competitive Runners](https://research.rug.nl/en/publications/increase-in-the-acute-chronic-workload-ratio-relates-to-injury-ri)
- [Prediction of Running Injuries from Training Load: a Machine Learning Approach](https://research.hanze.nl/ws/portalfiles/portal/16171742/eTelemed2017Predictionofinjuries.pdf)

## Acknowledgments

Special thanks to the contributors and researchers who made this project possible.


