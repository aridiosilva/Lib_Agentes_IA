# Como incluir tools para acesso ao Gmail

O caminho recomendado para incluir ferramentas com acesso ao Gmail é usar a **Gmail API com OAuth 2.0**.

Evite solicitar a senha do usuário ou usar credenciais SMTP diretamente.

## 1. Criar um projeto no Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie ou selecione um projeto.
3. Ative a **Gmail API**.
4. Configure a tela de consentimento OAuth.
5. Crie credenciais do tipo **OAuth Client ID**.
6. Escolha o tipo de aplicação:
   - Aplicação web
   - Aplicação desktop
   - Serviço no servidor

## 2. Definir os escopos necessários

Use somente as permissões indispensáveis.

### Ler emails

```text
https://www.googleapis.com/auth/gmail.readonly
