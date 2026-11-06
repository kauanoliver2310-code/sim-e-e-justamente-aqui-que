# 03 — Arquitetura revisada

## Decisão principal: inbound primeiro

```
            CANAL PRINCIPAL (barato, sem risco de opt-in)
 Vídeo curto ──► Cliente chama no WhatsApp ──► n8n (webhook Cloud API)
 (Reels/TikTok/Shorts)        │                     │
                              │          ┌──────────┴───────────┐
                              │          ▼                      ▼
                              │   Classificação IA        Consulta CNPJ
                              │   (intenção + ICP,        (BrasilAPI + cache,
                              │    JSON validado)          regra determinística)
                              │          └──────────┬───────────┘
                              │                     ▼
                              │          Rascunho de resposta + link certo
                              │                     ▼
                              │          APROVAÇÃO DO KAUAN (1 toque)
                              │                     ▼
                              └──────────── Resposta na janela de 24h (grátis)
                                                    ▼
                                           CRM (Sheets → Postgres) + follow-up

            CANAL SECUNDÁRIO (controlado, fase 2)
 Dados Abertos CNPJ (filtro CNAE + município) ──► Compliance ──► E-mail com
 opção de descadastro (≤100/dia) ──► resposta ──► entra no fluxo acima
```

## Componentes escolhidos

| Camada | Escolha | Alternativa | Por quê |
|---|---|---|---|
| Orquestração | **n8n Community, auto-hospedado** | n8n Cloud | Custo fixo baixo; o Kauan já planeja usar. Cloud se não quiser cuidar de servidor. |
| Regras e cálculos | **Código Python testado** (este repositório) | Nós Code do n8n em JS | Testável e versionado. Na fase 1, as regras podem ser portadas para nós Code. |
| IA principal | **Claude Haiku 5.5** | Claude Sonnet 5.5 (casos difíceis) ou Gemini Flash (após confirmar preço) | Preço oficial verificado (US$ 0,10/0,50), saída estruturada, nó nativo no n8n. *Aviso: sou o Claude; o ChatGPT deve validar com 50 mensagens reais.* |
| Cadastro | **BrasilAPI + cache** | Dados Abertos CNPJ (download local) | Grátis; o cache evita depender da disponibilidade. |
| Compliance fase 2 | **Lista Suja (arquivo semestral)** + certidão IBAMA manual | API paga de terceiros | Grátis; volume baixo não justifica API paga. |
| Banco | **Google Sheets** (fase 1) → **PostgreSQL** (fase 2) | Supabase (Postgres gerenciado) | Sheets valida o processo; Postgres quando houver mais de ~500 leads ou necessidade de auditoria LGPD. |
| WhatsApp | **Cloud API oficial da Meta** | — | Evolution API descartada (risco de banimento e violação dos termos). |
| E-mail | **Resend grátis** | Plano pago | 100/dia basta para a fase 2. |
| Agenda | **Google Calendar** ou **link do Cal.com** | — | Para vender maquininha, link de agenda resolve; reunião nem sempre é necessária. |

## Onde a IA entra (e onde NÃO entra)

| Tarefa | Quem faz |
|---|---|
| Validar CNPJ, deduplicar, checar situação cadastral | **Código** |
| Decidir APTO/PENDENTE/restrição | **Código** (`compliance.py`) |
| Calcular custo, limite de envio, idempotência | **Código** |
| Entender a mensagem do cliente (intenção, dúvida, oposição) | **IA**, com saída JSON validada |
| Redigir rascunho de resposta / e-mail | **IA**, sempre com aprovação humana |
| Aprovar envio, confirmar restrição, fechar venda | **Kauan** |

## Modelo de dados (PostgreSQL, fase 2)

Ver `sql/schema.sql`. Tabelas: `leads`, `consultas_fonte` (evidência com data da base),
`pareceres_compliance`, `mensagens` (chave de idempotência única), `supressao` (hash de contato),
`eventos_lgpd`, `agendamentos`, `rascunhos_vs_aprovados`.

## Contrato de integração n8n ↔ código

| Endpoint (fase 2, serviço Python) | Entrada | Saída |
|---|---|---|
| `POST /cnpj/validar` | `{cnpj}` | `{valido, normalizado}` |
| `POST /compliance/avaliar` | `{cnpj, resultados[]}` | `{parecer, confianca, motivos, evidencias, fontes_pendentes}` |
| `POST /classificacao/validar` | `{texto_saida_llm}` | `{status, intencao, icp, confianca}` |
| `POST /mensagens/rascunho` | `{cnpj, canal, destino, texto, campanha, etapa}` | `{chave}` ou 409 se duplicada |
| `POST /lgpd/oposicao` | `{cnpj?, telefone?, email?, canal}` | 204 |

Na fase 1 não existe serviço: n8n + Sheets + nós Code com as mesmas regras.
