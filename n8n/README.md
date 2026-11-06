# n8n — Fase 1 (WhatsApp inbound)

Dois workflows prontos para importar (`workflows/`):

| Workflow | O que faz |
|---|---|
| **01 - WhatsApp entrada** | Recebe a mensagem, ignora repetida e quem pediu para sair, registra "SAIR", classifica com IA (JSON validado), gera rascunho e grava na aba **Aprovacao** |
| **02 - Enviar aprovadas** | A cada 2 min, envia só as linhas com `status = APROVADA` e `aprovado_por` preenchido. Bloqueia oposição, janela de 24h vencida e reenvio. **Começa em `dry_run: true` (não envia nada).** |

## Passo a passo

1. **Planilha Google** com 2 abas e estes cabeçalhos na linha 1 (exatamente assim):
   - `Aprovacao`: `chave | telefone | nome | mensagem_cliente | recebido_em | intencao | confianca | rascunho | proximo_passo | status | motivo | aprovado_por | enviado_em | ref_envio | criado_em`
   - `Supressao`: `chave | canal | motivo | registrado_em`
2. **Importar** os 2 JSON no n8n (menu Workflows → Import from file).
3. **Credenciais** no n8n:
   - *Google Sheets OAuth2*: selecione em todos os nós de planilha.
   - *Header Auth* "Anthropic": nome `x-api-key`, valor = sua chave da API → nos nós "Claude P1" e "Claude P2".
   - *Header Auth* "WhatsApp": nome `Authorization`, valor `Bearer SEU_TOKEN_PERMANENTE` → no nó "WhatsApp enviar".
4. **Editar os nós `Config`** (ID da planilha, link de indicação, `phone_number_id`) e o token em "Verificar token Meta".
5. **Meta**: configure o webhook para `https://SEU-N8N/webhook/whatsapp`, com o mesmo token de verificação, e assine o campo `messages`.
6. Ative o 01. Mande um "oi" do seu celular para o número → deve aparecer a linha na aba Aprovacao.
7. **Rotina de aprovação**: edite o `rascunho` se quiser, escreva seu nome em `aprovado_por` e mude o `status` para `APROVADA`.
8. Ative o 02 em `dry_run: true` → status vira `SIMULADA`. Só quando confiar, mude para `false`.

## Status na aba Aprovacao
`RASCUNHO` → (você) `APROVADA` → `ENVIADA` / `SIMULADA` / `BLOQUEADA` / `JANELA_EXPIRADA` / `FALHA`.
`FILA_HUMANA` = a IA falhou ou ficou em dúvida: responda você mesmo pelo WhatsApp.

## Testado vs. não testado
- **Testado aqui:** o código de todos os nós Code (15 testes em `tests/`, cobrindo duplicidade, SAIR, falha da IA, sem aprovação, dry-run, janela de 24h, reenvio e falha de envio) e a integridade das conexões.
- **NÃO testado:** a importação em um n8n real, os nós Google Sheets/HTTP e as chamadas reais à Meta e à Anthropic. Faça o passo 6 e me mande o print/erro se algo falhar.
- A memória contra duplicidade (`staticData`) só funciona com o workflow **ativo** (não em "Test workflow").

## Mudar código
Edite `src/*.js`, rode `node --test n8n/tests/nos.test.mjs` e `python3 n8n/build.py`, e reimporte.
