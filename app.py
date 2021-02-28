from flask import Flask
from dash import Dash
import dash_html_components as html
import os
import json

server = Flask(__name__)

app = Dash(name=__name__,
           server=server)

# The ID and range of a google spreadsheet.
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
RANGE_NAME = os.environ['RANGE_NAME']
CREDS = os.environ['GDRIVE_AUTH']

def get_google_sheet():
    """
    Returns all values from the target google sheet.
    Prints values from a sample spreadsheet.
    """
    service_account_info = json.loads(CREDS)
    creds = service_account.Credentials.from_service_account_info(
        service_account_info)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def gsheet_to_df(values):
    """
    Converts Google sheet API data to Pandas DataFrame

    Input: Google API service.spreadsheets().get() values
    Output: Pandas DataFrame with all data from Google Sheet
    """
    header = values[0]
    rows = values[1:]
    if not rows:
        print('No data found.')
    else:
        df = pd.DataFrame(columns=header, data=rows)
    return df


app.layout = html.Div(
    html.H2('The basic Dash APP',
            style={
                'font-family': 'plain',
                'font-weight': 'light',
                'color': 'grey',
                'text-align': 'center',
                'font-size': 24,
            })
)

if __name__ == '__main__':
    app.run_server(debug=True)