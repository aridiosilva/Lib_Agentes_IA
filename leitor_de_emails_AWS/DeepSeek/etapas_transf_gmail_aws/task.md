# Tarefas de Implementação

- `[x]` Criar arquivo `credentials/workmail_credentials.json` com template padrão
- `[x]` Criar o novo cliente `src/workmail_client.py` (usando `imaplib`)
- `[x]` Remover o antigo `src/gmail_client.py`
- `[x]` Modificar `src/__init__.py` para exportar `WorkmailClient` em vez de `GmailClient`
- `[x]` Adaptar `src/main.py` para utilizar o `WorkmailClient` e validar `workmail_credentials.json`
- `[x]` Adaptar `src/email_processor.py` para receber `WorkmailClient`
- `[x]` Testar e validar a execução da aplicação
