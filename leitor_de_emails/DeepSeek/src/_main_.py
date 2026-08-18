"""
src/main.py
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