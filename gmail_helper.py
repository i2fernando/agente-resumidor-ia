import os
import base64
import json
from email import message_from_bytes

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Escopo de permissão: leitura dos e-mails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def autenticar_gmail():
    """Autentica com a conta Google e retorna o serviço da API Gmail."""
    creds = None
    token_path = 'token.json'
    credentials_path = os.path.join('credentials', 'credentials.json')

    # Verifica se já existe um token salvo
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Se não, inicia o fluxo de login OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Salva o token para uso futuro
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Cria o serviço da API
    service = build('gmail', 'v1', credentials=creds)
    return service


def buscar_emails(service, quantidade=5):
    """Busca os últimos e-mails da caixa de entrada"""
    resultados = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=quantidade).execute()
    mensagens = resultados.get('messages', [])

    emails = []

    for mensagem in mensagens:
        msg = service.users().messages().get(userId='me', id=mensagem['id'], format='full').execute()
        payload = msg['payload']
        headers = payload.get('headers', [])
        assunto = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem Assunto)')
        remetente = next((h['value'] for h in headers if h['name'] == 'From'), '(Remetente desconhecido)')
        link = f"https://mail.google.com/mail/u/0/#inbox/{mensagem['id']}"

        # Extrai corpo do e-mail
        corpo = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    corpo = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            corpo = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        emails.append({
            'assunto': assunto,
            'remetente': remetente,
            'corpo': corpo,
            'link': link
        })

    return emails
