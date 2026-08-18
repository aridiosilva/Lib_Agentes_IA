"""
src/workmail_client.py
WorkMail Client - Conexão e busca de e-mails via protocolo IMAP (Amazon WorkMail)
"""

import os
import json
import imaplib
import email
from email.policy import default
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class WorkmailClient:
    """Cliente para acessar emails do Amazon WorkMail via IMAP"""
    
    def __init__(self, credentials_path: str = 'credentials/workmail_credentials.json'):
        self.credentials_path = credentials_path
        self.mail = None
        self.cached_messages = {}  # Cache de mensagens para evitar múltiplos downloads
        
    def authenticate(self):
        """Autentica e conecta ao servidor IMAP"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado em: {self.credentials_path}")
            
        with open(self.credentials_path, 'r', encoding='utf-8') as f:
            creds = json.load(f)
            
        imap_server = creds.get('imap_server')
        username = creds.get('username')
        password = creds.get('password')
        
        if not all([imap_server, username, password]):
            raise ValueError("As credenciais do WorkMail devem conter 'imap_server', 'username' e 'password'.")
            
        # Conecta via SSL
        self.mail = imaplib.IMAP4_SSL(imap_server, 993)
        self.mail.login(username, password)
        return self.mail
        
    def buscar_emails(self, dias: int = 90, max_results: int = 200) -> List[Dict]:
        """
        Busca e-mails dos últimos N dias com anexos PDF
        
        Args:
            dias: Número de dias para trás
            max_results: Máximo de resultados mais recentes
            
        Returns:
            Lista de e-mails processados
        """
        if not self.mail:
            self.authenticate()
            
        # Seleciona pasta inbox de forma segura (somente leitura)
        self.mail.select("INBOX", readonly=True)
        
        # Gera data limite no padrão IMAP (DD-Mon-YYYY) sem depender do locale da máquina
        meses = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data_limite = datetime.now() - timedelta(days=dias)
        data_str = f"{data_limite.day:02d}-{meses[data_limite.month - 1]}-{data_limite.year}"
        
        # Query de busca IMAP
        search_query = f'(SINCE {data_str})'
        status, messages = self.mail.search(None, search_query)
        
        if status != 'OK' or not messages[0]:
            return []
            
        # Pega a lista de números das mensagens
        msg_nums = messages[0].split()
        
        # Inverte para processar as mais recentes primeiro
        msg_nums.reverse()
        
        # Limita a quantidade máxima de resultados
        msg_nums = msg_nums[:max_results]
        
        emails_processados = []
        
        for num in msg_nums:
            msg_id = num.decode('utf-8')
            email_data = self._processar_mensagem(msg_id)
            if email_data:
                emails_processados.append(email_data)
                
        return emails_processados
        
    def _processar_mensagem(self, msg_id: str) -> Optional[Dict]:
        """Processa uma mensagem individual e a mantém em cache"""
        try:
            # Baixa a mensagem completa
            status, data = self.mail.fetch(msg_id.encode('utf-8'), '(RFC822)')
            if status != 'OK' or not data or not data[0]:
                return None
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email, policy=default)
            
            # Guarda em cache para a fase de download do anexo
            self.cached_messages[msg_id] = msg
            
            assunto = msg.get('Subject', '')
            remetente = msg.get('From', '')
            data_envio = msg.get('Date', '')
            
            # Verifica se deve processar este email
            if not self._deve_processar(remetente, assunto):
                return None
                
            # Extrai os metadados dos anexos
            anexos = self._extrair_anexos(msg)
            
            if not anexos:
                return None
                
            return {
                'id': msg_id,
                'remetente': remetente,
                'assunto': assunto,
                'data': data_envio,
                'anexos': anexos
            }
            
        except Exception as e:
            print(f'Erro ao processar mensagem {msg_id}: {e}')
            return None
            
    def _deve_processar(self, remetente: str, assunto: str) -> bool:
        """Aplica regras de filtragem baseadas no remetente e assunto"""
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
        
    def _extrair_anexos(self, msg) -> List[Dict]:
        """Extrai a lista de anexos PDF da mensagem"""
        anexos = []
        
        # Caminha pelas partes da mensagem
        for part_index, part in enumerate(msg.walk()):
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
                
            filename = part.get_filename()
            if filename and filename.lower().endswith('.pdf'):
                anexos.append({
                    'filename': filename,
                    'attachmentId': str(part_index)  # Usamos o índice da parte como ID do anexo
                })
                
        return anexos
        
    def baixar_anexo(self, msg_id: str, attachment_id: str) -> Optional[bytes]:
        """Baixa o conteúdo de um anexo do cache ou do servidor"""
        msg = self.cached_messages.get(msg_id)
        
        if not msg:
            # Fallback: se não estiver no cache, baixa a mensagem de novo
            if not self.mail:
                self.authenticate()
            status, data = self.mail.fetch(msg_id.encode('utf-8'), '(RFC822)')
            if status == 'OK' and data and data[0]:
                msg = email.message_from_bytes(data[0][1], policy=default)
                self.cached_messages[msg_id] = msg
            else:
                return None
                
        try:
            part_index = int(attachment_id)
            # Acessa a parte correspondente
            for idx, part in enumerate(msg.walk()):
                if idx == part_index:
                    return part.get_payload(decode=True)
        except Exception as e:
            print(f'Erro ao baixar anexo {attachment_id} da mensagem {msg_id}: {e}')
            
        return None
        
    def logout(self):
        """Fecha a conexão IMAP"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
            self.mail = None
