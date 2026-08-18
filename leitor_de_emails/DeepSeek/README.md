# Agente Leitor de E-mails de Contas a Pagar

Sistema para ler e-mails do Gmail, extrair dados de faturas e boletos em PDF, e gerar um demonstrativo estruturado das contas a pagar.

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Conta Gmail com acesso à API
- Google Cloud Console configurado

## 🚀 Instalação

1. Clone ou baixe este repositório

2. Crie e ative um ambiente virtual:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

# DEEPSEEK.md - Agente Leitor de Emails de Contas a Pagar

> **IMPORTANTE:** Este agente opera gerando código Python que o usuário executa localmente. O DeepSeek NÃO tem acesso direto a Gmail, PDFs ou arquivos locais. O agente gera o código, o usuário executa, e o agente analisa os resultados.

---

## ÍNDICE DE INSTRUÇÕES

1. [Comportamento do Agente](#1-comportamento-do-agente)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [requirements.txt](#3-requirementstxt)
4. [src/gmail_client.py](#4-srcgmail_clientpy)
5. [src/pdf_extractor.py](#5-srcpdf_extractorry)
6. [src/email_processor.py](#6-srcemail_processorpy)
7. [src/main.py](#7-srcmainpy)
8. [src/__init__.py](#8-src__init__py)
9. [src/__main__.py](#9-src__main__py)
10. [credentials/credentials.json - Instruções](#10-credentialscredentialsjson---instruções)
11. [README.md - Instruções para o Usuário](#11-readmemd---instruções-para-o-usuário)
12. [Script de Setup Automático](#12-script-de-setup-automático)
13. [Formato de Saída JSON](#13-formato-de-saída-json)
14. [Exemplo de Uso](#14-exemplo-de-uso)---

## 1. COMPORTAMENTO DO AGENTE

### Regras Obrigatórias

1. **NUNCA** tente acessar Gmail, PDFs ou arquivos diretamente
2. **SEMPRE** gere código Python completo quando solicitado
3. **FORNEÇA** instruções claras de execução passo-a-passo
4. **ANALISE** o JSON de saída que o usuário te enviar
5. **APRESENTE** demonstrativo visual das contas

### Fluxo de Trabalho

```
Usuário: "Processa meus e-mails"
↓
Agente: Gera código Python completo
↓
Usuário: Executa script localmente
↓
Usuário: Envia JSON de saída para o agente
↓
Agente: Analisa e apresenta demonstrativo
```

---

## 2. ESTRUTURA DO PROJETO

```
leitor-contas-pagar/
│
├── README.md
├── requirements.txt
├── setup.py
│
├── credentials/
│   └── credentials.json
│
├── src/
│   ├── __init__.py          # Seção 8 - Torna src um pacote
│   ├── __main__.py          # Seção 9 - python -m src
│   ├── gmail_client.py      # Seção 4
│   ├── pdf_extractor.py     # Seção 5
│   ├── email_processor.py   # Seção 6
│   └── main.py              # Seção 7 - Ponto de entrada principal
│
├── temp/
│
└── output/
    └── contas_a_pagar.json'''
```

---

## 3. requirements.txt

```txt
# requirements.txt
google-auth>=2.23.0
google-auth-oauthlib>=1.0.0
google-api-python-client>=2.108.0
pypdf>=3.17.0
pdfplumber>=0.10.0
python-dateutil>=2.8.2
requests>=2.31.0
```

##4. src/gmail_client.py

```
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
```


##5. src/pdf_extractor.py

```
"""
   src/pdf_extractor.py
   PDF Extractor - Extração de dados de boletos e faturas
"""

import re
import io
from typing import Dict, Optional, List
from datetime import datetime
import pdfplumber
from pypdf import PdfReader


class PDFExtractor:
    """Extrator de dados de PDFs de contas a pagar"""
    
    # Mapeamento de bancos por código de barras
    BANCO_CODIGOS = {
        '001': 'Banco do Brasil',
        '237': 'Bradesco',
        '341': 'Itaú',
        '104': 'Caixa Econômica',
        '033': 'Santander',
        '260': 'Nubank',
        '745': 'Citibank',
        '399': 'HSBC',
        '422': 'Safra',
        '756': 'Sicoob',
        '077': 'Inter',
    }
    
    def extrair_texto(self, pdf_bytes: bytes) -> str:
        """Extrai texto do PDF"""
        try:
            # Tenta com pdfplumber primeiro (melhor para tabelas)
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                texto = ''
                for page in pdf.pages:
                    texto += page.extract_text() or ''
                if texto.strip():
                    return texto
            
            # Fallback para pypdf
            reader = PdfReader(io.BytesIO(pdf_bytes))
            texto = ''
            for page in reader.pages:
                texto += page.extract_text() or ''
            return texto
            
        except Exception as e:
            raise ValueError(f'Erro ao extrair texto do PDF: {e}')
    
    def extrair_dados_boleto(self, texto: str) -> Dict:
        """
        Extrai dados estruturados do texto do PDF
        
        Args:
            texto: Texto extraído do PDF
            
        Returns:
            Dicionário com dados extraídos
        """
        dados = {
            'emissor': None,
            'banco_pagamento': None,
            'tipo': None,
            'vencimento': None,
            'valor': None,
            'codigo_barras': None,
            'linha_digitavel': None,
            'matricula': None,
            'apartamento': None,
            'bloco': None,
            'desconto': None,
            'multa': None,
        }
        
        # Limpa e normaliza texto
        texto = texto.replace('\n', ' ').replace('\r', ' ')
        texto = ' '.join(texto.split())
        
        # 1. Extrai código de barras (padrões comuns)
        dados['codigo_barras'] = self._extrair_codigo_barras(texto)
        
        # 2. Identifica banco de pagamento
        if dados['codigo_barras']:
            codigo_banco = dados['codigo_barras'][:3]
            dados['banco_pagamento'] = self.BANCO_CODIGOS.get(codigo_banco)
        
        # Se não identificou pelo código, tenta por texto
        if not dados['banco_pagamento']:
            dados['banco_pagamento'] = self._identificar_banco_texto(texto)
        
        # 3. Extrai linha digitável
        dados['linha_digitavel'] = self._extrair_linha_digitavel(texto)
        
        # 4. Extrai emissor
        dados['emissor'] = self._extrair_emissor(texto)
        
        # 5. Extrai tipo
        dados['tipo'] = self._extrair_tipo(texto)
        
        # 6. Extrai vencimento
        dados['vencimento'] = self._extrair_vencimento(texto)
        
        # 7. Extrai valor
        dados['valor'] = self._extrair_valor(texto)
        
        # 8. Extrai matrícula
        dados['matricula'] = self._extrair_matricula(texto)
        
        # 9. Extrai dados de condomínio
        dados['apartamento'] = self._extrair_apartamento(texto)
        dados['bloco'] = self._extrair_bloco(texto)
        
        return dados
    
    def _extrair_codigo_barras(self, texto: str) -> Optional[str]:
        """Extrai código de barras (44 dígitos)"""
        padroes = [
            r'\b(\d{44})\b',
            r'código de barras[:\s]*(\d{44})',
            r'codigo de barras[:\s]*(\d{44})',
            r'linha digitável[:\s]*(\d{44})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _identificar_banco_texto(self, texto: str) -> Optional[str]:
        """Identifica banco pelo texto"""
        bancos = {
            'bradesco': 'Bradesco',
            'itaú': 'Itaú',
            'itau': 'Itaú',
            'banco do brasil': 'Banco do Brasil',
            'caixa econômica': 'Caixa Econômica',
            'caixa economica': 'Caixa Econômica',
            'santander': 'Santander',
            'nubank': 'Nubank',
            'sicredi': 'Sicredi',
            'sicoob': 'Sicoob',
            'banco inter': 'Inter',
            'inter': 'Inter',
        }
        
        texto_lower = texto.lower()
        for key, value in bancos.items():
            if key in texto_lower:
                return value
        
        return None
    
    def _extrair_linha_digitavel(self, texto: str) -> Optional[str]:
        """Extrai linha digitável"""
        padroes = [
            r'\b(\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d{1}\s*\d{14})\b',
            r'\b(\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d{1}\s*\d{14})\b',
            r'linha digitável[:\s]*([\d\.\s]{47,48})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1).replace(' ', '')
        
        return None
    
    def _extrair_emissor(self, texto: str) -> Optional[str]:
        """Extrai emissor da cobrança"""
        emissores = {
            'nubank': 'Nubank',
            'banco do brasil': 'Banco do Brasil',
            'bradesco': 'Bradesco',
            'itau': 'Itaú',
            'itaú': 'Itaú',
            'caixa': 'Caixa Econômica',
            'santander': 'Santander',
            'vivo': 'Vivo',
            'cpfl': 'CPFL',
            'enel': 'Enel',
            'cis': 'CIS',
            'administradora': 'Administradora de Condomínio',
            'condominio': 'Administradora de Condomínio',
            'condomínio': 'Administradora de Condomínio',
            'sicoob': 'Sicoob',
            'sicredi': 'Sicredi',
        }
        
        texto_lower = texto.lower()
        
        for key, value in emissores.items():
            if key in texto_lower:
                return value
        
        padrao_empresa = r'(?:empresa|prestador|favorecido)[:\s]+([A-ZÀ-Ú][A-ZÀ-Ú\s]{2,})'
        match = re.search(padrao_empresa, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extrair_tipo(self, texto: str) -> Optional[str]:
        """Extrai tipo de documento"""
        texto_lower = texto.lower()
        
        if 'boleto' in texto_lower:
            return 'boleto'
        elif 'fatura' in texto_lower or 'cartão' in texto_lower or 'cartao' in texto_lower:
            return 'fatura'
        elif 'carne' in texto_lower or 'carnê' in texto_lower:
            return 'carnê'
        
        return None
    
    def _extrair_vencimento(self, texto: str) -> Optional[str]:
        """Extrai data de vencimento no formato YYYY-MM-DD"""
        padroes = [
            (r'vencimento[:\s]*(\d{2})[/-](\d{2})[/-](\d{4})', '%d/%m/%Y'),
            (r'vencimento[:\s]*(\d{2})[/-](\d{2})[/-](\d{2})', '%d/%m/%y'),
            (r'vencimento[:\s]*(\d{4})[/-](\d{2})[/-](\d{2})', '%Y-%m-%d'),
            (r'vencimento[:\s]*(\d{2})\.(\d{2})\.(\d{4})', '%d.%m.%Y'),
        ]
        
        for padrao, formato in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                try:
                    if formato == '%d/%m/%y':
                        dia, mes, ano = match.groups()
                        ano = f'20{ano}' if int(ano) < 70 else f'19{ano}'
                        data_str = f'{dia}/{mes}/{ano}'
                        formato = '%d/%m/%Y'
                    else:
                        data_str = '-'.join(match.groups())
                    
                    data = datetime.strptime(data_str, formato)
                    return data.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None
    
    def _extrair_valor(self, texto: str) -> Optional[float]:
        """Extrai valor decimal"""
        padroes = [
            r'valor[:\s]*R?\$?\s*([\d,]+\.\d{2})',
            r'valor[:\s]*R?\$?\s*([\d.]+\,\d{2})',
            r'R?\$?\s*([\d,]+\.\d{2})',
            r'R?\$?\s*([\d.]+\,\d{2})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                valor_str = match.group(1)
                if ',' in valor_str and '.' in valor_str:
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                elif ',' in valor_str:
                    valor_str = valor_str.replace(',', '.')
                try:
                    return round(float(valor_str), 2)
                except:
                    continue
        
        return None
    
    def _extrair_matricula(self, texto: str) -> Optional[str]:
        """Extrai número de matrícula/contrato"""
        padroes = [
            r'matrícula[:\s]*([A-Z0-9\-]{6,})',
            r'matricula[:\s]*([A-Z0-9\-]{6,})',
            r'contrato[:\s]*([A-Z0-9\-]{6,})',
            r'n[°º]?\s*[:\s]*([A-Z0-9\-]{6,})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extrair_apartamento(self, texto: str) -> Optional[str]:
        """Extrai número do apartamento (condomínio)"""
        padroes = [
            r'apartamento[:\s]*([A-Z0-9\-]{1,10})',
            r'apto[:\s]*([A-Z0-9\-]{1,10})',
            r'ap[.:\s]*([A-Z0-9\-]{1,10})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extrair_bloco(self, texto: str) -> Optional[str]:
        """Extrai bloco (condomínio)"""
        padroes = [
            r'bloco[:\s]*([A-Z0-9\-]{1,10})',
            r'bl[.:\s]*([A-Z0-9\-]{1,10})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extrair_dados_condominio(self, texto: str) -> Dict:
        """Extrai dados específicos de condomínio"""
        dados = {}
        
        apto = self._extrair_apartamento(texto)
        if apto:
            dados['apartamento'] = apto
        
        bloco = self._extrair_bloco(texto)
        if bloco:
            dados['bloco'] = bloco
        
        return dados
```
---

##6. src/email_processor.py

```
"""
   src/email_processor.py
   Email Processor - Orquestra o processamento completo
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

from gmail_client import GmailClient
from pdf_extractor import PDFExtractor


class EmailProcessor:
    """Processador principal de e-mails"""
    
    def __init__(self, gmail_client: GmailClient, pdf_extractor: PDFExtractor):
        self.gmail = gmail_client
        self.pdf_extractor = pdf_extractor
        self.temp_dir = 'temp'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def processar(self, dias: int = 90, max_emails: int = 200) -> Dict:
        """
        Processa e-mails e gera JSON estruturado
        
        Args:
            dias: Número de dias para buscar
            max_emails: Máximo de e-mails a processar
            
        Returns:
            Dicionário com dados estruturados
        """
        print(f'🔍 Buscando e-mails dos últimos {dias} dias...')
        
        emails = self.gmail.buscar_emails(dias=dias, max_results=max_emails)
        print(f'📧 Encontrados {len(emails)} e-mails com PDFs')
        
        contas = []
        total_pdfs_lidos = 0
        total_pdfs_com_erro = 0
        total_emails_processados = 0
        
        for email in emails:
            total_emails_processados += 1
            print(f'  📩 Processando: {email["assunto"][:50]}...')
            
            for anexo in email['anexos']:
                try:
                    pdf_bytes = self.gmail.baixar_anexo(
                        email['id'], 
                        anexo['attachmentId']
                    )
                    
                    if not pdf_bytes:
                        continue
                    
                    temp_path = os.path.join(self.temp_dir, anexo['filename'])
                    with open(temp_path, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    texto = self.pdf_extractor.extrair_texto(pdf_bytes)
                    dados_pdf = self.pdf_extractor.extrair_dados_boleto(texto)
                    
                    conta = {
                        'email_id': email['id'],
                        'data_email': email['data'],
                        'remetente': email['remetente'],
                        'assunto': email['assunto'],
                        'emissor': dados_pdf.get('emissor'),
                        'banco_pagamento': dados_pdf.get('banco_pagamento'),
                        'tipo': dados_pdf.get('tipo'),
                        'categoria': self._determinar_categoria(email, dados_pdf),
                        'vencimento': dados_pdf.get('vencimento'),
                        'valor': dados_pdf.get('valor'),
                        'codigo_barras': dados_pdf.get('codigo_barras'),
                        'linha_digitavel': dados_pdf.get('linha_digitavel'),
                        'matricula': dados_pdf.get('matricula'),
                        'apartamento': dados_pdf.get('apartamento'),
                        'bloco': dados_pdf.get('bloco'),
                        'desconto': dados_pdf.get('desconto'),
                        'multa': dados_pdf.get('multa'),
                        'status': self._calcular_status(dados_pdf.get('vencimento')),
                        'anexo_pdf': anexo['filename'],
                        'erro': None
                    }
                    
                    contas.append(conta)
                    total_pdfs_lidos += 1
                    
                    os.remove(temp_path)
                    
                except Exception as e:
                    total_pdfs_com_erro += 1
                    print(f'    ❌ Erro no PDF {anexo["filename"]}: {e}')
                    
                    conta = {
                        'email_id': email['id'],
                        'data_email': email['data'],
                        'remetente': email['remetente'],
                        'assunto': email['assunto'],
                        'emissor': None,
                        'banco_pagamento': None,
                        'tipo': None,
                        'categoria': self._determinar_categoria(email, {}),
                        'vencimento': None,
                        'valor': None,
                        'codigo_barras': None,
                        'linha_digitavel': None,
                        'matricula': None,
                        'apartamento': None,
                        'bloco': None,
                        'desconto': None,
                        'multa': None,
                        'status': None,
                        'anexo_pdf': anexo['filename'],
                        'erro': str(e)
                    }
                    contas.append(conta)
        
        json_output = self._gerar_json(contas, total_emails_processados, 
                                      total_pdfs_lidos, total_pdfs_com_erro)
        
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'contas_a_pagar.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)
        
        print(f'\n✅ Processamento concluído!')
        print(f'📄 JSON salvo em: {output_path}')
        print(f'📊 Total de contas encontradas: {len(contas)}')
        print(f'💰 Total geral: R$ {json_output["total_geral"]:.2f}')
        
        return json_output
    
    def _determinar_categoria(self, email: Dict, dados_pdf: Dict) -> str:
        """Determina a categoria da conta"""
        assunto = email['assunto'].lower()
        remetente = email['remetente'].lower()
        emissor = dados_pdf.get('emissor', '').lower()
        
        if 'condominio' in assunto or 'condomínio' in assunto:
            return 'condominio'
        
        if 'cartão' in assunto or 'cartao' in assunto or 'visa' in assunto or 'mastercard' in assunto:
            return 'cartao'
        
        if any(palavra in assunto for palavra in ['água', 'agua', 'esgoto', 'luz', 'energia', 'elétrica', 'eletrica']):
            return 'utilidade'
        
        if any(palavra in assunto for palavra in ['internet', 'celular', 'telefone', 'vivo']):
            return 'telecom'
        
        if 'boleto' in assunto or dados_pdf.get('tipo') == 'boleto':
            return 'boleto'
        
        if any(em in emissor for em in ['nubank', 'banco do brasil', 'bradesco', 'itau', 'caixa', 'santander']):
            return 'boleto'
        
        return 'outros'
    
    def _calcular_status(self, vencimento: Optional[str]) -> Optional[str]:
        """Calcula status do vencimento"""
        if not vencimento:
            return None
        
        try:
            data_venc = datetime.strptime(vencimento, '%Y-%m-%d')
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            dias_ate = (data_venc - hoje).days
            
            if dias_ate < 0:
                return 'vencido'
            elif dias_ate == 0:
                return 'hoje'
            elif dias_ate <= 3:
                return '3_dias'
            elif dias_ate <= 7:
                return 'ate_7_dias'
            else:
                return 'mais_de_7_dias'
        except:
            return None
    
    def _gerar_json(self, contas: List[Dict], total_emails: int, 
                    total_pdfs_lidos: int, total_pdfs_com_erro: int) -> Dict:
        """Gera JSON estruturado de saída"""
        resumo_categorias = {
            'cartao': {'quantidade': 0, 'total': 0.0},
            'boleto': {'quantidade': 0, 'total': 0.0},
            'condominio': {'quantidade': 0, 'total': 0.0},
            'utilidade': {'quantidade': 0, 'total': 0.0},
            'telecom': {'quantidade': 0, 'total': 0.0},
            'outros': {'quantidade': 0, 'total': 0.0}
        }
        
        alertas = {
            'vencidos': [],
            'hoje': [],
            'proximos_3_dias': []
        }
        
        total_geral = 0.0
        valores = []
        vencimento_mais_proximo = None
        
        for conta in contas:
            categoria = conta.get('categoria', 'outros')
            if categoria in resumo_categorias:
                resumo_categorias[categoria]['quantidade'] += 1
                if conta.get('valor'):
                    resumo_categorias[categoria]['total'] += conta['valor']
            
            if conta.get('valor'):
                total_geral += conta['valor']
                valores.append(conta['valor'])
            
            if conta.get('status') == 'vencido':
                alertas['vencidos'].append(conta['email_id'])
            elif conta.get('status') == 'hoje':
                alertas['hoje'].append(conta['email_id'])
            elif conta.get('status') == '3_dias':
                alertas['proximos_3_dias'].append(conta['email_id'])
            
            if conta.get('vencimento'):
                if not vencimento_mais_proximo or conta['vencimento'] < vencimento_mais_proximo:
                    vencimento_mais_proximo = conta['vencimento']
        
        del resumo_categorias['outros']
        
        media_valor = sum(valores) / len(valores) if valores else 0.0
        
        return {
            'data_execucao': datetime.now().isoformat(),
            'periodo_busca': {
                'inicio': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'fim': datetime.now().strftime('%Y-%m-%d'),
                'dias': 90
            },
            'total_contas': len(contas),
            'total_geral': round(total_geral, 2),
            'resumo_por_categoria': resumo_categorias,
            'contas': contas,
            'alertas': alertas,
            'estatisticas': {
                'total_emails_processados': total_emails,
                'total_pdfs_lidos': total_pdfs_lidos,
                'total_pdfs_com_erro': total_pdfs_com_erro,
                'media_valor': round(media_valor, 2),
                'vencimento_mais_proximo': vencimento mais
                'vencimento_mais_proximo': vencimento_mais_proximo
            }
        }
```
---

##7. src/_main_.py

```
"""
   src/_main_.py
   Ponto de entrada principal do sistema
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Adiciona src ao path para importação
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_client import GmailClient
from pdf_extractor import PDFExtractor
from email_processor import EmailProcessor


def verificar_credentials():
    """Verifica se o arquivo credentials.json existe"""
    cred_path = 'credentials/credentials.json'
    
    if not os.path.exists(cred_path):
        print('\n❌ Arquivo credentials.json não encontrado!')
        print('\n📋 Instruções para obter credentials.json:')
        print('  1. Acesse https://console.cloud.google.com/')
        print('  2. Crie um novo projeto ou selecione um existente')
        print('  3. Ative a Gmail API: APIs & Services > Library > Gmail API > Enable')
        print('  4. Configure OAuth: APIs & Services > Credentials > Create Credentials > OAuth Client ID')
        print('  5. Tipo de aplicação: Desktop app')
        print('  6. Baixe o arquivo JSON e renomeie para credentials.json')
        print('  7. Coloque o arquivo na pasta credentials/')
        print('\n   Pasta esperada: credentials/credentials.json')
        return False
    
    return True


def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    try:
        import google.auth
        import googleapiclient
        import pdfplumber
        import pypdf
        return True
    except ImportError as e:
        print(f'\n❌ Dependência faltando: {e}')
        print('\n📋 Instale as dependências:')
        print('  pip install -r requirements.txt')
        return False


def main():
    """Função principal"""
    print('\n' + '='*60)
    print('📧 LEITOR DE EMAILS - CONTAS A PAGAR')
    print('='*60 + '\n')
    
    # Verifica pré-requisitos
    if not verificar_credentials():
        sys.exit(1)
    
    if not verificar_dependencias():
        sys.exit(1)
    
    try:
        # Inicializa componentes
        print('🔐 Autenticando no Gmail...')
        gmail_client = GmailClient()
        gmail_client.authenticate()
        print('✅ Autenticação realizada com sucesso!\n')
        
        pdf_extractor = PDFExtractor()
        processor = EmailProcessor(gmail_client, pdf_extractor)
        
        # Processa e-mails
        print('📥 Iniciando processamento...\n')
        resultado = processor.processar(dias=90, max_emails=200)
        
        # Exibe resumo
        print('\n' + '='*60)
        print('📊 RESUMO DAS CONTAS A PAGAR')
        print('='*60)
        print(f'📅 Período: {resultado["periodo_busca"]["inicio"]} a {resultado["periodo_busca"]["fim"]}')
        print(f'📧 Total de e-mails processados: {resultado["estatisticas"]["total_emails_processados"]}')
        print(f'📄 Total de contas encontradas: {resultado["total_contas"]}')
        print(f'💰 Total geral: R$ {resultado["total_geral"]:.2f}')
        print(f'📊 Média por conta: R$ {resultado["estatisticas"]["media_valor"]:.2f}')
        
        print('\n📂 Resumo por categoria:')
        for categoria, dados in resultado['resumo_por_categoria'].items():
            if dados['quantidade'] > 0:
                print(f'  • {categoria.capitalize()}: {dados["quantidade"]} contas | R$ {dados["total"]:.2f}')
        
        print('\n⚠️ Alertas:')
        if resultado['alertas']['vencidos']:
            print(f'  🔴 Vencidos: {len(resultado["alertas"]["vencidos"])} contas')
        if resultado['alertas']['hoje']:
            print(f'  🟠 Vencem hoje: {len(resultado["alertas"]["hoje"])} contas')
        if resultado['alertas']['proximos_3_dias']:
            print(f'  🟡 Vencem em até 3 dias: {len(resultado["alertas"]["proximos_3_dias"])} contas')
        if not any(resultado['alertas'].values()):
            print('  ✅ Nenhum alerta urgente')
        
        if resultado['estatisticas']['vencimento_mais_proximo']:
            print(f'\n📅 Vencimento mais próximo: {resultado["estatisticas"]["vencimento_mais_proximo"]}')
        
        if resultado['estatisticas']['total_pdfs_com_erro'] > 0:
            print(f'\n⚠️ PDFs com erro: {resultado["estatisticas"]["total_pdfs_com_erro"]}')
        
        print('\n' + '='*60)
        print('✅ Processamento concluído com sucesso!')
        print('📄 JSON salvo em: output/contas_a_pagar.json')
        print('='*60 + '\n')
        
    except Exception as e:
        print(f'\n❌ Erro durante a execução: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
```

---

##8. src/_init_.py

```
"""
src/__init__.py
Pacote src - Módulos para leitura de e-mails e extração de dados de contas a pagar
"""

from .gmail_client import GmailClient
from .pdf_extractor import PDFExtractor
from .email_processor import EmailProcessor

__version__ = '1.0.0'
__all__ = ['GmailClient', 'PDFExtractor', 'EmailProcessor']
```

---

##9. src/main.py (Opcional - permite executar como módulo)

```
"""
   src/__main__.py
   Permite executar o pacote com: python -m src
"""

from .main import main

if __name__ == '__main__':
    main()
```

---

##10. credentials/credentials.json - INSTRUÇÕES

```
/*
INSTRUÇÕES PARA OBTER O ARQUIVO credentials.json:

1. Acesse https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Ative a Gmail API:
   - Menu > APIs & Services > Library
   - Busque por "Gmail API"
   - Clique em "Enable"
4. Configure OAuth 2.0:
   - Menu > APIs & Services > Credentials
   - Clique em "+ CREATE CREDENTIALS"
   - Selecione "OAuth client ID"
   - Application type: "Desktop app"
   - Dê um nome (ex: "Leitor de Contas")
   - Clique em "CREATE"
5. Baixe o arquivo JSON:
   - Clique no ícone de download ao lado do client ID criado
   - O arquivo baixado terá um nome como: client_secret_XXXXX.apps.googleusercontent.com.json
6. Renomeie o arquivo para "credentials.json"
7. Coloque na pasta credentials/ do projeto

ESTRUTURA ESPERADA:
credentials/
└── credentials.json    <- Arquivo baixado e renomeado

CONTEÚDO DO credentials.json (exemplo):
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "seu-projeto",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
*/
```
---

## 11. README.md - Instruções para o Usuário

# Leitor de E-mails de Contas a Pagar

Sistema para ler e-mails do Gmail, extrair dados de faturas e boletos em PDF, e gerar um demonstrativo estruturado das contas a pagar.

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Conta Gmail com acesso à API
- Google Cloud Console configurado

## 🚀 Instalação

1. Clone ou baixe este repositório
2. Crie e ative um ambiente virtual:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

###Linux/Mac:

```
python3 -m venv venv
source venv/bin/activate
```
3. Instale as dependências:

```
pip install -r requirements.txt
```
---

4. Configure as credenciais do Gmail:

- Siga as instruções em credentials/credentials.json
- Coloque o arquivo em credentials/credentials.json

##🔧 Execução

Execute o script principal:

```
python src/main.py
```


O navegador abrirá para autenticação:

1. Faça login com a conta Gmail desejada
2. Autorize o acesso
3. O token será salvo para próximas execuções

##📤 Saída

O sistema gera um arquivo output/contas_a_pagar.json com:

- Resumo por categoria (cartão, boleto, condomínio, utilidade, telecom)
- Lista detalhada de todas as contas
- Alertas (vencidos, vencem hoje, vencem em 3 dias)
- Estatísticas gerais

##🗂️ Estrutura do Projeto

```
leitor-contas-pagar/
├── README.md
├── requirements.txt
├── credentials/
│   ├── credentials.json      # Baixado do Google Cloud Console
│   └── token.pickle           # Gerado automaticamente (não commitar)
├── src/
│   ├── __init__.py
│   ├── gmail_client.py        # Conexão com Gmail
│   ├── pdf_extractor.py       # Extração de dados de PDF
│   ├── email_processor.py     # Orquestração
│   └── main.py                # Ponto de entrada
├── temp/                      # Arquivos temporários (não commitar)
└── output/
    └── contas_a_pagar.json    # JSON de saída (não commitar)
```
---

##⚙️ Configurações

As principais configurações estão em src/email_processor.py:

- dias: 90 (dias para trás)
- max_emails: 200 (máximo de e-mails processados)

Para alterar, modifique os parâmetros na chamada processor.processar() em src/main.py.

## 🛠️ Solução de Problemas

Erro: "Arquivo credentials.json não encontrado"
Verifique se o arquivo está em credentials/credentials.json

Baixe novamente do Google Cloud Console

###Erro: "Dependência faltando"

```
pip install -r requirements.txt
```

###Erro de autenticação

```
- Delete credentials/token.pickle e execute novamente
```

### O navegador não abre### 

```
- Verifique se o navegador padrão está configurado
- Ou execute com --no-browser e cole a URL manualmente
```

## 🔐 Segurança

```
- NUNCA commite token.pickle ou credentials.json
- NUNCA compartilhe o JSON de saída com dados sensíveis
- Os PDFs são deletados após o processamento

```

---

## 12. Script de Setup Automático (setup.py)

```python
"""
setup.py - Script para configurar o ambiente automaticamente
"""

import os
import sys
import subprocess

def criar_estrutura():
    """Cria a estrutura de diretórios"""
    diretorios = ['credentials', 'temp', 'output', 'src']
    for d in diretorios:
        os.makedirs(d, exist_ok=True)
        print(f'📁 Criado: {d}/')
    
    # Cria __init__.py em src se não existir
    src_init = 'src/__init__.py'
    if not os.path.exists(src_init):
        with open(src_init, 'w') as f:
            f.write('# Pacote src\n')
        print(f'📄 Criado: {src_init}')
    
    print('\n✅ Estrutura criada com sucesso!')

def instalar_dependencias():
    """Instala as dependências"""
    print('\n📦 Instalando dependências...')
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print('✅ Dependências instaladas com sucesso!')
    except subprocess.CalledProcessError:
        print('❌ Erro ao instalar dependências. Execute manualmente:')
        print('   pip install -r requirements.txt')

def main():
    print('='*60)
    print('🔧 CONFIGURAÇÃO AUTOMÁTICA - LEITOR DE CONTAS')
    print('='*60 + '\n')
    
    criar_estrutura()
    
    if os.path.exists('requirements.txt'):
        resposta = input('\nInstalar dependências agora? (s/N): ')
        if resposta.lower() == 's':
            instalar_dependencias()
    
    print('\n' + '='*60)
    print('✅ Configuração concluída!')
    print('\n📋 Próximos passos:')
    print('  1. Coloque o arquivo credentials.json em credentials/')
    print('  2. Execute: python src/main.py')
    print('='*60)

if __name__ == '__main__':
    main()
```

---

### 12. Script de Setup Automático (opcional)

```python
"""
setup.py - Script para configurar o ambiente automaticamente
"""

import os
import sys
import subprocess

def criar_estrutura():
    """Cria a estrutura de diretórios"""
    diretorios = ['credentials', 'temp', 'output']
    for d in diretorios:
        os.makedirs(d, exist_ok=True)
        print(f'📁 Criado: {d}/')
    
    # Cria __init__.py em src se não existir
    src_init = 'src/__init__.py'
    if not os.path.exists(src_init):
        with open(src_init, 'w') as f:
            f.write('# Pacote src\n')
        print(f'📄 Criado: {src_init}')
    
    print('\n✅ Estrutura criada com sucesso!')

def instalar_dependencias():
    """Instala as dependências"""
    print('\n📦 Instalando dependências...')
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print('✅ Dependências instaladas com sucesso!')
    except subprocess.CalledProcessError:
        print('❌ Erro ao instalar dependências. Execute manualmente:')
        print('   pip install -r requirements.txt')

def main():
    print('='*60)
    print('🔧 CONFIGURAÇÃO AUTOMÁTICA - LEITOR DE CONTAS')
    print('='*60 + '\n')
    
    criar_estrutura()
    
    if os.path.exists('requirements.txt'):
        resposta = input('\nInstalar dependências agora? (s/N): ')
        if resposta.lower() == 's':
            instalar_dependencias()
    
    print('\n' + '='*60)
    print('✅ Configuração concluída!')
    print('\n📋 Próximos passos:')
    print('  1. Coloque o arquivo credentials.json em credentials/')
    print('  2. Execute: python src/main.py')
    print('='*60)

if __name__ == '__main__':
    main()

```
---

## 13. FORMATO DE SAÍDA JSON

Agora o arquivo completo deve incluir:

```
{
  "data_execucao": "2026-08-17T10:30:00.000Z",
  "periodo_busca": {
    "inicio": "2026-05-19",
    "fim": "2026-08-17",
    "dias": 90
  },
  "total_contas": 0,
  "total_geral": 0.00,
  "resumo_por_categoria": {
    "cartao": { "quantidade": 0, "total": 0.00 },
    "boleto": { "quantidade": 0, "total": 0.00 },
    "condominio": { "quantidade": 0, "total": 0.00 },
    "utilidade": { "quantidade": 0, "total": 0.00 },
    "telecom": { "quantidade": 0, "total": 0.00 }
  },
  "contas": [
    {
      "email_id": "string",
      "data_email": "2026-08-13T10:30:00Z",
      "remetente": "string",
      "assunto": "string",
      "emissor": "string",
      "banco_pagamento": "string | null",
      "tipo": "boleto | fatura | carnê",
      "categoria": "cartao | boleto | condominio | utilidade | telecom",
      "vencimento": "2026-08-13",
      "valor": 0.00,
      "codigo_barras": "string | null",
      "linha_digitavel": "string | null",
      "matricula": "string | null",
      "apartamento": "string | null",
      "bloco": "string | null",
      "desconto": 0.00 | null,
      "multa": 0.00 | null,
      "status": "vencido | hoje | 3_dias | ate_7_dias | mais_de_7_dias",
      "anexo_pdf": "nome_arquivo.pdf",
      "erro": "string | null"
    }
  ],
  "alertas": {
    "vencidos": [],
    "hoje": [],
    "proximos_3_dias": []
  },
  "estatisticas": {
    "total_emails_processados": 0,
    "total_pdfs_lidos": 0,
    "total_pdfs_com_erro": 0,
    "media_valor": 0.00,
    "vencimento_mais_proximo": "2026-08-13 | null"
  }
}
```

---

# 14. EXEMPLO DE USO

## Como o Agente Deve Responder

##Usuário##: "Quero processar meus e-mails para ver as contas a pagar"

##Agente##:

Vou gerar o sistema completo para ler seus e-mails e extrair as contas a pagar.

O sistema irá:

1. Conectar ao seu Gmail via OAuth 2.0
2. Buscar e-mails dos últimos 90 dias com anexos PDF
3. Filtrar faturas, boletos e contas de serviços
4. Extrair dados como vencimento, valor, emissor e banco
5. Gerar um JSON estruturado com todas as informações

---

##Pré-requisitos##:

1. Python 3.9+
2. Conta Gmail
3. Credenciais OAuth do Google Cloud Console

---
 
##Instalação:##

1. Crie uma pasta para o projeto
2. Copie os arquivos que vou gerar
3. Execute python setup.py para configurar automaticamente
4. Coloque o arquivo credentials.json na pasta credentials/
5. Execute python src/main.py

Aqui está o código completo:

	[Gera todos os arquivos listados neste documento]

Após executar, me envie o conteúdo do arquivo output/contas_a_pagar.json para eu analisar e apresentar o demonstrativo.

---

## Análise do JSON pelo Agente

Quando o usuário enviar o JSON, o agente deve:

1. ##Valida## a estrutura do JSON

2. ##Apresentar## resumo visual:

	- Total de contas e valor geral
	- Resumo por categoria em tabela
	- Alertas de vencimento com cores
	- Lista detalhada de todas as contas

3. ##Recomendar## próximos passos:

	- Quais contas venceram
	- Quais vencem hoje
	- Quais vencem nos próximos dias

---

## RESUMO DA ESTRUTURA COMPLETA DE ARQUIVOS

```
leitor-contas-pagar/
│
├── README.md                          # Instruções de uso
├── requirements.txt                   # Dependências Python
├── setup.py                           # Script de setup automático
│
├── credentials/
│   └── credentials.json               # Baixado do Google Cloud Console
│
├── src/
│   ├── __init__.py                    # Pacote Python
│   ├── __main__.py                    # Ponto de entrada como módulo
│   ├── gmail_client.py                # Conexão Gmail
│   ├── pdf_extractor.py               # Extração de PDFs
│   ├── email_processor.py             # Orquestração
│   └── main.py                        # Ponto de entrada principal
│
├── temp/                              # PDFs temporários
│
└── output/
    └── contas_a_pagar.json            # JSON de saída
```

---

## INSTRUÇÕES FINAIS PARA O AGENTE

Quando o usuário pedir para processar e-mails:

1. ##Gere todo o código acima## de forma organizada
2. ##Explique## o fluxo de trabalho passo-a-passo
3. ##Instrua## sobre como obter o credentials.json
4. ##Após o usuário executar## e enviar o JSON, analise e apresente:

	- Tabela com todas as contas
	- Resumo por categoria
	- Alertas de vencimento
	- Recomendações de pagamento

##NUNCA## tente acessar Gmail, PDFs ou arquivos diretamente — o DeepSeek não tem essa capacidade.
