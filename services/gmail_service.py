from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        """Autentica con Gmail API."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)
        return self.service

    def get_emails(self, query='', max_results=10):
        """Obtiene emails basados en una consulta."""
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']).execute()
                
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                date = next(h['value'] for h in headers if h['name'] == 'Date')
                
                # Extraer el cuerpo del email
                if 'parts' in msg['payload']:
                    body = msg['payload']['parts'][0]['body'].get('data', '')
                else:
                    body = msg['payload']['body'].get('data', '')

                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body
                })

            return emails
        except Exception as e:
            print(f"Error al obtener emails: {str(e)}")
            return []

    def search_emails_by_date(self, start_date, end_date):
        """Busca emails entre fechas específicas."""
        query = f'after:{start_date} before:{end_date}'
        return self.get_emails(query=query)

    def search_emails_by_sender(self, sender_email):
        """Busca emails de un remitente específico."""
        query = f'from:{sender_email}'
        return self.get_emails(query=query) 