# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from google.oauth2 import service_account
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# If modifying these scopes, delete the file token.pickle.

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1V66QX4O9DxGTiiu5fnL4LVj0T038XiD7_uxd-ab1pDw'

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="!A2:J314").execute()
values = result.get('values', [])

def gsheet_to_df(values):
    """
    Converts Google sheet API df to Pandas dfFrame

    Input: Google API service.spreadsheets().get() values
    Output: Pandas dfFrame with all df from Google Sheet
    """
    header = values[0]
    rows = values[1:]
    if not rows:
        print('No df found.')
    else:
        df = pd.DataFrame(columns=header, data=rows)
    return df

df_raw = gsheet_to_df(values)
df = df_raw[df_raw.columns.drop('Date')].apply(pd.to_numeric)
print(df.columns)
df['Date'] = pd.to_datetime(df_raw['Date'].str.strip(), format='%d/%m/%Y')
df['Day_num'] = df['Date'].dt.dayofweek
df['Day'] = df['Date'].dt.day_name()

factor = 100

# Kpi evaluation
df['TotPhra'] = (df['FCE_PhraVerb'] + df['CAE_PhraVerb']+ df['CPE_PhraVerb'])/3 * factor
df['TotWord'] = (df['FCE_WordForm'] + df['CAE_WordForm']+ df['CPE_WordForm'])/9* factor
df['TotCol'] = (df['FCE_Collocation'] + df['CAE_Collocation']+ df['CPE_Collocation'])/3* factor

df['TotFCE'] = (df['FCE_PhraVerb'] + df['FCE_WordForm']+ df['FCE_Collocation'])/5* factor
df['TotCAE'] = (df['CAE_PhraVerb'] + df['CAE_WordForm']+ df['CAE_Collocation'])/5* factor
df['TotCPE'] = (df['CPE_PhraVerb'] + df['CPE_WordForm']+ df['CPE_Collocation'])/5* factor

df['Tot'] = (df['TotFCE'] + df['TotCAE']+ df['TotCPE'])/3

df.dropna(inplace=True)
print(df.isna().sum())
print(df)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Floe Joe Wordbank Dashboard", className="header-title"
                ),
                html.P(
                    children="Monitoring daily English prep exercises for FCE, CAE and CPE",
                    className="header-description",
                ),
            ],
            className="header",
        ),
html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Day", className="menu-title"),
                        dcc.Dropdown(
                            id="day-filter",
                            options=[
                                {"label": day, "value": day}
                                for day in np.unique(df['Day'])
                            ],
                            value="Monday",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df.Date.min(),
                            max_date_allowed=df.Date.max(),
                            start_date=df.Date.min(),
                            end_date=df.Date.max(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="line-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": df["Date"],
                                    "y": df["Tot"],
                                    "type": "lines",
                                    "hovertemplate": "%{y:.2f}%"
                                    "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Avg percent tot points",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        },
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output("line-chart", "figure"),
[
        Input("day-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date")
    ],
)
def update_charts(day, start_date, end_date):
    mask = (
        (df["Day"] == day)
        & (df.Date >= start_date)
        & (df.Date <= end_date)
    )
    filtered_data = df.loc[mask, :]
    line_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Tot"],
                "type": "lines",
                "hovertemplate": "%{y:.2f} % <extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Avg percent tot points",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"suffix": "%", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }
    return line_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True, port =8080)
