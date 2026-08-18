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

from workmail_client import WorkmailClient
from pdf_extractor import PDFExtractor
from email_processor import EmailProcessor


def verificar_credentials():
    """Verifica se o arquivo workmail_credentials.json existe"""
    cred_path = 'credentials/workmail_credentials.json'
    
    if not os.path.exists(cred_path):
        print('\n❌ Arquivo workmail_credentials.json não encontrado!')
        print('\n📋 Instruções para obter/criar workmail_credentials.json:')
        print('  1. Crie um arquivo com o nome workmail_credentials.json na pasta credentials/')
        print('  2. Insira a seguinte estrutura preenchida com seus dados:')
        print('     {')
        print('       "imap_server": "imap.mail.us-east-1.awsapps.com",')
        print('       "username": "seu-usuario@seu-dominio.awsapps.com",')
        print('       "password": "sua-senha-aqui"')
        print('     }')
        print('\n   Pasta esperada: credentials/workmail_credentials.json')
        return False
    
    return True


def verificar_dependencias():
    """Verifica se as dependências do leitor estão instaladas"""
    try:
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
    print('📧 LEITOR DE EMAILS - CONTAS A PAGAR (AMAZON WORKMAIL)')
    print('='*60 + '\n')
    
    # Verifica pré-requisitos
    if not verificar_credentials():
        sys.exit(1)
    
    if not verificar_dependencias():
        sys.exit(1)
    
    workmail_client = None
    try:
        # Inicializa componentes
        print('🔐 Autenticando no Amazon WorkMail...')
        workmail_client = WorkmailClient()
        workmail_client.authenticate()
        print('✅ Autenticação realizada com sucesso!\n')
        
        pdf_extractor = PDFExtractor()
        processor = EmailProcessor(workmail_client, pdf_extractor)
        
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
    finally:
        if workmail_client:
            workmail_client.logout()


if __name__ == '__main__':
    main()