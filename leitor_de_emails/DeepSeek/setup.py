
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