"""
src/__init__.py
Pacote src - Módulos para leitura de e-mails e extração de dados de contas a pagar
"""

import os
import sys
# Adiciona src ao path para importação
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_client import GmailClient
from pdf_extractor import PDFExtractor
from email_processor import EmailProcessor

__version__ = '1.0.0'
__all__ = ['GmailClient', 'PDFExtractor', 'EmailProcessor']