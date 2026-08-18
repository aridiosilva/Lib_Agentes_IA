"""
src/email_processor.py
Email Processor - Orquestração do processamento de e-mails e PDFs
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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
                'vencimento_mais_proximo': vencimento_mais_proximo
            }
        }