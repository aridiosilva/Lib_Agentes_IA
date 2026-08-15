# Lib_Agentes_IA_Elaborados

Uma biblioteca de **agentes de IA elaborados** e prontos para usar, cada um especializado em realizar tarefas específicas indicadas em seus nomes.

## 📋 Sobre

Esta biblioteca contém agentes de IA pré-configurados com toda a estrutura necessária para funcionamento imediato. Cada agente foi projetado com:

- **Identidade clara** — papéis, personalidades e comportamentos definidos
- **Propósito específico** — tarefas bem delimitadas e nomes descritivos
- **Configuração completa** — ferramentas, regras, memória e contexto prontos
- **Múltiplos formatos** — compatível com ChatGPT, Gemini, Claude e outras plataformas

## 📁 Estrutura de cada agente

Cada pasta de agente contém:

```
nome-do-agente/
├── agent.json              # Configuração completa do agente (estrutura My Agent Studio)
├── README.md               # Descrição e modo de uso
└── prompts/
    ├── chatgpt.md          # Prompt otimizado para ChatGPT
    ├── gemini.md           # Prompt otimizado para Google Gemini
    └── claude.md           # Prompt otimizado para Claude (Anthropic)
```

### Arquivo `agent.json`
Contém a configuração editável do agente no formato da [My Agent Studio](https://github.com/aridiosilva/my-agent-studio):
- Identity (identidade, avatar, tom)
- Soul (missão, essência, filosofia)
- Personality (traços, behavior sliders)
- Tools (ferramentas disponíveis)
- Knowledge (base de conhecimento)
- Memory (estratégia de memória)
- Rules (guard rails)

Pode ser **importado diretamente** na My Agent Studio para edição visual.

### Arquivos `*.md` (Prompts)
Prompts prontos para copiar e colar diretamente nas plataformas:

- **chatgpt.md** — Formatado para ChatGPT 4, 4o e versões anteriores
- **gemini.md** — Otimizado para Google Gemini (Gemini 2.0, 1.5, etc)
- **claude.md** — Estruturado para Claude (3.5 Sonnet, Opus, etc)

Cada prompt inclui:
- System prompt (configuração do modelo)
- Context e comportamento esperado
- Ferramentas e instruções de operação
- Guardrails e limites de segurança

## 🚀 Como usar

### Opção 1: Na My Agent Studio (Recomendado)
1. Acesse [My Agent Studio](https://aridiosilva.github.io/my-agent-studio/)
2. Clique em **Importar agente**
3. Selecione o arquivo `agent.json` do agente desejado
4. O agente carrega com toda a configuração visual
5. Edite, teste e exporte conforme necessário

### Opção 2: No ChatGPT, Gemini ou Claude
1. Abra o chat da plataforma escolhida
2. Copie o conteúdo do arquivo `prompts/*.md` correspondente
3. Cole como mensagem inicial
4. A IA assume o papel do agente imediatamente
5. Prossiga com suas instruções

### Opção 3: Em seu próprio harness
1. Leia o `agent.json` com seu parser
2. Extraia as ferramentas, regras e contexto
3. Construa o system prompt com os dados do agente
4. Use em qualquer LLM via API (OpenAI, Anthropic, Google, etc)

## 📚 Agentes disponíveis

A biblioteca contém agentes para diversas categorias:

- **Análise e Pesquisa** — Analistas de dados, pesquisadores, revisores
- **Criação de Conteúdo** — Redatores, copywriters, roteiristas, editores
- **Desenvolvimento** — Code reviewers, arquitetos, debuggers
- **Negócios** — Consultores, gerentes, especialistas em marketing
- **Suporte e Educação** — Tutores, especialistas em atendimento
- **Criatividade** — Designers, idealizadores, brainstormers
- *(e muito mais)*

Veja a lista completa em [AGENTS.md](./AGENTS.md).

## 🔧 Modificar um agente

### Usando My Agent Studio
1. Importe o `agent.json`
2. Navegue pelas 9 etapas: Soul, Propósito, Personalidade, Comportamento, Ferramentas, Conhecimento, Memória, Guardrails, Exportação
3. Edite visualmente
4. Exporte novamente como `agent.json`
5. Submeta um PR com as mudanças

### Editando o JSON diretamente
O `agent.json` segue o esquema da My Agent Studio. Estrutura básica:

```json
{
  "kind": "my-agent-studio/agent",
  "version": 1,
  "agent": {
    "name": "Nome do Agente",
    "purpose": "Descrever o propósito",
    "soul": { ... },
    "personality": { ... },
    "tools": [ ... ],
    "knowledge": [ ... ],
    "memory": { ... },
    "rules": [ ... ]
  }
}
```

## 💡 Boas práticas

1. **Comece pelo agente mais próximo** do que você precisa e customize
2. **Teste em múltiplas plataformas** — o agente funciona em todas, mas cada LLM tem sutilezas
3. **Itere rapidamente** — use a My Agent Studio para prototipagem visual, depois versione
4. **Versionamento** — guarde `agent.json` com versão (v1, v2, etc) em seu projeto
5. **Exportação** — sempre exporte tanto `agent.json` quanto o markdown quando salvar uma versão

## 🤝 Contribuindo

Quer adicionar um novo agente ou melhorar os existentes?

1. Fork do repositório
2. Crie uma branch: `git checkout -b agente/novo-agente`
3. Adicione a pasta com `agent.json` e os três prompts (`chatgpt.md`, `gemini.md`, `claude.md`)
4. Atualize [AGENTS.md](./AGENTS.md) com a descrição
5. Submeta um Pull Request

### Checklist para novo agente
- [ ] `agent.json` válido e testado na My Agent Studio
- [ ] Três prompts (chatgpt.md, gemini.md, claude.md)
- [ ] Pasta com nome claro indicando a tarefa
- [ ] README.md na pasta explicando o agente
- [ ] Testado em pelo menos uma plataforma (ChatGPT, Gemini ou Claude)
- [ ] Entrada adicionada em AGENTS.md

## 📖 Documentação

- [My Agent Studio](https://github.com/aridiosilva/my-agent-studio) — Ferramenta de criação visual
- [AGENTS.md](./AGENTS.md) — Catálogo completo de agentes
- [SCHEMA.md](./SCHEMA.md) — Especificação do formato `agent.json`
- [PROMPTS.md](./PROMPTS.md) — Guia de customização de prompts

## 📝 Licença

Esta biblioteca é distribuída sob a licença [MIT](./LICENSE).

Os agentes podem ser usados, modificados e distribuídos livremente. Atribua crédito quando usar em produção.

## 🔗 Links úteis

- **My Agent Studio**: https://aridiosilva.github.io/my-agent-studio/
- **Repositório**: https://github.com/aridiosilva/Lib_Agentes_IA_Elaborados
- **Issues e Discussões**: https://github.com/aridiosilva/Lib_Agentes_IA_Elaborados/issues

## 🎯 Roadmap

- [ ] 50+ agentes pré-configurados (em andamento)
- [ ] Suporte a Claude Projects
- [ ] CLI para gerar agentes (`npx agente-ia novo-agente`)
- [ ] Galeria interativa no site
- [ ] Exemplos de integração com APIs (OpenAI, Anthropic, Google)
- [ ] Sistema de versionamento automático

---

**Criado com ❤️ para makers, desenvolvedores e empresas que querem agentes de IA prontos para trabalhar.**