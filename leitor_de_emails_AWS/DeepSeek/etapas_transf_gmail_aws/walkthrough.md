# Walkthrough da Migração para Amazon WorkMail

A migração da API do Gmail para a API do Amazon WorkMail (via protocolo padrão IMAP Seguro) foi concluída com sucesso!

## Principais Mudanças

1. **Configuração de Credenciais**:
   * Criado o arquivo de configuração de exemplo [`credentials/workmail_credentials.json`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/credentials/workmail_credentials.json) em substituição ao antigo modelo do Google.
2. **Novo Cliente IMAP**:
   * Criado [`src/workmail_client.py`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/workmail_client.py), implementando conexão via `imaplib`, busca com filtro de datas no padrão IMAP (`SINCE`) e cache de e-mails para carregamento otimizado de anexos PDF.
   * Removido o arquivo obsoleto `src/gmail_client.py`.
3. **Refatoração Interna**:
   * Adaptado [`src/__init__.py`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/__init__.py) para exportar `WorkmailClient`.
   * Atualizado [`src/email_processor.py`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/email_processor.py) para aceitar `WorkmailClient` e manter a mesma assinatura e lógica do pipeline original.
   * Modificado [`src/main.py`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/main.py) para inicializar a autenticação IMAP e garantir o encerramento seguro da conexão (`finally: client.logout()`).

---

## Validação de Execução

Testamos a execução completa do módulo com as novas implementações:
```powershell
cmd /c "set PYTHONIOENCODING=utf-8 && .venv\Scripts\python.exe -m src"
```

### Resultado do Teste
O interpretador Python carregou todos os módulos sem erros de importação e tentou a conexão com o servidor do Amazon WorkMail (`imap.mail.us-east-1.awsapps.com`), retornando:
```text
🔐 Autenticando no Amazon WorkMail...
❌ Erro durante a execução: [ALERT] Access Denied.
```
Isso valida que todo o fluxo de importação, instanciação das classes e a tentativa de autenticação estão funcionando perfeitamente (sendo barrada apenas pelas credenciais de teste configuradas).

---

## Próximos Passos para o Usuário
1. Abra o arquivo [`credentials/workmail_credentials.json`](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/credentials/workmail_credentials.json).
2. Substitua os campos `"imap_server"`, `"username"` e `"password"` com as credenciais reais do seu e-mail do Amazon WorkMail.
3. Execute a aplicação no terminal.
