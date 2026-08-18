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
                if not vencimento_mais_proximo or conta['vencimento'] < vencimento_mais_proximo:
                    vencimento_mais_proximo = conta['vencimento']
        
        # Remove categoria 'outros' do resumo final
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