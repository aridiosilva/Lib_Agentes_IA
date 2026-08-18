# Substituir API Gmail pela API Amazon WorkMail (via IMAP)

Este plano detalha a migração do cliente de leitura de e-mails para utilizar o Amazon WorkMail através do protocolo padrão IMAP Seguro (IMAPS).

## User Review Required

> [!IMPORTANT]
> A migração utilizará o protocolo **IMAP com SSL (porta 993)**. Para isso, o usuário precisará configurar um arquivo de credenciais simples contendo o servidor IMAP do Amazon WorkMail, o e-mail completo e a senha da conta.

> [!WARNING]
> Certifique-se de que o acesso IMAP está habilitado para o seu usuário no console administrativo do Amazon WorkMail.

## Open Questions

1. **Servidor IMAP**: O padrão do Amazon WorkMail varia por região (ex: `imap.mail.us-east-1.awsapps.com` para a Virgínia do Norte). O plano prevê ler essa configuração do arquivo de credenciais. Está de acordo?
2. **Formato do arquivo de credenciais**: Substituiremos o arquivo `credentials.json` do Google por `workmail_credentials.json` no formato JSON.

---

## Proposed Changes

### credentials/

#### [NEW] [workmail_credentials.json](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/credentials/workmail_credentials.json)
Arquivo de configuração local com os dados de acesso ao Amazon WorkMail.

---

### src/

#### [NEW] [workmail_client.py](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/workmail_client.py)
Implementa a classe `WorkmailClient` que se conecta via `imaplib` ao servidor do Amazon WorkMail, lista as mensagens, filtra por data e palavras-chave, e extrai os anexos PDF. Esta classe substitui a funcionalidade do Gmail.

#### [DELETE] [gmail_client.py](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/gmail_client.py)
Remoção do cliente antigo do Gmail.

#### [MODIFY] [__init__.py](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/__init__.py)
Atualizar a exportação de `GmailClient` para `WorkmailClient`.

#### [MODIFY] [main.py](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/main.py)
Modificar a importação de `GmailClient` para `WorkmailClient`, atualizar a chamada de autenticação e a checagem do arquivo de credenciais.

#### [MODIFY] [email_processor.py](file:///c:/Users/as294/Lib_Agentes_IA/leitor_de_emails/DeepSeek/src/email_processor.py)
Ajustar o tipo aceito no construtor para `WorkmailClient`. As assinaturas dos métodos `buscar_emails` e `baixar_anexo` serão mantidas idênticas às originais para evitar impacto na lógica de processamento de e-mails.

---

## Verification Plan

### Automated Tests
- Testar a importação correta rodando `python check_deps.py` (ou um validador de importação).
- Executar `python -m src` para validar a inicialização do novo cliente e leitura das credenciais locais.

### Manual Verification
- O usuário preencherá o arquivo `credentials/workmail_credentials.json` com dados reais e executará a aplicação para validar a busca e extração de boletos.
