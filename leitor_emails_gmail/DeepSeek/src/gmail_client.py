"""
src/gmail_client.py
Gmail Client - Conexão e busca de e-mails via API Gmail
"""

import os
import base64
import pickle
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Se modificar escopos, deletar token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    """Cliente para acessar API do Gmail"""
    
    def __init__(self, credentials_path: str = 'credentials/credentials.json', 
                 token_path: str = 'credentials/token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
    def authenticate(self):
        """Autentica e retorna serviço Gmail"""
        creds = None
        
        # Carrega token existente
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não houver credenciais válidas, faz login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salva token para próxima execução
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def buscar_emails(self, dias: int = 90, max_results: int = 200) -> List[Dict]:
        """
        Busca e-mails dos últimos N dias com anexos PDF
        
        Args:
            dias: Número de dias para trás
            max_results: Máximo de resultados
            
        Returns:
            Lista de e-mails processados
        """
        if not self.service:
            self.authenticate()
        
        # Data limite
        data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y/%m/%d')
        
        # Query: tem anexo PDF, após data_limite
        query = f'has:attachment filename:pdf after:{data_limite}'
        
        try:
            # Busca mensagens
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            emails_processados = []
            
            for msg in messages:
                email_data = self._processar_mensagem(msg['id'])
                if email_data:
                    emails_processados.append(email_data)
            
            return emails_processados
            
        except HttpError as error:
            print(f'Ocorreu um erro: {error}')
            return []
    
    def _processar_mensagem(self, msg_id: str) -> Optional[Dict]:
        """Processa uma mensagem individual"""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=msg_id, format='full').execute()
            
            # Extrai cabeçalhos
            headers = msg['payload']['headers']
            
            assunto = None
            remetente = None
            data = None
            
            for header in headers:
                if header['name'] == 'Subject':
                    assunto = header['value']
                elif header['name'] == 'From':
                    remetente = header['value']
                elif header['name'] == 'Date':
                    data = header['value']
            
            # Verifica se deve processar este email
            if not self._deve_processar(remetente, assunto):
                return None
            
            # Extrai anexos
            anexos = self._extrair_anexos(msg)
            
            if not anexos:
                return None
            
            return {
                'id': msg_id,
                'remetente': remetente,
                'assunto': assunto,
                'data': data,
                'anexos': anexos
            }
            
        except HttpError as error:
            print(f'Erro ao processar mensagem {msg_id}: {error}')
            return None
    
    def _deve_processar(self, remetente: str, assunto: str) -> bool:
        """Aplica regras de filtragem"""
        if not remetente or not assunto:
            return False
        
        remetente = remetente.lower()
        assunto = assunto.lower()
        
        # Remetentes conhecidos
        remetentes_conhecidos = [
            '@bb.com.br', '@bancodobrasil.com.br',
            '@nubank.com.br', '@nubank.com',
            '@cis.com.br',
            '@bradesco.com.br',
            '@itau.com.br',
            '@caixa.gov.br',
            '@santander.com.br',
            '@vivo.com.br',
            '@cpfl.com.br', '@cpfl.com',
            '@enel.com.br', '@enel.com'
        ]
        
        # Palavras-chave no assunto
        palavras_chave = [
            'fatura', 'boleto', 'conta', 'vencimento', 'pagamento',
            'cartão', 'visa', 'mastercard', 'água', 'esgoto',
            'internet', 'celular', 'condomínio', 'condominio',
            'seguro', 'energia', 'elétrica', 'luz', 'taxa condominial',
            '2ª via', 'segunda via'
        ]
        
        # Verifica remetente conhecido
        for rem in remetentes_conhecidos:
            if rem in remetente:
                return True
        
        # Verifica palavras-chave
        for palavra in palavras_chave:
            if palavra in assunto:
                return True
        
        return False
    
    def _extrair_anexos(self, msg: Dict) -> List[Dict]:
        """Extrai anexos PDF da mensagem"""
        anexos = []
        
        def processar_part(part):
            if part.get('filename'):
                filename = part['filename']
                if filename.lower().endswith('.pdf'):
                    # Verifica se tem attachmentId (anexo real)
                    if 'body' in part and 'attachmentId' in part['body']:
                        attachment_id = part['body']['attachmentId']
                        anexos.append({
                            'filename': filename,
                            'attachmentId': attachment_id
                        })
            
            if 'parts' in part:
                for subpart in part['parts']:
                    processar_part(subpart)
        
        if 'payload' in msg:
            processar_part(msg['payload'])
        
        return anexos
    
    def baixar_anexo(self, msg_id: str, attachment_id: str) -> bytes:
        """Baixa um anexo específico"""
        if not self.service:
            self.authenticate()
        
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id).execute()
            
            data = attachment.get('data')
            if data:
                return base64.urlsafe_b64decode(data.encode('UTF-8'))
            
            return None
            
        except HttpError as error:
            print(f'Erro ao baixar anexo: {error}')
            return None