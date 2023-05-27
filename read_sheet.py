from __future__ import print_function

import os
import pandas as pd

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client import client, file, tools

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_values(spreadsheet_id, range_name):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    print(creds.valid)

    if not creds or not creds.valid:

        store = file.Storage('token.json')
        creds = None
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)


    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials = creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)} rows retrieved")
        
        
        return rows
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == '__main__':
    # Pass: spreadsheet_id, and range_name
    data=get_values("1k231VS8qEGrymQkh-jF15H7QstEJ73teyi2JMt96c9U", "Form Responses 1")
    df = pd.DataFrame(data[1:], columns=data[0])
    df.to_csv('data/test.csv',index = False,encoding='utf-8-sig')
    print(df)